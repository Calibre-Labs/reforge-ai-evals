---
name: uig
description: >
  Build a User Input Grid (UIG) for an AI product or feature, evaluate existing eval datasets
  against it, and propose new queries to fill coverage gaps. Use this skill whenever Sandhya
  asks to design an eval framework, audit a test set, build a "user input grid", "synthetic
  query matrix" or "SQM", improve dataset coverage, or assess whether her offline evals
  reflect what real users will actually ask. Also trigger when she shares a product domain
  + sample dataset and wants to know what the dataset is missing, or when she's setting up
  evals from scratch for a new AI feature. Output is a markdown file (UIG framework + dataset
  evaluation + recommendations) saved to the relevant project subfolder under AgentWork —
  never default to Google Docs.
---

# User Input Grid Skill

A User Input Grid (UIG) — also called a Synthetic Query Matrix (SQM) — is a structured framework
for ensuring eval coverage of an AI product reflects the real diversity of users, content domains,
question types, and query styles the system will face in production. It comes from the Reforge AI
Evals curriculum and a few teams at Amplitude, Linear, and Notion have published versions of it.

The core idea: pick 3–5 dimensions that drive meaningful diversity in your product, define 4–7
values per dimension, and treat the cartesian product (pruned for plausibility) as your eval
sourcing matrix. A 4-dimension grid with average ~5 values per dimension gives ~625 theoretical
combinations — practical eval sets land at 30–80 high-coverage queries after pruning.

The reason this matters: most AI eval datasets are built from one of three weak sources — engineer
intuition (overfits to features the engineer knows about), real-user query logs (overfits to common
easy cases users actually try), or synthetic generation without a framework (random uneven coverage).
A UIG forces you to be deliberate about *what* you're testing, makes gaps visible, and gives you a
shared vocabulary with the product team for talking about coverage.

## When to use this skill

This skill triggers in three modes — be explicit with Sandhya about which one you're in before
starting:

1. **Greenfield UIG** — designing a UIG for a new AI product/feature with no existing dataset.
   Workflow ends at "framework + example queries to seed the dataset."

2. **Audit existing dataset(s)** — Sandhya has one or more eval datasets and wants to know what
   they're missing. Workflow includes evaluating each dataset against the UIG with STRONG/PARTIAL/WEAK
   coverage ratings, surfacing gaps, and recommending additions.

3. **Both** — design the UIG informed by patterns in the existing dataset, then audit the dataset
   against the UIG. This is the most common case when a team has been building evals ad-hoc and
   wants to put structure around them.

If Sandhya doesn't specify, ask which mode in one short question, then proceed.

## Workflow

### Step 1 — Understand the product

Before designing dimensions, you need to know: what does this AI product do, who uses it, what
data does it have access to, what tools does it call, and what does success look like? Don't skip
this — a UIG built without product understanding produces generic dimensions like "easy / medium /
hard" that don't catch real failure modes.

If the user has shared product docs, sample queries, system prompts, or tool definitions, read them
first. If you don't have enough context, ask 2–3 specific questions — not a generic interview.
Examples: "What tools does the AI assistant call? Are there domains it explicitly can't handle?
What are the most common user goals?"

### Step 2 — Read the dataset(s) if any exist

If there are existing datasets, read them before designing the UIG. Real query data is the best
input you have. Look for:

- **Persona signals** — are there user-type labels in metadata? Do queries imply different user
  contexts (freelancer, new user, power user)?
- **Domain coverage** — what data areas do queries touch? What's missing from the queries that
  the product clearly supports?
- **Question type distribution** — how many lookups vs aggregations vs comparisons vs how-to?
- **Style patterns** — are queries well-specified, vague, count-only, edge cases?
- **Scoring criteria quality** — are pass/fail criteria deterministic, or vague LLM-judge prompts?
  Watch for OR conditions ("X *or* asks for clarification") that make the test always pass.

This "dataset-first reading" surfaces dimensions you'd never invent from first principles. In a
real session, reading 185 user questions for Monarch Money revealed a missing "Financial advice/
coaching" question type and a "Transaction management" domain that wasn't in the first-principles
draft.

### Step 3 — Design the dimensions

Pick **3–5 dimensions**. Fewer than 3 and the grid doesn't drive enough diversity; more than 5 and
the cartesian product explodes and the dimensions start overlapping conceptually.

**Two dimensions are nearly universal** for any data/agent product. Use these as defaults, adapted
to context. Read `references/dimension-patterns.md` for the full canonical list with definitions
and examples:

- **Question Type** — what cognitive/tool-use pattern the AI must apply (Lookup, Aggregation,
  Multi-step, Comparison/Trend, Predictive, How-to, etc.)
- **Query Style** — specificity and format of the user's phrasing (Well-specified, Under-specified,
  Count-only, Edge case, etc.)

**Two dimensions are always domain-specific** and need to be derived from the product:

