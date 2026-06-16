"""Standalone smoke test for the research agent — no frontend involved.

    cd backend && PYTHONPATH=. uv run python scripts/try_agent.py [domain] [question]
"""

import asyncio
import sys

from app.agent.research_agent import ResearchAgent
from app.config import get_settings
from app.enrichment.enricher import enrich
from app.pipeline.pipeline import build_landscape


async def main() -> None:
    domain = sys.argv[1] if len(sys.argv) > 1 else "pandadoc.com"
    question = (
        sys.argv[2]
        if len(sys.argv) > 2
        else "How crowded is this market, and who are the two best-funded competitors?"
    )
    settings = get_settings()
    if not settings.ai_enabled:
        print("Set ANTHROPIC_API_KEY in backend/.env first.")
        return

    space = await build_landscape(domain, settings, mode="live")
    await enrich(space, settings)
    print(f"Landscape: {space.name} | {space.num_credible_peers} peers")
    print(f"Q: {question}\nA: ", end="", flush=True)

    agent = ResearchAgent(settings, space)
    async for delta in agent.stream([{"role": "user", "content": question}]):
        print(delta, end="", flush=True)
    print()


if __name__ == "__main__":
    asyncio.run(main())
