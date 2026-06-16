"""Build the bundled demo fixtures from REAL Pulse responses.

For each demo domain: call the live API, run the full cleaning + analysis
pipeline, bake AI enrichment (if a key is set), and write
`backend/fixtures/demo/<domain>.json` ({raw, enrichment}). Demo mode then
replays these offline.

    cd backend && PYTHONPATH=. uv run python scripts/build_demo_fixture.py [domain ...]
"""

import asyncio
import json
import sys
from pathlib import Path

from app.config import get_settings
from app.enrichment.enricher import enrich, extract_enrichment
from app.pipeline.pipeline import build_from_response
from app.pipeline.pulse_client import fetch_live

OUT_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "demo"
DEFAULT_DOMAINS = ["pandadoc.com", "gocardless.com", "groundcover.com"]


async def main() -> None:
    settings = get_settings()
    domains = sys.argv[1:] or DEFAULT_DOMAINS
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for domain in domains:
        print(f"[{domain}] fetching live…", flush=True)
        resp = await fetch_live(domain, settings)
        space = build_from_response(resp, settings, "demo")
        if settings.ai_enabled:
            await enrich(space, settings)

        path = OUT_DIR / f"{domain}.json"
        path.write_text(json.dumps({"raw": resp.model_dump(), "enrichment": extract_enrichment(space)}, indent=2))
        print(
            f"[{domain}] peers={space.num_credible_peers} quarantined={space.quarantined_count} "
            f"unreliable={space.unreliable_headcount_count} AI={'baked' if settings.ai_enabled else 'off'} → {path.name}"
        )

    if not settings.ai_enabled:
        print("\nNo ANTHROPIC_API_KEY — fixtures have no AI summaries. Set the key and re-run to bake them.")


if __name__ == "__main__":
    asyncio.run(main())
