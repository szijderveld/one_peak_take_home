"""Field-by-field cleaning of the messy Pulse data.

Each function targets one problem called out in the Data Quality & Field
Reference doc. `clean_record` composes them into a `Company`. Functions are pure
so they're trivial to unit-test (see tests/test_cleaning.py).
"""

import re

from app.models.domain import Company, GeoShare
from app.models.raw import RawRecord

_TLDS = (".com", ".io", ".co", ".ai", ".app", ".dev", ".net", ".org")

# Machine-appended boilerplate / leaked annotations to cut from descriptions.
_DESC_CUTS = [
    re.compile(r"\bKeywords:\s", re.I),
    re.compile(r"\bFounded\s+\d+\s+years?\s+ago\b", re.I),
    re.compile(r"\bIncome streams:\s", re.I),
]
_INTERNAL_NOTE = re.compile(
    r"classified internally|not for OP\b|internal note|\bdead\b[^.]{0,40}analyst",
    re.I,
)
_DESC_HEADCOUNT = re.compile(r"([\d][\d,]*(?:\.\d+)?)\s+employees", re.I)

_COUNTRY_ALIASES = {
    "usa": "United States",
    "us": "United States",
    "u.s.": "United States",
    "united states of america": "United States",
    "uk": "United Kingdom",
    "u.k.": "United Kingdom",
    "hong kong s.a.r.": "Hong Kong",
}


def clean_domain(domain: str | None) -> str | None:
    """Lowercase, strip scheme/www/path. The reliable identity / join key."""
    if not domain:
        return None
    d = domain.strip().lower()
    d = re.sub(r"^https?://", "", d)
    d = d.removeprefix("www.")
    d = d.split("/")[0].strip()
    return d or None


def clean_name(name: str | None, domain: str | None) -> str:
    """Human label. Strip ` | …` decorations and domain-as-name TLDs; gently
    title-case all-lowercase brands. Falls back to the domain stem."""
    label = (name or "").split(" | ")[0].strip().strip("\"'").replace("_", " ")
    if not label:
        label = (domain or "").split(".")[0]
    # "CloudRunner.IO" / "pijajo.com" → drop a trailing TLD-as-suffix
    low = label.lower()
    for tld in _TLDS:
        if low.endswith(tld) and " " not in label:
            label = label[: -len(tld)]
            break
    if label and label == label.lower():  # deliberate-lowercase unknown → title it
        label = label.title()
    return label or (domain or "company")


def clean_description(description: str | None) -> str | None:
    """Strip Keywords/boilerplate/internal-notes, collapse whitespace, and
    truncate to a ~2-sentence preview. Never shown raw."""
    if not description:
        return None
    text = description
    # Drop everything from the first machine-boilerplate marker onward.
    cut = min((m.start() for p in _DESC_CUTS if (m := p.search(text))), default=len(text))
    text = text[:cut]
    # Remove a leaked internal annotation (and anything after it).
    if note := _INTERNAL_NOTE.search(text):
        text = text[: note.start()]
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return None
    # First two sentences, hard-capped for previews.
    parts = re.split(r"(?<=[.!?])\s+", text)
    preview = " ".join(parts[:2]).strip()
    if len(preview) > 280:
        preview = preview[:279].rstrip() + "…"
    return preview


def _desc_headcount(description: str | None) -> int | None:
    if not description:
        return None
    m = _DESC_HEADCOUNT.search(description)
    if not m:
        return None
    n = int(float(m.group(1).replace(",", "")))
    return n if 1 < n < 2_000_000 else None


def clean_employees(
    employees: float | None, growth: float | None, description: str | None
) -> tuple[int | None, bool]:
    """Return (headcount, reliable). Treats the `1` sentinel as unknown,
    prefers the narrative figure when the structured count contradicts it, and
    down-weights implausible tiny-count + extreme-decline snapshots."""
    if employees is None:
        return None, True
    e = int(round(employees))
    desc_e = _desc_headcount(description)
    if e <= 1:  # the "1" (or 0) sentinel almost always means unknown
        return desc_e, False
    if desc_e and desc_e > 5 * e:  # structured count flatly contradicts the text
        return desc_e, False
    if growth is not None and growth < -50 and e < 50:  # artefact, not a real collapse
        return e, False
    return e, True


def clean_growth(growth: float | None) -> float | None:
    return round(growth, 1) if growth is not None else None


def clean_founded(founded_date: str | None) -> tuple[int | None, str]:
    """Return (year, precision). A `-01-01` date is year-precision filler."""
    if not founded_date:
        return None, "unknown"
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", founded_date.strip())
    if not m:
        return None, "unknown"
    year, month, day = int(m[1]), m[2], m[3]
    precision = "year" if (month, day) == ("01", "01") else "day"
    return year, precision


