---
name: uig
description: >
  Build a User Input Grid (UIG) for an AI product or feature, evaluate existing eval datasets
  against it, and propose new inputs to fill coverage gaps. Use this skill whenever someone
  asks to design an eval framework, audit a test set, build a "user input grid", "synthetic
  query matrix" or "SQM", improve dataset coverage, or assess whether their offline evals
  reflect what real users will actually send. Also trigger when they share a product domain
  + sample dataset and want to know what the dataset is missing, or when they're setting up
  evals from scratch for a new AI feature. Output is a markdown file (UIG framework + dataset
  evaluation + recommendations) saved to the current project directory.
---

# User Input Grid Skill

A User Input Grid (UIG) — also called a Synthetic Query Matrix (SQM) — is a structured framework
for ensuring eval coverage of an AI product reflects the real diversity of users, content domains,
input types, and input styles the system will face in production. It comes from the Reforge AI
Evals curriculum and a few teams at Amplitude, Linear, and Notion have published versions of it.

The core idea: pick 3–5 dimensions that drive meaningful diversity in your product, define 4–7
values per dimension, and treat the cartesian product (pruned for plausibility) as your eval
sourcing matrix. A 4-dimension grid with average ~5 values per dimension gives ~625 theoretical
combinations — practical eval sets land at 30–80 high-coverage inputs after pruning.

The reason this matters: most AI eval datasets are built from one of three weak sources — engineer
intuition (overfits to features the engineer knows about), real-user logs (overfits to common
easy cases users actually try), or synthetic generation without a framework (random uneven
coverage). A UIG forces you to be deliberate about *what* you're testing, makes gaps visible, and
gives you a shared vocabulary with the product team for talking about coverage.

## When to use this skill

This skill triggers in three modes — be explicit about which one you're in before starting:

1. **Greenfield UIG** — designing a UIG for a new AI product/feature with no existing dataset.
   Workflow ends at "framework + example inputs to seed the dataset."

2. **Audit existing dataset(s)** — there are one or more eval datasets and you want to know what
   they're missing. Workflow includes evaluating each dataset against the UIG with STRONG/PARTIAL/WEAK
   coverage ratings, surfacing gaps, and recommending additions.

3. **Both** — design the UIG informed by patterns in the existing dataset, then audit the dataset
   against the UIG. This is the most common case when a team has been building evals ad-hoc and
   wants to put structure around them.

If the mode isn't specified, ask in one short question, then proceed.

## Workflow

### Step 1 — Understand the product

Before designing dimensions, you need to know: what does this AI product do, who uses it, what
data does it have access to, what tools does it call, and what does success look like? Don't skip
this — a UIG built without product understanding produces generic dimensions that don't catch real
failure modes.

If the user has shared product docs, sample inputs, system prompts, or tool definitions, read them
first. If you don't have enough context, ask 2–3 specific questions — not a generic interview.
Examples: "What actions can the AI take? Are there topics it explicitly can't handle? What are the
most common user goals?"

### Step 2 — Read the dataset(s) if any exist

If there are existing datasets, read them before designing the UIG. Real input data is the best
signal you have. Look for:

- **Persona signals** — are there user-type labels in metadata? Do inputs imply different user
  contexts (new user, power user, admin, customer vs. employee)?
- **Domain coverage** — what topic areas do inputs touch? What's missing from the inputs that
  the product clearly supports?
- **Input type distribution** — how many action instructions vs. information requests vs.
  multi-step tasks vs. ambiguous inputs?
- **Style patterns** — are inputs well-specified, vague, count-only, edge cases?
- **Scoring criteria quality** — are pass/fail criteria deterministic, or vague LLM-judge prompts?
  Watch for OR conditions ("X *or* asks for clarification") that make the test always pass.

This "dataset-first reading" surfaces dimensions you'd never invent from first principles.

### Step 3 — Design the dimensions

Pick **3–5 dimensions**. Fewer than 3 and the grid doesn't drive enough diversity; more than 5 and
the cartesian product explodes and the dimensions start overlapping conceptually.

**Two dimensions are nearly universal** for any AI product. Use these as defaults, adapted to
context:

#### Input Type — what the user is asking the AI to do

