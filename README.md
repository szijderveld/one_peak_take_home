# PULSE · Competitive Landscape

Enter a company domain → get a clear, consistent view of its competitive
landscape, structured the way an investor reasons about a deal: the **company**,
the **space** it operates in, and its **position** within that space — plus a
web-search **research chat agent** grounded in the same data.

Built on the Pulse Competitor Intelligence API: the messy API data is cleaned,
structured into a small Pydantic domain model, analysed, and enriched with Claude.

> One Peak — Product Data Engineer take-home. See [`NEXT_STEPS.md`](NEXT_STEPS.md)
> for the approach, trade-offs, and discovery questions.

## Stack
- **Backend** — FastAPI + Pydantic (Python 3.12, managed with `uv`)
- **Frontend** — React + TypeScript + Vite + Tailwind; geographic map via d3-geo
- **AI** — Anthropic Claude: Sonnet 4.6 (narrative summaries + research chat),
  Haiku 4.5 (batched per-company blurbs)

## Run

**1. Backend**
```bash
cd backend
cp .env.example .env          # add ANTHROPIC_API_KEY (the Pulse key is prefilled)
uv run uvicorn app.main:app --reload --port 8000
```

**2. Frontend**
```bash
cd frontend
npm install
npm run dev                   # http://localhost:5173  (proxies /api → :8000)
```

Open http://localhost:5173, enter a domain (e.g. `pandadoc.com`), and **Analyse**.

> Without an `ANTHROPIC_API_KEY` the app still works end-to-end — the AI summaries
> and chat are simply disabled (they turn on automatically once a key is present).

## Tests
```bash
cd backend && uv run pytest        # cleaning pipeline, anchored to the data-quality doc
```

## How it works

```
domain ─▶ Pulse API ─▶ clean each record ─▶ select credible peers ─▶ analyse ─▶ AI-enrich ─▶ Space
         (retry on        (cleaning.py,      (drop seed / noise-     (rankings,   (Sonnet +     │
          timeout)         per-field)         floor / quarantine)     shape)       Haiku)        ▼
                                                                                            React UI + chat
```

The whole result is one **`Space`** object: the seed `Company`, the credible peer
`Company` list, the space-level aggregates, the seed's position, the
data-confidence notes, and the AI narrative. The deterministic pipeline and the
AI enrichment are cleanly separated — AI only ever *adds* properties.

### Data handling highlights (the messy bits)
`employees == 1` → unknown; structured headcount that contradicts the narrative →
the narrative figure, flagged; geography from the structured array, never the
buggy summary string; `-01-01` → year precision; inconsistent industry
comma-spacing; leaked internal notes & `Keywords:` spam stripped from
descriptions; duplicate domains de-duplicated; **wrong-company profiles
quarantined**; and the large similarity-floor block the API returns as padding is
dropped so the "space" is genuinely credible. All surfaced in **Data confidence**.

## Project structure
```
backend/
  app/
    models/        raw.py (API DTO) · domain.py (Company, Space)
    pipeline/      pulse_client.py · cleaning.py · analysis.py · pipeline.py
    enrichment/    enricher.py        (concurrent Sonnet + Haiku, structured output)
    agent/         research_agent.py  (Sonnet + server-side web search)
    main.py        /api/landscape · /api/chat (SSE)
  scripts/         try_agent.py
  tests/           test_cleaning.py
frontend/
  src/components/  the four sections, company-card modal, chat panel, charts, map
```

## Notes
- `try_agent.py` exercises the research agent standalone:
  `cd backend && PYTHONPATH=. uv run python scripts/try_agent.py pandadoc.com "how crowded is this market?"`
- The Pulse API enforces a ~30s budget and times out on cold/multi-domain
  requests; the client sends one domain and retries (a repeat warms the cache).
- Real captured Pulse API responses are intentionally not committed (data hygiene).
