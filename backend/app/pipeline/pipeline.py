"""Orchestration: raw Pulse response → cleaned companies → analysed `Space`.

Splits the seed from competitors, cleans each record, drops the seed-bar
duplicates / sub-threshold rows, quarantines identity mismatches, then hands the
credible set to the analysis step. (AI enrichment is layered on top separately.)
"""

from app.config import Settings
from app.models.domain import Company, Space
from app.models.raw import PulseResponse, RawRecord
from app.pipeline import analysis, cleaning
from app.pipeline.pulse_client import get_competitors


async def build_landscape(domain: str, settings: Settings) -> Space:
    resp = await get_competitors(domain, settings)
    return build_from_response(resp, settings, fallback_domain=domain)


def build_from_response(resp: PulseResponse, settings: Settings, fallback_domain: str = "") -> Space:
    """The deterministic core: raw response → cleaned, analysed `Space` (no AI)."""
    seed_raw, competitor_raws = _split_seed(resp)
    seed = cleaning.clean_record(seed_raw, is_seed=True) if seed_raw else _fallback_seed(fallback_domain)
    cleaned = [cleaning.clean_record(r, is_seed=False) for r in competitor_raws]
    peers, quarantined, dropped = _select_peers(cleaned, seed, settings.similarity_threshold)

    return analysis.build_space(
        seed,
        peers,
        all_competitors=cleaned,
        quarantined_count=quarantined,
        dropped_unverifiable_count=dropped,
        cache_hit=resp.cache_hit,
        count=resp.count,
    )


def _split_seed(resp: PulseResponse) -> tuple[RawRecord | None, list[RawRecord]]:
    """The seed is the row with sources == ['seed'] (similarity 1.0)."""
    seed: RawRecord | None = None
    competitors: list[RawRecord] = []
    for rec in resp.results:
        if seed is None and (rec.sources == ["seed"] or rec.similarity == 1.0):
            seed = rec
        else:
            competitors.append(rec)
    return seed, competitors


def _select_peers(
    cleaned: list[Company], seed: Company, threshold: float
) -> tuple[list[Company], int, int]:
    """Credible peers: above the similarity bar, above the API's noise floor,
    identity-verified, with a verifiable headcount, de-duplicated by domain.
    Returns (peers, quarantined, dropped_unverifiable)."""
    candidates = [
        c for c in cleaned if c.similarity >= threshold and c.domain != seed.domain
    ]
    # The API pads results with a large block at its minimum similarity (84/100
    # sit at exactly 0.6 for pandadoc) — that's the inclusion baseline, not a
    # real match. Drop it when it dominates — but only if a real cluster remains
    # above it (otherwise the floor is all we have, so keep it).
    if candidates:
        floor = min(c.similarity for c in candidates)
        above = [c for c in candidates if c.similarity > floor]
        if len(above) >= 5 and sum(c.similarity == floor for c in candidates) > 0.4 * len(candidates):
            candidates = above

    by_domain: dict[str, Company] = {}
    quarantined = dropped = 0
    for c in candidates:
        if not c.identity_ok:
            quarantined += 1  # credible by score, but its profile describes someone else
            continue
        if c.employees is None and not c.employees_reliable:
            dropped += 1  # the "1" headcount sentinel with no narrative figure → an unverifiable entity
            continue
        key = c.domain or c.display_name.lower()
        if key not in by_domain or c.similarity > by_domain[key].similarity:
            by_domain[key] = c
    peers = sorted(by_domain.values(), key=lambda c: c.similarity, reverse=True)
    return peers, quarantined, dropped


def _fallback_seed(domain: str) -> Company:
    """If the API returns no seed row, build a minimal stand-in from the domain."""
    d = cleaning.clean_domain(domain)
    return Company(domain=d, display_name=cleaning.clean_name(None, d), is_seed=True, similarity=1.0)
