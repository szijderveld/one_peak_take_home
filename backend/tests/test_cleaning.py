"""Cleaning unit tests, anchored to the Data Quality & Field Reference doc's
worked examples (PayPal headcount, the geography bug, the polluted
payleven_brazil record, year-precision dates, inconsistent tag spacing)."""

from app.models.raw import RawRecord
from app.pipeline import cleaning as c


def test_domain_is_lowercased_and_stripped():
    assert c.clean_domain("https://www.PandaDoc.com/pricing") == "pandadoc.com"
    assert c.clean_domain(None) is None


def test_name_handles_lowercase_tld_and_decorations():
    assert c.clean_name("pandadoc", "pandadoc.com") == "Pandadoc"
    assert c.clean_name("CloudRunner.IO", "cloudrunner.io") == "CloudRunner"
    assert c.clean_name("Shift4 | Lighthouse Network", "shift4.com") == "Shift4"
    assert c.clean_name(None, "groundcover.com") == "Groundcover"


def test_description_strips_keywords_and_boilerplate_and_truncates():
    raw = (
        "Doc Field provides a document and contract management platform. "
        "It enables real-time collaboration and e-signing. "
        "Founded 6 years ago with 14.0 employees. Serves B2B,Education. "
        "Income streams: Subscription. Keywords: contracts, docs, e-sign"
    )
    out = c.clean_description(raw)
    assert "Founded 6 years ago" not in out
    assert "Keywords" not in out
    assert "Income streams" not in out
    assert out.startswith("Doc Field provides")


def test_description_removes_leaked_internal_note():
    raw = "SumUp is a mobile payments company. This was classified internally as dead — JS."
    out = c.clean_description(raw)
    assert "classified internally" not in out
    assert out.startswith("SumUp is a mobile payments company")


def test_employees_paypal_prefers_narrative_over_implausible_count():
    # Structured 17 vs "35170.0 employees" in the text → trust the narrative, flag it.
    emp, reliable = c.clean_employees(17.0, -0.95, "... Founded 27 years ago with 35170.0 employees ...")
    assert emp == 35170
    assert reliable is False


def test_employees_one_is_unknown():
    assert c.clean_employees(1.0, None, None) == (None, False)


def test_employees_tiny_count_with_extreme_decline_is_downweighted():
    emp, reliable = c.clean_employees(17.0, -95.0, "iZettle is a payments company.")
    assert emp == 17 and reliable is False


def test_employees_normal_is_reliable():
    assert c.clean_employees(851.0, 12.0, "GoCardless handles bank payments.") == (851, True)


def test_founded_year_precision():
    assert c.clean_founded("2013-01-01") == (2013, "year")  # filler day → year precision
    assert c.clean_founded("2015-03-12") == (2015, "day")
    assert c.clean_founded(None) == (None, "unknown")


def test_hq_split_on_last_comma():
    assert c.clean_hq("London, United Kingdom") == ("London", "United Kingdom")
    assert c.clean_hq("United States") == (None, "United States")
    assert c.clean_hq("Stockholms kommun, Sweden") == ("Stockholms kommun", "Sweden")


def test_tags_split_then_strip_inconsistent_spacing():
    assert c.split_tags("Analytics,Database,Enterprise Software, Software") == [
        "Analytics",
        "Database",
        "Enterprise Software",
        "Software",
    ]
    assert c.split_tags(None) == []


def test_funding_rounds_and_treats_zero_as_unknown():
    assert c.clean_funding(2.6500000000000004) == 2.65
    assert c.clean_funding(0.0) is None
    assert c.clean_funding(None) is None


def test_stage_uses_tier_for_seed():
    assert c.normalise_stage(None, "Seed", is_seed=True) == "Seed"
    assert c.normalise_stage("Post-IPO Financing", None, is_seed=False) == "Post-IPO"
    assert c.normalise_stage(None, None, is_seed=False) is None


def test_geography_derived_from_array_other_last():
    arr = [
        {"country": "United States", "percent": 0.22, "confidence": "High"},
        {"country": "Other", "percent": 0.60, "confidence": "High"},
        {"country": "Netherlands", "percent": 0.18, "confidence": "High"},
    ]
    geo = c.parse_geography(arr)
    assert [g.country for g in geo] == ["United States", "Netherlands", "Other"]


def test_identity_quarantine_on_wrong_company_description():
    # A *substantial* profile naming a different company than the record →
    # quarantined (the payleven_brazil row that actually describes SumUp).
    sumup = (
        "SumUp is a global financial technology company providing mobile "
        "point-of-sale solutions to small merchants. Founded in 2012, it offers "
        "card readers and a business account so any merchant can accept card "
        "payments quickly and affordably across Europe and beyond."
    )
    assert c.check_identity("payleven_brazil", "payleven.com", sumup) is False
    # 'Doc Field' text matches the 'docfield' domain once alphanumerics collapse.
    docfield = (
        "Doc Field provides a document and contract management platform that "
        "helps businesses streamline contract processes with real-time "
        "collaboration, e-signing and data extraction across many industries."
    )
    assert c.check_identity("Docfield", "docfield.com", docfield) is True


def test_identity_does_not_quarantine_terse_or_short_name():
    # A terse tagline needn't repeat the brand — not a mismatch.
    assert c.check_identity("BaseBear", "basebear.com", "Build online databases in minutes!") is True
    # Name/domain too short to verify reliably → never quarantine.
    generic = "We are a global, multi-disciplinary integration consultancy firm. " * 4
    assert c.check_identity("Eve", "eve.legal", generic) is True


def test_clean_record_end_to_end_seed():
    raw = RawRecord(
        name="pandadoc",
        domain="PandaDoc.com",
        description="Document automation software. Keywords: docs, e-sign",
        industries="Sales Software, SaaS",
        employees=891.0,
        total_funding_usd_million=66.929633,
        founded_date="2013-01-01",
        employee_12_months_growth_relative=10.58,
        tier="Seed",
        similarity=1.0,
        sources=["seed"],
    )
    company = c.clean_record(raw, is_seed=True)
    assert company.domain == "pandadoc.com"
    assert company.display_name == "Pandadoc"
    assert company.employees == 891 and company.employees_reliable
    assert company.total_funding_m == 66.93
    assert company.founded_year == 2013 and company.founded_precision == "year"
    assert company.industries == ["Sales Software", "SaaS"]
    assert company.funding_stage == "Seed"
    assert "Keywords" not in company.description