- **User Persona** — different user types whose context changes what a good answer looks like.
  Don't fall back to "novice / intermediate / expert" — that's a smell. Real personas are defined
  by their goals and data shape (e.g. "freelancer with variable income" vs "household manager
  tracking shared budgets").
- **Data/Content Domain** — the distinct data areas, content types, or capability surfaces the
  product covers. This is the dimension you most need the dataset to inform — first-principles
  drafts almost always miss something.

For each dimension, define 4–7 values. Each value needs a **short justification** (one sentence on
why it's distinct from the others) and a **characteristic example query** showing what it generates.

### Step 4 — Write the UIG markdown file

Save the output to `AgentWork/<project-folder>/<descriptive-name>.md`. If you don't know the
project folder, ask. Never default to Google Docs.

Use the structure in `references/output-template.md`. Briefly: Title → intro paragraph → UIG
summary table → one section per dimension with a values table and notes on judgment calls →
example query combinations table covering several rows of the grid.

The example queries section is important — it makes the abstract grid concrete and forces you
to verify that each row produces a sensible query. If a combination feels nonsensical when you
try to write a query for it, that's a signal the grid has an implausible region you can prune.

### Step 5 — Evaluate datasets against the UIG (if mode 2 or 3)

For each dataset, rate coverage on each dimension as **STRONG / PARTIAL / WEAK**:

- **STRONG** — most values represented, with clear examples
- **PARTIAL** — some values present, others noticeably missing
- **WEAK** — only one or two values covered

For each (dataset × dimension) cell, write a one-paragraph note covering: what's present, what's
missing, and the practical implication of the gap. The implication matters more than the gap
itself — "no comparison queries" is a fact; "the AI could score 98% on this dataset and still be
broken at time-period comparisons" is the point.

Read `references/dataset-evaluation.md` for the rating rubric, common failure patterns to watch
for (persona collapse, how-to skew, advice-without-criteria, OR conditions, real-query feedback
loops), and how to handle output-quality datasets (like hallucination guardrail tests) which need
different criteria than input-diversity datasets.

After per-dataset tables, write an **overall coverage summary** combining the datasets, then a
**recommendations section** prioritized by impact:

1. Question types that are entirely absent — these are the highest-priority gaps because they
   represent failure modes nothing in the eval suite would catch.
2. Cross-domain queries that span two dimension values — usually missing because real users don't
   phrase them this way, but they catch coordination bugs.
3. Persona-differentiated queries where the persona context meaningfully shapes the right answer.
4. Out-of-scope and edge-case queries that test graceful decline / scope clarification.
5. Output-quality / hallucination tests for high-stakes domains.

For each recommendation, give 3–6 example queries with the dimension labels and what the test
should verify. Don't just say "add comparison queries" — write the actual queries.

### Step 6 — Expand the dataset (if requested)

If Sandhya asks to "expand the dataset" or "fill the gaps", generate a fresh markdown file with
**30–80 new queries** organized by the gap they fill, each tagged with persona / domain / question
type / style. For every query, include an evaluable scoring criterion — read
`references/eval-best-practices.md` for what makes a criterion evaluable (and the OR-condition
trap that makes a criterion always pass).

Don't generate from random combinations. Walk through the gaps in priority order and write queries
deliberately. Aim for queries that look like things a real user would type — including typos, casual
phrasing, frustration, and incomplete sentences when the dataset shows that's how real users write.

## Output Format

**Default to markdown.** Save to `AgentWork/<project>/<name>.md`. Sandhya's standing instruction
is to never default to Google Docs for working outputs.

If Sandhya explicitly asks for a Google Doc, deck, or Word doc, hand off to the appropriate skill
(`gdrive-pro:gdoc-ent`, `gdrive-pro:gslide-ent`, or `docx`) — don't try to recreate UIG output in
those formats from this skill.

For UIGs with rich tables that benefit from visual layout, an HTML file is also acceptable as a
secondary format. But markdown is the default.

## Reference Files

Read these as you need them — don't load them all upfront.

- `references/methodology.md` — Deep theory: where UIG comes from, why dimensions matter more than
  raw query count, the relationship to test pyramids, when UIG is the wrong tool.
- `references/dimension-patterns.md` — Canonical Question Type and Query Style values with
  definitions, plus a catalog of Persona and Domain dimension patterns observed across products
  (financial, search, support, code-gen, content-gen).
- `references/dataset-evaluation.md` — STRONG/PARTIAL/WEAK rubric, the seven common failure
  patterns (persona collapse, how-to skew, advice-without-criteria, OR conditions in scoring,
  real-query feedback loop, missing comparison/trend, output-quality vs input-diversity confusion),
  and worked examples.
- `references/eval-best-practices.md` — LLM-judge vs deterministic scoring, criteria that can be
  programmatically checked vs criteria that need human judgment, the OR-condition trap, when to
  use expected outputs vs scoring rubrics, multi-turn coverage, and how to handle high-stakes
  vs low-stakes failures differently.
- `references/output-template.md` — The exact markdown structure for the UIG file. Headings,
  table layouts, recommendation format.

## Working Notes

- **Don't skip the dataset reading step.** First-principles UIGs miss things real data would
  surface. Even 15 minutes spent reading a sample of real queries will reshape the grid.

- **Resist the urge to make dimensions orthogonal at all costs.** Some overlap is fine if it
  produces meaningful coverage. "Question Type" and "Query Style" partially overlap (a count-only
  question is usually an aggregation) but they catch different failure modes — count-only tests
  output format, while aggregation tests arithmetic correctness.

- **A UIG with 4 dimensions averaging 5 values gives 625 combinations.** You don't need eval
  coverage of all 625 — you need coverage of the dimensions, not the full cartesian product.
  30–80 deliberately chosen queries that hit each dimension value at least 3 times is much more
  valuable than 500 random combinations.

- **Tables of dimension values should be readable on their own.** Someone glancing at the UIG
  summary table without reading the body should immediately understand the framework. Use short
  value names (1–3 words) and put the longer descriptions in the per-dimension sections.

- **The goal isn't "coverage of every value" — it's catching failure modes the team didn't
  anticipate.** When you write the recommendations section, lead with what *would have been
  caught* if these queries had been in the eval set. That framing turns abstract coverage gaps
  into concrete reasons to invest.
