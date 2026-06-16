"""Deterministic analysis over the cleaned, credible company set.

Builds the `Space` aggregate root: market-shape stats, per-metric rankings, the
seed's position, and the data-confidence notes. No AI here — that's layered on
afterwards by the enricher.
"""

from collections import Counter
from datetime import date
from statistics import median

from app.models.domain import Company, Space

_CURRENT_YEAR = date.today().year


def _field(seed: Company, peers: list[Company]) -> list[Company]:
    """The whole space (seed + credible peers) — ranks like '#4 of 9' include the seed."""
    return [seed, *peers]


def _rank(seed_value, values: list[float], *, higher_is_better: bool) -> tuple[int | None, int]:
    """Rank of the seed among companies that report this metric. Returns (rank, of)."""
    if seed_value is None:
        return None, len(values)
    ordered = sorted(values, reverse=higher_is_better)
    return ordered.index(seed_value) + 1, len(ordered)


def _maturity_label(year: int | None) -> str:
    if year is None:
        return "mixed maturity"
    if year <= 2013:
        return "established market"
    if year <= 2018:
        return "maturing market"
    return "emerging market"


def _intensity_label(num_peers: int) -> str:
    if num_peers < 8:
        return "niche"
    if num_peers <= 20:
        return "moderately competitive"
    return "crowded"


# Public-market / acquisition outcomes — the clearest incumbent signal.
_INCUMBENT_STAGE = ("post-ipo", "ipo", "merger", "acquired", "lbo")
# Late-stage venture (Series C → pre-IPO) — the "established player" band.
_ESTABLISHED_STAGE = ("series c", "series d", "series e", "series f", "series g", "pre-ipo", "growth equity")


def classify_tier(c: Company) -> str:
    """Two cohorts, per the agreed rubric:

    Incumbent  — the entrenched market leader: public (IPO) or acquired, the
                 largest headcounts (>=1k), or an old & sizeable company that
                 never took venture rounds (self-sustaining / bootstrapped).
    Established — the younger, scaling challenger: late-stage venture capital
                 (Series C through pre-IPO), mid-aged (~4-10y), 100-500 staff.
    """
    stage = (c.funding_stage or "").lower()
    age = _CURRENT_YEAR - c.founded_year if c.founded_year else None
    emp = c.employees if (c.employees is not None and c.employees_reliable) else None

    if any(m in stage for m in _INCUMBENT_STAGE):
        return "incumbent"  # public or acquired
    if emp is not None and emp >= 1000:
        return "incumbent"  # incumbent-scale headcount
    if any(m in stage for m in _ESTABLISHED_STAGE):
        return "established"  # late-stage venture challenger
    # Old, sizeable, and never raised named VC → self-sustaining / bootstrapped.
    if age is not None and age >= 15 and emp is not None and emp >= 500 and "series" not in stage and "seed" not in stage:
        return "incumbent"
    return "established"


def _archetype(funding_rank, funding_of, growth_rank, growth_of, founded_year, median_year) -> str:
    if funding_rank and founded_year and median_year and funding_rank <= max(funding_of // 2, 1) and founded_year <= median_year:
        return "Established player"
    if growth_rank and growth_rank <= max(growth_of // 3, 1):
        return "Fast grower"
    if funding_rank and funding_rank > 2 * funding_of // 3:
        return "Emerging challenger"
    return "Mid-market player"


def build_space(
    seed: Company,
    peers: list[Company],
    *,
    all_competitors: list[Company],
    quarantined_count: int,
    cache_hit: bool,
    count: int,
) -> Space:
    field = _field(seed, peers)
    for c in field:
        c.market_tier = classify_tier(c)

    # Relevance breakdown across every returned competitor (not just credible peers).
    # Tiers are set to the API's real similarity range (it floors ~0.58-0.60 and
    # rarely exceeds ~0.78): the <=0.60 block is the inclusion-floor padding.
    direct = sum(1 for c in all_competitors if c.similarity >= 0.70)
    adjacent = sum(1 for c in all_competitors if 0.60 < c.similarity < 0.70)
    peripheral = sum(1 for c in all_competitors if c.similarity <= 0.60)

    # Per-metric universes (only companies that actually report the metric).
    fundings = [c.total_funding_m for c in field if c.total_funding_m is not None]
    headcounts = [c.employees for c in field if c.employees is not None and c.employees_reliable]
    growths = [c.growth_12m for c in field if c.growth_12m is not None]
    years = [c.founded_year for c in field if c.founded_year is not None]

    median_year = int(median(years)) if years else None

    funding_rank, funding_of = _rank(seed.total_funding_m, fundings, higher_is_better=True)
    headcount_rank, headcount_of = _rank(
        seed.employees if seed.employees_reliable else None, headcounts, higher_is_better=True
    )
    growth_rank, growth_of = _rank(seed.growth_12m, growths, higher_is_better=True)
    maturity_rank, maturity_of = _rank(seed.founded_year, years, higher_is_better=False)  # older = more established

    # Themes = the most common industries across the field ("what defines this space").
    industry_counts = Counter(tag for c in field for tag in c.industries)
    themes = [label for label, _ in industry_counts.most_common(6)]
    top_industry = themes[0] if themes else "Software"

    capital_ranking = [
        c.domain for c in sorted(
            (c for c in field if c.total_funding_m is not None),
            key=lambda c: c.total_funding_m,
            reverse=True,
        ) if c.domain
    ]
    closest = [
        c.domain for c in sorted(peers, key=lambda c: c.similarity, reverse=True)[:6] if c.domain
    ]

    unreliable = sum(1 for c in field if c.employees is not None and not c.employees_reliable)
    notes = [
        "Geography is derived from the structured locations array, not the buggy summary string.",
        "Descriptions are cleaned of internal notes and keyword spam before display.",
    ]
    if unreliable:
        notes.insert(0, f"{unreliable} headcount figure(s) looked unreliable and were down-weighted.")
    if quarantined_count:
        notes.insert(0, f"{quarantined_count} record(s) quarantined for mismatched identity.")

    return Space(
        seed=seed,
        companies=peers,
        name=f"{top_industry} landscape",
        num_credible_peers=len(peers),
        median_founded_year=median_year,
        maturity_label=_maturity_label(median_year),
        total_capital_m=round(sum(fundings), 2),
        total_headcount=sum(headcounts),
        intensity_label=_intensity_label(len(peers)),
        relevance_direct=direct,
        relevance_adjacent=adjacent,
        relevance_peripheral=peripheral,
        themes=themes,
        capital_ranking=capital_ranking,
        archetype=_archetype(funding_rank, funding_of, growth_rank, growth_of, seed.founded_year, median_year),
        funding_rank=funding_rank,
        funding_of=funding_of,
        headcount_rank=headcount_rank,
        headcount_of=headcount_of,
        growth_rank=growth_rank,
        growth_of=growth_of,
        maturity_rank=maturity_rank,
        maturity_of=maturity_of,
        closest_comparators=closest,
        unreliable_headcount_count=unreliable,
        quarantined_count=quarantined_count,
        notes=notes,
        cache_hit=cache_hit,
        count=count,
    )
