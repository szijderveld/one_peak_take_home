"""Boundary DTOs that mirror the Pulse API response shape.

These are intentionally permissive: every field is optional and unknown keys are
ignored, so missing / null / unexpected data never crashes ingestion. They are
*not* domain entities — the pipeline cleans them into `Company` / `Space`.
"""

from pydantic import BaseModel, ConfigDict


class RawRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str | None = None
    domain: str | None = None
    description: str | None = None
    similarity: float | None = None
    industries: str | None = None
    employees: float | None = None
    employee_12_months_growth_relative: float | None = None
    employee_locations_array: list[dict] | None = None
    employee_geography: str | None = None
    founded_date: str | None = None
    hq_locations: str | None = None
    funding_stage: str | None = None
    total_funding_usd_million: float | None = None
    last_round_funding_usd_million: float | None = None
    last_round_funding_date: str | None = None
    tier: str | None = None
    gr_business_models: str | None = None
    sources: list[str] | None = None


class PulseResponse(BaseModel):
    """The API envelope. Trust `success`, not just the HTTP status."""

    model_config = ConfigDict(extra="ignore")

    success: bool = False
    count: int = 0
    cache_hit: bool = False
    results: list[RawRecord] = []
    error: str | None = None
    message: str | None = None
