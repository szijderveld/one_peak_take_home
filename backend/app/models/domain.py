"""The domain model — exactly two entities, `Company` and `Space`.

AI enrichment is expressed as properties *on* these models (e.g.
`Company.ai_summary`, `Space.summary`), populated in place by the enricher.
`GeoShare` is the single supporting value object (the talent-map needs
structured per-country shares).
"""

from pydantic import BaseModel, Field


class GeoShare(BaseModel):
    country: str
    percent: float  # 0..1
    confidence: str | None = None


class Company(BaseModel):
    """A cleaned company, plus its AI-enhanced properties."""

    # Identity — `domain` is the join key; `display_name` is the human label.
    domain: str | None = None
    display_name: str
    is_seed: bool = False
    identity_ok: bool = True  # False = description named a different company
    similarity: float = 0.0  # 0..1 relevance to the seed

    description: str | None = None  # cleaned, preview-length
    ai_blurb: str | None = None  # AI: one-line "what they do"
    ai_summary: str | None = None  # AI: richer narrative (populated for the seed)

    employees: int | None = None
    employees_reliable: bool = True  # False = down-weighted (e.g. the "1" sentinel)
    growth_12m: float | None = None  # % headcount change over 12 months

    founded_year: int | None = None
    founded_precision: str = "unknown"  # "year" | "day" | "unknown"

    hq_city: str | None = None
    hq_country: str | None = None

    industries: list[str] = Field(default_factory=list)
    business_models: list[str] = Field(default_factory=list)

    funding_stage: str | None = None  # normalised label
    total_funding_m: float | None = None
    last_round_m: float | None = None
    last_round_date: str | None = None

    market_tier: str = "established"  # "incumbent" | "established"
    geography: list[GeoShare] = Field(default_factory=list)


class Space(BaseModel):
    """The competitive landscape — the aggregate root returned by the API.

    Holds the peer companies, the space-level aggregates, where the seed sits,
    data-confidence notes, and the AI narrative properties.
    """

    seed: Company
    companies: list[Company] = Field(default_factory=list)  # credible peers (excl. seed)

    # --- Space-level aggregates ---
    name: str = ""
    num_credible_peers: int = 0
    median_founded_year: int | None = None
    maturity_label: str = ""  # e.g. "established market"
    total_capital_m: float = 0.0
    total_headcount: int = 0
    intensity_label: str = ""  # "niche" | "moderately competitive" | "crowded"
    # Relevance breakdown across ALL returned competitors (by similarity band).
    relevance_direct: int = 0  # >= 0.70
    relevance_adjacent: int = 0  # 0.50 - 0.69
    relevance_peripheral: int = 0  # < 0.50
    themes: list[str] = Field(default_factory=list)  # what defines this space
    capital_ranking: list[str] = Field(default_factory=list)  # domains, desc funding

    # --- Seed's position within the space (flat scalars; ranks are per-metric,
    # over the companies that actually report that metric) ---
    archetype: str = ""  # e.g. "Established player"
    funding_rank: int | None = None
    funding_of: int = 0
    headcount_rank: int | None = None
    headcount_of: int = 0
    growth_rank: int | None = None
    growth_of: int = 0
    maturity_rank: int | None = None
    maturity_of: int = 0
    closest_comparators: list[str] = Field(default_factory=list)  # peer domains, by similarity

    # --- Data confidence ---
    unreliable_headcount_count: int = 0
    quarantined_count: int = 0
    notes: list[str] = Field(default_factory=list)

    # --- AI-enhanced narrative properties ---
    summary: str | None = None  # THE SPACE narrative
    position_summary: str | None = None  # MARKET POSITION narrative
    incumbents_summary: str | None = None  # the incumbent tier, characterised
    established_summary: str | None = None  # the established / mid field, characterised

    # --- Meta ---
    cache_hit: bool = False
    count: int = 0  # raw record count from the API
    mode: str = "live"  # "live" | "demo"
