"""AI enrichment — fills the narrative properties on `Space` and the per-company
`ai_blurb` / `ai_summary`, in place.

Two calls run concurrently:
  • narrative (Sonnet) — evaluative, PE-analyst prose: company / space / position /
    established / emerging summaries, plus the space name and themes.
  • per-company (Haiku) — a one-line blurb and a short overlay summary for each
    displayed company, batched into ONE call.

The prompts deliberately push for *judgement*, not stat recital — the numbers are
already on the page. If a call fails (or no key) the fields stay null and the UI
falls back to the cleaned data.
"""

import asyncio

from anthropic import AsyncAnthropic
from pydantic import BaseModel

from app.config import Settings
from app.models.domain import Company, Space

# --- AI-boundary DTOs (not domain models) ---------------------------------


class _Narrative(BaseModel):
    space_name: str
    space_themes: list[str]
    company_summary: str
    space_summary: str
    position_summary: str
    established_summary: str
    emerging_summary: str


class _CompanyAI(BaseModel):
    domain: str
    blurb: str
    summary: str


class _Batch(BaseModel):
    items: list[_CompanyAI]


# --- public entry point ----------------------------------------------------


async def enrich(space: Space, settings: Settings) -> None:
    if not settings.ai_enabled:
        return
    client = AsyncAnthropic(api_key=settings.anthropic_api_key)
    narrative, batch = await asyncio.gather(
        _narrative(client, space, settings),
        _company_ai(client, space, settings),
        return_exceptions=True,
    )
    if isinstance(narrative, _Narrative):
        space.seed.ai_summary = narrative.company_summary
        space.summary = narrative.space_summary
        space.position_summary = narrative.position_summary
        space.established_summary = narrative.established_summary
        space.emerging_summary = narrative.emerging_summary
        if narrative.space_name.strip():
            space.name = narrative.space_name.strip()
        if narrative.space_themes:
            space.themes = narrative.space_themes
    if isinstance(batch, _Batch):
        by_domain = {b.domain: b for b in batch.items}
        for c in [space.seed, *space.companies]:
            item = by_domain.get(c.domain)
            if not item:
                continue
            c.ai_blurb = item.blurb
            if not c.is_seed:  # the seed's ai_summary is the richer company_summary
                c.ai_summary = item.summary


# --- narrative (Sonnet) ----------------------------------------------------

_NARRATIVE_SYSTEM = (
    "You are a market analyst briefing a private-equity investor who is seeing this "
    "company and its competitive landscape for the FIRST time. Write sharp, evaluative "
    "prose that helps them form a view — NOT a recap of the numbers (those already appear "
    "on the page; cite a figure only when it directly supports a judgement). Focus on "
    "market structure and dynamics, what genuinely differentiates the players, "
    "defensibility and moats, and the risks and opportunities an investor would weigh. "
    "Be objective but not opinionated, you are here to inform. No hype, no preamble, no markdown."
)


async def _narrative(client: AsyncAnthropic, space: Space, settings: Settings) -> _Narrative:
    resp = await client.messages.parse(
        model=settings.narrative_model,
        max_tokens=2000,
        system=_NARRATIVE_SYSTEM,
        messages=[{"role": "user", "content": _narrative_prompt(space)}],
        output_format=_Narrative,
    )
    return resp.parsed_output


def _line(c: Company, desc: bool = False) -> str:
    base = f"{c.display_name} (${c.total_funding_m}M, {c.employees} emp, {c.funding_stage or 'stage n/a'})"
    return f" - {base}" + (f" — {c.description}" if desc and c.description else "")


