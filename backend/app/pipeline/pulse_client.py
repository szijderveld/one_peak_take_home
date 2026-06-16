"""Client for the Pulse Competitor Intelligence API.

Live calls trust the `success` boolean (not just the HTTP status) and retry on
the documented ~30s timeout — a repeated request warms the server cache and
usually succeeds. Demo mode replays a bundled synthetic fixture instead.
"""

import asyncio
import json
from pathlib import Path

import httpx

from app.config import Settings
from app.models.raw import PulseResponse

_ENDPOINT = "/api/external/competitor_search"
_FIXTURE_DIR = Path(__file__).resolve().parents[2] / "fixtures" / "demo"


class PulseError(RuntimeError):
    """Raised when a search cannot be completed (auth, repeated timeout, …)."""


async def get_competitors(domain: str, settings: Settings, mode: str = "live") -> PulseResponse:
    """Single entry point used by the pipeline."""
    if mode == "demo":
        return load_demo(domain).response
    return await fetch_live(domain, settings)


async def fetch_live(domain: str, settings: Settings, *, retries: int = 4) -> PulseResponse:
    if not settings.pulse_api_key:
        raise PulseError("PULSE_API_KEY is not set")

    url = settings.pulse_base_url + _ENDPOINT
    headers = {"X-API-Key": settings.pulse_api_key, "Content-Type": "application/json"}
    body = {"domains": [domain]}  # one domain per call — multi-domain reliably times out
    last_reason = "unknown"

    async with httpx.AsyncClient(timeout=45.0) as client:
        for attempt in range(retries):
            try:
                resp = await client.post(url, headers=headers, json=body)
            except httpx.TimeoutException:
                last_reason = "request timed out"
                await asyncio.sleep(1.0)
                continue

            if resp.status_code == 200:
                data = PulseResponse(**resp.json())
                if data.success:
                    return data
                last_reason = data.message or data.error or "search reported failure"
            elif resp.status_code in (502, 503, 504):
                last_reason = f"upstream {resp.status_code} (search exceeded budget)"
            else:  # 401/403/etc — not transient, fail fast
                raise PulseError(f"Pulse API error {resp.status_code}: {_detail(resp)}")

            await asyncio.sleep(1.0)  # let the cache warm, then retry

    raise PulseError(f"Pulse search for {domain!r} did not succeed after {retries} attempts ({last_reason}).")


def _detail(resp: httpx.Response) -> str:
    try:
        return str(resp.json())
    except Exception:
        return resp.text[:200]


class DemoBlob:
    """A bundled real response + its pre-baked AI enrichment."""

    def __init__(self, raw: dict, enrichment: dict):
        self.response = PulseResponse(**raw)
        self.enrichment = enrichment


def available_demo_domains() -> list[str]:
    if not _FIXTURE_DIR.exists():
        return []
    return sorted(p.stem for p in _FIXTURE_DIR.glob("*.json"))


def load_demo(domain: str = "") -> DemoBlob:
    """Load the bundled fixture for `domain`, falling back to the first available."""
    domains = available_demo_domains()
    if not domains:
        raise PulseError("No demo fixtures — run scripts/build_demo_fixture.py")
    pick = domain if domain in domains else domains[0]
    blob = json.loads((_FIXTURE_DIR / f"{pick}.json").read_text())
    return DemoBlob(raw=blob["raw"], enrichment=blob.get("enrichment", {}))
