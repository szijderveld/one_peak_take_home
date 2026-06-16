# Next Steps: PULSE Competitive Landscape

## 1. What I built, and why

A tool where you enter a company domain and get a structured, consistent view of
its competitive landscape. It answers the investor's questions by dividing the
view into three interfaces:

- **Company:** an at-a-glance view of what the company does and what it is.
- **The Space:** the market the company operates in. This is a standalone
  representation of the market, which I have chosen to characterise by
  highlighting its **key players**.
- **Market Position:** where the company sits *relative* to that space. It shows
  its relative position, plus its most similar rivals.

The main display is built from the API data, cleaned and lightly enriched with AI
models (which also bring some inherent knowledge of the companies themselves).
This gives a deterministic, controlled view of the space relative to the input
data. On its own, though, that limits how much can be understood about the
problem. To extend the tool, a **research agent** with web search adds a deeper
research layer for users to ask more in-depth questions. The agent is fully aware
of the context on the page, so it can answer questions inside the tool, without
the user switching to a separate LLM or Google.

**Data handling.** The API was a strong starting point, most useful for the
similarity matching that defines the "space," but much of the rest wasn't fully
reliable. The issues were mostly missing fields, but also included implausible
headcounts, descriptions about the wrong company, internal notes leaking into
descriptions, buggy geography data, and padding of the results around the
similarity score. This was handled at the API boundary: raw API data is parsed
into Pydantic classes, with cleaning methods designed field by field and a
priority of only passing through 'clean' companies. The preference was to show
only credible information and never surface wrong-company records. A
**data-confidence panel** tells the user which fields had unreliable data.

## 2. What I'd explore next

In building this there were many avenues to explore: improved workflow
integration, mining more useful information through AI and search, usability
improvements, or scope expansion.

My biggest value-add next step would be to integrate **deep research search** into
the workflow. After the API data is called and cleaned, each section would be
additionally researched by a search-enabled LLM. This would do two things: first,
validate the data currently shown; second, enhance it through research into the
company, the space, and related market activity. This improves the data-quality
issues that already exist in the API and can't be solved by cleaning alone, while
also offering deep research conducted in a systematic way.

### Further priority list

- **User custom prompts.** Different users want slightly different things. The AI
  prompts govern what gets surfaced, so it makes sense to let users tweak them to
  get the exact insight they want from each section.
- **Write-back for users.** Open a field in the API for write-back. As an internal
  tool, the investment team should be able to add notes, or a message board, on
  specific companies.
- **Side-by-side view**. Creation of more indepth views such as companiring two companies side by side. This would be led by what more is needed for the user.
- **Search by description.** This is already available in the API but not yet
  built into the tool. It is a useful expansion that, in effect, lets users create
  their own custom **space**.

## 3. How it fits the workflow

This tool is designed for the start of the investigation of a new company. The
idea is for the investment team to save the 3 to 5 hours of googling and instead
learn the business's proposition and its position in the market in around 20
minutes.

It does this by breaking the market into components and clearly summarising the
key information about each, with a research assistant on hand for any further deep
dives.

The natural next steps after this are to share the result with a colleague or send
a direct message to the business. There are buttons in place for this, to help it
integrate into the rest of the workflow. Improvements here could include AI
drafting an investment-case document straight from this screen, suggesting a
valuation, or building the case for investment by contrasting the company's risk
profile against One Peak's other investments.

## 4. Questions I'd want to ask you

**How are investment decisions made?** I'd want to understand the full workflow,
from identification, to investigation, to the final decision. Each of these stages
probably needs a different tool. Identification, for example, would need a
watchdog-style tool constantly monitoring and raising alerts for companies likely
to pass the next two stages. Ironically, that tool is best built *last*, because
it needs to learn from the evaluation tool first. This POC focuses on
**evaluating an opportunity** (a single company). Knowing what the next stage
looks like helps me build it to integrate well, which is why this broad question
is so useful for guiding everything that follows.

**Where exactly does the "investigation" pain bite?** I know the team is currently
"googling." The goal is to replace and standardise that to save time, so I'd want
to know specifically *what* they're googling and *where* the real pain points are (is this amount of infromation needed, reliability, or more just presentation of information in one place?).

### Further questions

- **Do you start from a specific company, or from a space/thesis you want to map?**
  This tells me whether the priority is diligence on a known target or sourcing
  across a space, which ties directly to the "search by description" step.
- **What signals do you use to make ur decisions**. This guides what metrics should be gathered and displayed in the front end. Also AI models should emullate this thinking.
- **What do you currently trust, and what would make you trust this enough to use
  it in a real decision?** The data-confidence panel is a first step, but I'd want
  to know what moves it from "interesting" to "relied upon."
- **What does the output look like** This decides how much to invest in export, AI drafting, and the share/message actions.