| Value | Definition | Example |
|-------|-----------|---------|
| Action instruction | Direct the AI to perform an operation | "Update the Nike opportunity to Closed Won" |
| Information request | Ask the AI to retrieve or explain something | "What's the status of case #12345?" |
| Aggregation | Compute or summarize across a set | "How many open P1 cases do I have this week?" |
| Multi-step | Chain of operations in one input | "Find at-risk accounts and draft outreach emails" |
| Clarification / follow-up | Continue or refine a prior turn | "Actually, make the tone more formal" |
| Ambiguous / under-specified | Intent unclear, AI must resolve | "Handle this" with no supporting context |
| Edge / out-of-scope | Outside the AI's topics or capabilities | A request the system is not designed to fulfill |

For products with workflow-triggered inputs (no user text — an automated record or event fires the
AI): add **Automated trigger** as a value and ensure your eval dataset includes both human-initiated
and system-initiated inputs.

For AI products with traditional search/query interfaces, "Action instruction" may be rare and
"Lookup" a better fit — adapt the values to what users actually send.

#### Input Style — how well-formed or specified the input is

| Value | Definition | Example |
|-------|-----------|---------|
| Well-specified | Complete, unambiguous, all context present | Clear intent, named entities, no missing fields |
| Under-specified | Missing context or intent the AI must infer | Vague instruction, implied subject, no record ID |
| Multi-constraint | Multiple conditions that must all be satisfied | "Empathetic but firm, under 100 words, no jargon" |
| Jargon-heavy | Domain- or org-specific terminology | Internal product codes, CRM field names, acronyms |
| Edge / out-of-scope | Impossible, self-contradicting, or out of bounds | Request the AI cannot or should not fulfill |

**Two dimensions are always domain-specific** and need to be derived from the product:

- **User Persona** — different user types whose context changes what a good response looks like.
  Don't fall back to "novice / intermediate / expert" — that's a smell. Real personas are defined
  by their goals and context (e.g. "sales rep closing deals" vs. "service agent handling escalations"
  vs. "customer self-serving on a portal").
- **Data/Content Domain** — the distinct topic areas, capability surfaces, or data categories the
  product covers. This is the dimension you most need the dataset to inform — first-principles
  drafts almost always miss something.

For agent products, consider a fifth dimension: **Action/Output Type** — what the AI *produces*
(drafted email, updated record, routing decision, summary, action refusal). This catches output
format and action correctness bugs that input-diversity dimensions alone won't surface.