def _narrative_prompt(space: Space) -> str:
    s = space.seed
    leaders = [c for c in space.companies if c.market_tier == "established"]
    emergers = [c for c in space.companies if c.market_tier == "emerging"]
    ctx = (
        f"SEED COMPANY: {s.display_name} [{s.domain}]\n"
        f"What it does: {s.description}\n"
        f"Stage {s.funding_stage}, ${s.total_funding_m}M raised, {s.employees} employees, "
        f"{s.growth_12m}% headcount growth over 12m, founded {s.founded_year}; industries {s.industries}.\n"
        f"Its position: funding rank #{space.funding_rank}/{space.funding_of}, "
        f"headcount #{space.headcount_rank}/{space.headcount_of}, growth #{space.growth_rank}/{space.growth_of}.\n\n"
        "Tiers: ESTABLISHED PLAYERS are the entrenched market leaders (public/IPO, acquired, or large & long-established / self-sustaining). "
        "EMERGING PLAYERS are the newer, high-growth challengers (early-stage through late-stage venture, seed to pre-IPO).\n\n"
        f"ESTABLISHED PLAYERS ({len(leaders)}):\n" + ("\n".join(_line(c, desc=True) for c in leaders[:8]) or " (none)") + "\n\n"
        f"EMERGING PLAYERS ({len(emergers)}):\n" + ("\n".join(_line(c, desc=True) for c in emergers[:10]) or " (none)") + "\n\n"
        f"MARKET: ~{space.num_credible_peers} credible peers, {space.intensity_label}, {space.maturity_label}, "
        f"median founded {space.median_founded_year}, ${space.total_capital_m}M total disclosed capital."
    )
    instructions = (
        "\n\nWrite these fields (2-4 sentences each unless noted):\n"
        f"- space_name: a precise market label (e.g. 'Document automation & e-signature').\n"
        "- space_themes: 4-6 short tags for what defines the space.\n"
        f"- company_summary: what {s.display_name} actually does and the role/angle it plays in this market — not a stat list.\n"
        "- space_summary: orient the investor — how the market is structured and consolidated, where competition really happens, what makes it attractive or hard to win.\n"
        f"- position_summary: EVALUATE {s.display_name} as a potential investment. Be concrete and opinionated: what does it do that the other companies here do NOT, where is its edge or its vulnerability, and what would most influence a decision to back it or pass. This is the most important field.\n"
        "- established_summary: characterise the established leaders — what their dominance and distribution mean for the space and for a new bet against or alongside them.\n"
        "- emerging_summary: characterise the emerging players — the newer, high-growth, venture-backed challengers: who is differentiating, who could break out, and the consolidation dynamics."
    )
    return ctx + instructions


# --- per-company (Haiku) ---------------------------------------------------

_COMPANY_SYSTEM = (
    "You write concise, factual company descriptions for an investor. Ground every "
    "statement in the provided text; if it's empty or clearly about a different company, "
    "return empty strings. No marketing language, no markdown."
)


async def _company_ai(client: AsyncAnthropic, space: Space, settings: Settings) -> _Batch:
    displayed = _displayed_companies(space)
    lines = [f"- {c.domain} | {c.display_name}: {c.description or '(no description)'}" for c in displayed]
    prompt = (
        "For each company below return, keyed by its domain:\n"
        "- blurb: ONE factual sentence (max ~16 words) on what it does.\n"
        "- summary: 2-3 sentences covering what it does, who it serves, and anything notable about its scale or positioning.\n\n"
        + "\n".join(lines)
    )
    resp = await client.messages.parse(
        model=settings.blurb_model,
        max_tokens=4000,
        system=_COMPANY_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
        output_format=_Batch,
    )
    return resp.parsed_output


def _displayed_companies(space: Space) -> list[Company]:
    """Seed + peers (established leaders first, then by similarity), capped to bound the call."""
    from app.pipeline.analysis import _field

    ranked = sorted(
        _field(space.seed, space.companies),
        key=lambda c: (not c.is_seed, c.market_tier != "established", -c.similarity),
    )
    seen: set[str] = set()
    out: list[Company] = []
    for c in ranked:
        if c.domain and c.domain not in seen:
            seen.add(c.domain)
            out.append(c)
        if len(out) >= 24:
            break
    return out
