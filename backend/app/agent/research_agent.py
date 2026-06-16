"""Standalone PULSE research agent.

Wraps Claude (Sonnet) with the server-side web-search tool and the current
competitive-landscape as grounding context. Self-contained — exercise it via
`scripts/try_agent.py`; the `/api/chat` route just streams `stream()`.
"""

from collections.abc import AsyncIterator

from anthropic import AsyncAnthropic

from app.config import Settings
from app.models.domain import Company, Space

WEB_SEARCH_TOOL = {"type": "web_search_20260209", "name": "web_search", "max_uses": 5}

_SYSTEM_INTRO = (
    "You are the PULSE research agent, helping an investment team understand a "
    "company's competitive landscape. You are given cleaned landscape data below. "
    "Answer questions about the company, its competitors, funding, headcount, and "
    "market positioning.\n\n"
    "Rules:\n"
    "- Prefer the provided data. Quote its numbers exactly.\n"
    "- Use web search for anything not in the data, or for current information "
    "(recent funding rounds, news, leadership, up-to-date headcount).\n"
    "- Be concise and specific. Don't invent figures; if unknown, say so.\n"
    "- When you use the web, briefly note the source.\n"
    "- Reply in short plain-text paragraphs for a chat bubble. Do NOT use markdown "
    "headings (#) or bold (**…**); a simple '- ' list is fine.\n"
)


class ResearchAgent:
    def __init__(self, settings: Settings, space: Space):
        self.settings = settings
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.system = _SYSTEM_INTRO + "\n=== LANDSCAPE DATA ===\n" + _context(space)

    async def stream(self, messages: list[dict]) -> AsyncIterator[str]:
        """Yield assistant text deltas. Web search runs server-side, interleaved."""
        async with self.client.messages.stream(
            model=self.settings.chat_model,
            max_tokens=1024,
            # Cache the (large, stable) landscape context across turns.
            system=[{"type": "text", "text": self.system, "cache_control": {"type": "ephemeral"}}],
            tools=[WEB_SEARCH_TOOL],
            messages=messages,
        ) as stream:
            async for event in stream:
                if event.type == "content_block_delta" and event.delta.type == "text_delta":
                    yield event.delta.text


def _company_line(c: Company) -> str:
    bits = [
        c.display_name,
        f"[{c.domain}]",
        f"sim={c.similarity:.2f}",
        f"${c.total_funding_m}M raised" if c.total_funding_m is not None else "funding n/a",
        f"{c.employees} emp" if c.employees is not None else "emp n/a",
        f"{c.growth_12m}% 12m" if c.growth_12m is not None else "",
        c.funding_stage or "",
        f"founded {c.founded_year}" if c.founded_year else "",
        f"{c.hq_city}, {c.hq_country}" if c.hq_country else "",
    ]
    line = " | ".join(b for b in bits if b)
    desc = c.ai_blurb or c.description
    return f"- {line}" + (f"\n    {desc}" if desc else "")


def _context(space: Space) -> str:
    s = space.seed
    header = (
        f"SEED COMPANY: {s.display_name} [{s.domain}]\n"
        f"{_company_line(s)}\n\n"
        f"SPACE: {space.name} — {space.num_credible_peers} credible peers, "
        f"{space.intensity_label}, {space.maturity_label} (median founded "
        f"{space.median_founded_year}). Total disclosed capital ${space.total_capital_m}M, "
        f"total headcount {space.total_headcount}. Themes: {', '.join(space.themes)}.\n"
        f"POSITION OF {s.display_name}: funding rank #{space.funding_rank}/{space.funding_of}, "
        f"headcount rank #{space.headcount_rank}/{space.headcount_of}, archetype {space.archetype}. "
        f"Closest comparators: {', '.join(space.closest_comparators[:5])}.\n\n"
        f"COMPETITORS ({len(space.companies)}):"
    )
    return header + "\n" + "\n".join(_company_line(c) for c in space.companies)