For each dimension, define 4–7 values. Each value needs a **short justification** (one sentence on
why it's distinct from the others) and a **characteristic example input** showing what it generates.

### Step 4 — Write the UIG markdown file

Ask the user where to save the output. Default: `<product-name>-uig.md` in the current working
directory.

Structure the file as follows:

```
# [Product Name] User Input Grid
Brief intro paragraph — what product, what the UIG covers, target dataset size.

## Dimensions Overview
Summary table: Dimension | Values | Notes

## [Dimension 1] — [Name]
Table: Value | Definition | Example Input | Why distinct
Notes on judgment calls made.

## [Dimension 2] — [Name]
...

## Example Input Combinations
Table of 8–12 rows sampling the grid: one row per combination, with a concrete example input.
This forces you to verify each combination produces a sensible, testable input.

## Dataset Evaluation  ← only in modes 2 and 3
Per-dataset coverage tables and overall summary.

## Recommendations
Prioritized gap list with example inputs.
```

The example inputs section is important — it makes the abstract grid concrete and forces you to
verify that each combination produces a sensible input. If a combination feels nonsensical when you
try to write an input for it, that's a signal the grid has an implausible region you can prune.

### Step 5 — Evaluate datasets against the UIG (if mode 2 or 3)

For each dataset, rate coverage on each dimension as **STRONG / PARTIAL / WEAK**:

- **STRONG** — most values represented, with clear examples
- **PARTIAL** — some values present, others noticeably missing
- **WEAK** — only one or two values covered

For each (dataset × dimension) cell, write a one-paragraph note covering: what's present, what's
missing, and the practical implication of the gap. The implication matters more than the gap
itself — "no multi-step inputs" is a fact; "the AI could score 95% on this dataset and still be
broken when users chain two operations in a single message" is the point.

**Seven common failure patterns to watch for:**

1. **Persona collapse** — all inputs written from one user type's perspective; the dataset silently
   assumes a single user context even though the product serves multiple roles.
2. **Instruction skew** — too many freeform instructions, missing information requests, aggregations,
   or structured/triggered inputs that the product clearly handles.
3. **Advice-without-criteria** — eval rows that test for "good response" but provide no falsifiable
   scoring criterion. If two evaluators would disagree on pass/fail, the criterion isn't ready.
4. **OR-condition trap** — scoring criteria phrased as "output contains X *or* asks for clarification."
   This always passes because a confused AI can always ask for clarification. Split into two separate
   eval rows.
5. **Real-input feedback loop** — dataset built entirely from real user logs, which overfit to the
   common easy cases actual users send. Rare but high-stakes inputs never appear.
6. **Missing comparison/trend** — time-period and multi-entity inputs are consistently absent because
   they're harder to write; they're also where AI products frequently fail.
7. **Output-quality vs. input-diversity confusion** — hallucination tests (output quality checks)
   mixed into a coverage dataset (input diversity checks). These need separate eval strategies.

After per-dataset tables, write an **overall coverage summary** combining all datasets, then a
**recommendations section** prioritized by impact:

1. Input types that are entirely absent — highest-priority gaps; nothing in the eval suite catches
   these failure modes.
2. Cross-dimension combinations that span two gap areas — catch coordination bugs.
3. Persona-differentiated inputs where the persona context meaningfully shapes the right response.
4. Out-of-scope and edge-case inputs that test graceful decline or scope clarification.
5. Output-quality / hallucination tests for high-stakes domains.

For each recommendation, give 3–6 example inputs with dimension labels and what the test should
verify. Don't just say "add multi-step inputs" — write the actual inputs.

### Step 6 — Expand the dataset (if requested)

If asked to "expand the dataset" or "fill the gaps", generate a fresh markdown file with
**30–80 new inputs** organized by the gap they fill, each tagged with persona / domain / input
type / style. For every input, include an evaluable scoring criterion.

**The OR-condition trap:** Never write a scoring criterion as "output does X *or* asks for
clarification." That criterion always passes — any AI can deflect with a clarifying question.
Instead, split into two rows: one where input is clear and the AI must act, one where input is
genuinely ambiguous and graceful clarification is the right response.

Don't generate from random combinations. Walk through the gaps in priority order and write inputs
deliberately. Aim for inputs that look like what a real user would actually send — including
partial information, casual phrasing, frustration, and incomplete context when that's how real
users communicate.

## Output Format

**Default to markdown.** Ask the user where to save; if unspecified, save to
`<product-name>-uig.md` in the current working directory.

For UIGs with rich tables that benefit from visual layout, an HTML file is also acceptable as a
secondary format. Markdown is the default.

## Working Notes

- **Don't skip the dataset reading step.** First-principles UIGs miss things real data would
  surface. Even 15 minutes reading a sample of real inputs will reshape the grid.

- **Resist the urge to make dimensions orthogonal at all costs.** Some overlap is fine if it
  produces meaningful coverage. "Input Type" and "Input Style" partially overlap (an ambiguous
  input is often also under-specified) but they catch different failure modes — ambiguous tests
  whether the AI resolves intent correctly, while under-specified tests whether it asks the right
  clarifying question.

- **A UIG with 4 dimensions averaging 5 values gives 625 combinations.** You don't need eval
  coverage of all 625 — you need coverage of the dimensions, not the full cartesian product.
  30–80 deliberately chosen inputs that hit each dimension value at least 3 times is much more
  valuable than 500 random combinations.

- **Tables of dimension values should be readable on their own.** Someone glancing at the UIG
  summary table without reading the body should immediately understand the framework. Use short
  value names (1–3 words) and put the longer descriptions in the per-dimension sections.

- **The goal isn't "coverage of every value" — it's catching failure modes the team didn't
  anticipate.** When you write the recommendations section, lead with what *would have been
  caught* if these inputs had been in the eval set. That framing turns abstract coverage gaps
  into concrete reasons to invest.

- **For conversational / multi-turn agents**, include at least a few multi-turn sequences in the
  dataset — not just isolated inputs. A clarification / follow-up row is only testable in context
  of the prior turn. Flag these explicitly in the dataset with a `multi_turn: true` tag.