def _normalise_country(country: str) -> str:
    c = country.strip()
    return _COUNTRY_ALIASES.get(c.lower(), c)


def clean_hq(hq_locations: str | None) -> tuple[str | None, str | None]:
    """Split on the last comma → (city, country). A lone token is the country."""
    if not hq_locations:
        return None, None
    parts = [p.strip() for p in hq_locations.split(",") if p.strip()]
    if not parts:
        return None, None
    if len(parts) == 1:
        return None, _normalise_country(parts[0])
    return ", ".join(parts[:-1]), _normalise_country(parts[-1])


def split_tags(value: str | None) -> list[str]:
    """Comma-split THEN strip (spacing is inconsistent); dedupe, preserve order."""
    if not value:
        return []
    seen: list[str] = []
    for tok in value.split(","):
        t = tok.strip()
        if t and t not in seen:
            seen.append(t)
    return seen


def clean_funding(value: float | None) -> float | None:
    """Round; treat 0.0 as unknown (ambiguous per the doc) so it doesn't skew stats."""
    if value is None or value == 0.0:
        return None
    return round(value, 2)


def normalise_stage(
    stage: str | None, tier: str | None, is_seed: bool
) -> str | None:
    """Read defensively; the seed row carries `tier` instead of `funding_stage`."""
    value = stage or (tier if is_seed else None)
    if not value:
        return None
    value = value.strip()
    return {"Post-IPO Financing": "Post-IPO", "Series Unknown": "Series (undisclosed)"}.get(
        value, value
    )


def parse_geography(arr: list[dict] | None) -> list[GeoShare]:
    """The trustworthy geographic source — derived from the array, never the
    buggy `employee_geography` string. Sorted desc, `Other` pushed last."""
    if not arr:
        return []
    shares = [
        GeoShare(
            country=item.get("country", "Unknown"),
            percent=float(item.get("percent") or 0.0),
            confidence=item.get("confidence"),
        )
        for item in arr
        if item.get("percent") is not None
    ]
    return sorted(shares, key=lambda g: (g.country == "Other", -g.percent))


def check_identity(name: str | None, domain: str | None, description: str | None) -> bool:
    """True unless the description never mentions the company at all — the
    signature of a wrong-company record (e.g. a 'payleven' row describing SumUp).

    Compares alphanumeric-collapsed strings so 'Doc Field' matches 'docfield'.
    We scan the whole description (not just the head) to avoid false positives:
    a genuine mismatch won't name the brand anywhere; a legitimate record almost
    always does, even if not in the first sentence."""
    if not description or len(description.strip()) < 220:
        return True  # nothing, or just a terse tagline that needn't repeat the name
    norm = lambda s: re.sub(r"[^a-z0-9]", "", (s or "").lower())
    body = norm(description)
    keys = [k for k in (norm(name), norm((domain or "").split(".")[0])) if len(k) >= 4]
    if not keys:
        return True  # name/domain too short to verify reliably
    return any(k in body for k in keys)  # else: a full profile must name the company


def clean_record(raw: RawRecord, is_seed: bool) -> Company:
    """Compose the field cleaners into a single cleaned `Company`."""
    domain = clean_domain(raw.domain)
    employees, employees_reliable = clean_employees(
        raw.employees, raw.employee_12_months_growth_relative, raw.description
    )
    founded_year, founded_precision = clean_founded(raw.founded_date)
    hq_city, hq_country = clean_hq(raw.hq_locations)
    return Company(
        domain=domain,
        display_name=clean_name(raw.name, domain),
        is_seed=is_seed,
        identity_ok=check_identity(raw.name, domain, raw.description),
        similarity=raw.similarity or 0.0,
        description=clean_description(raw.description),
        employees=employees,
        employees_reliable=employees_reliable,
        growth_12m=clean_growth(raw.employee_12_months_growth_relative),
        founded_year=founded_year,
        founded_precision=founded_precision,
        hq_city=hq_city,
        hq_country=hq_country,
        industries=split_tags(raw.industries),
        business_models=split_tags(raw.gr_business_models),
        funding_stage=normalise_stage(raw.funding_stage, raw.tier, is_seed),
        total_funding_m=clean_funding(raw.total_funding_usd_million),
        last_round_m=clean_funding(raw.last_round_funding_usd_million),
        last_round_date=raw.last_round_funding_date,
        geography=parse_geography(raw.employee_locations_array),
    )
