# PULSE Competitive Landscape — Next Steps

Prep notes for our conversation, not a polished spec.

## What I built and why

A tool that turns a **company domain** into a clear competitive landscape, structured the way an investor actually reasons: **understand the Company → understand the Space → understand the company's Position in it.** A web-search **research agent**, grounded in the same data, handles the follow-up questions.

Under the hood:

- **Pulse API → cleaning pipeline → a small Pydantic domain model → AI enrichment → one page.** The domain model is deliberately just **two objects, `Company` and `Space`** (the space holds the peer companies, the aggregates, the seed's position, and the data-confidence notes). AI enrichment is layered on as *properties* of those objects, never a parallel structure.
- **Cleaning is rule-based and unit-tested**, because making sense of the messy data is the core of the task. It handles the specific failure modes in the data: the `1`-employee sentinel, structured headcounts that contradict the narrative (PayPal-style), geography derived from the structured array rather than the buggy summary string, year-precision (`-01-01`) dates, inconsistent industry comma-spacing, leaked internal analyst notes, `Keywords:` spam, duplicate domains, **identity quarantine** of wrong-company profiles, and dropping the large similarity-floor block the API returns as padding.
- **AI is used where judgement helps, not for mechanical cleaning**: three narrative summaries (company / space / position) plus a sharper space name and themes, and a batched set of one-line company blurbs. Model choice is per use case — **Sonnet** for the judgement work and the chat agent, **Haiku** for the high-volume blurbs — and the two enrichment calls run **concurrently**.

### Key trade-offs (happy to dig into any of these)

- **Deterministic vs. AI split.** Everything that can be a rule *is* a rule (testable, explainable, cheap); AI only does synthesis. This keeps the output defensible — I can point at why every number is what it is.
- **"Batching" ≠ the Batch API.** The async Batch API is for offline jobs (~1h); wrong for an interactive request. Here, batching means folding many companies into *one* structured call and running independent calls concurrently.
- **Credible peers.** The API returns ~100 results but pads with a big block at its similarity floor (84/100 at exactly 0.6 for PandaDoc). I drop that block and keep the genuine cluster — a heuristic I'd want to validate.
- **Scoped out for time:** persistence, auth, multi-domain search, streaming the result in two phases.

## What I'd explore next

- **Enrich at analysis time, not just in chat** — pull recent funding/news, founders, and customers via web search during the run, with per-field confidence surfaced inline and editable by the user.
- **Caching + perceived latency** — cache landscapes by domain, pre-warm common ones, and stream the page data-first / AI-second (the Pulse call dominates latency).
- **Sharper comparison** — a positioning 2×2, "who's nearest on which axis," and a **compare two companies** mode.
- **Entity resolution** — dedupe rebrands/subsidiaries and reconcile `name` vs `domain` vs description more robustly.
- **Trust** — evals that score the AI summaries for factuality against the structured data; a visible confidence model.
- **Fit** — export into a deal-memo section / push into PULSE so it lands where the work already happens.

## How it fits the investment workflow (assumptions to validate)

- I'm picturing **pre-meeting and early diligence**: a two-minute, consistent landscape before a call, then the chat agent for the long tail ("who's growing fastest and why?", "what's the moat?").
- Assumptions I'd want to test: that the team **starts from a company/domain** (vs. a thesis or a space); that **funding / headcount / growth / maturity** are the right comparison axes; how much they trust an AI summary vs. raw fields; and **where this should live** to actually get used.

## Questions for the stakeholder

1. Walk me through the last competitive landscape you built — what did you start from, and what took longest?
2. Is the win **breadth** (surface every competitor) or a **curated, credible short-list**? Where's the current pain?
3. What decision does this feed — a go/no-go screen, a deep dive, a section of the deal memo?
4. Which signals do you trust **least** today, and what would make you trust this output enough to act on it?
5. Do you think in terms of a company's *competitors*, or a *space* you're mapping? (That changes the entry point.)
6. What do you always end up looking up manually that isn't here — pricing, customers, tech stack, hiring signals?
7. Where should this live — standalone, inside PULSE, in the CRM, in Slack?
