---
name: trace-codes
description: >
  Turn free-form notes from reading agent traces into trace codes: named, yes/no failure or
  quality patterns with definitions, examples and counts. Use this skill whenever someone has
  annotated traces or review notes and asks to "cluster my notes", "create trace codes", "find the
  failure modes", "do error analysis on these annotations", "what patterns are in these traces",
  or "what should we fix first". Also use to merge new notes into an existing set of codes.
  Output is a trace codes file, a labeling sheet for human review, and proposed rubric updates.
---

# Trace codes skill

Trace analysis has three steps: build a set of inputs and run the agent, read the traces and
write notes, then cluster the notes into codes. A person does the reading. This skill does the
clustering and everything that follows from it.

A trace code is a short name for one pattern seen across traces, defined so that anyone can
answer yes or no for a single trace. Codes become the vocabulary for the rubric, the backlog and
the automated evals.

Do not write the notes yourself. If the user has traces and no notes, tell them to read and
annotate at least ten first. Reading is where product judgment comes in, so a person does it.
You may help them read faster (summarize a long trace, point at the tool calls) but the
observations must be theirs.

## Inputs

| Input | Required | Typical form |
|---|---|---|
| Notes | Yes | A CSV or JSON with a trace id and a free-text note per trace. Pasted text also works. |
| Traces | Helpful | The files or folder the notes refer to, so examples can quote what happened |
| Rubric | Helpful | The current eval rubric, to map each code to a line |
| Existing codes | If any | A previous trace codes file to merge into |

Find these in the working folder before asking. If the notes have no trace ids, number them and
say so.

## Workflow

### Step 1. Split notes into observations

One note often contains several observations ("stale revenue number, also no source for the
third company, good scoping question"). Split each note into single observations and keep the
trace id with each. Keep positive observations too. A code can describe something the agent
should keep doing.

### Step 2. Cluster into codes

Group observations that describe the same pattern. For each group write:

- **Title**: three to six words, descriptive, no jargon the team would not use.
- **Definition**: one sentence that can be answered yes or no for a single trace. Start with
  "The agent ..." or "The output ...".
- **Examples**: two or three, each with the trace id and a short paraphrase of what happened.
  Quote the trace when it is available.
- **Count**: how many traces show it, out of how many were annotated.

Rules:

- Codes must not overlap. If two definitions would both say yes for the same reason on the same
  trace, merge them or redraw the line between them.
- Split a code when its examples have different causes or would need different fixes.
- Do not force every observation into a code. List the leftovers under "Unclustered" with their
  trace ids. Leftovers are often the start of the next code.
- Expect six to twelve codes from ten to thirty traces. Far more than that usually means the
  codes are too narrow.
- Use the reviewer's words where possible. Do not import a generic taxonomy.

### Step 3. Tag each code

Add three tags to every code:

- **Rubric group**: outcome, trajectory, governance or experience.
- **Rubric line**: the ID of the line it relates to if a rubric exists, and whether that line
  caught it, caused it, or nothing covers it.
- **Layer**, when the trace shows it: context (the model had the information and misused it),
  retrieval (the wrong or stale information came in), harness (the code around the model did or
  failed to do something) or systems (cost, latency, a tool or API failing). Write "unknown" if
  the notes and traces do not show the cause. Do not guess.

### Step 4. Recommend the next step for each code

Work through these questions in order:

1. Was the agent ever told to handle this? If not, it is a specification gap. Recommend a prompt
   or PRD change, not an eval.
2. Does it work in some cases and fail in others? If it never works, recommend a design change
   (a tool, a retrieval step, a different architecture), not an eval.
3. If it works inconsistently, it needs an eval. If a rule on the trace can decide it, recommend
   a code-based eval. Otherwise recommend an LLM judge.

### Step 5. Prioritize

Rank codes by how often they occur and how much each one costs the user or the business. An
irreversible or trust-breaking failure outranks a frequent cosmetic one. If user feedback exists
(tickets, thumbs, complaints), note which codes it supports. Name the top three.

### Step 6. Propose rubric changes

If a rubric exists, list the changes the codes imply, one per line: add a line, sharpen a line,
or no change because an existing line already caught it. Do not edit the rubric here. Offer to
run `eval-rubric` in v2 mode with these codes.

## Output

Save three files in the working folder:

1. `trace-codes.md`: a summary table (code, definition, count, rubric group, layer, next step),
   then one section per code with its examples, then Unclustered, then proposed rubric changes.
2. `trace-codes.csv`: one row per code with the same fields, for other skills and tools to read.
3. `trace-labels.csv`: one row per annotated trace and one column per code. Pre-fill a cell with
   `suggested` only where the reviewer's own note supports it. Leave the rest blank. The reviewer
   confirms or corrects every cell with `yes` or `no`. These human labels are what judges get
   calibrated against later, so never present suggestions as labels.

In the reply, give the number of traces and codes, the top three codes with counts, and the one
question the reviewer should settle first (usually a code with a fuzzy boundary).

## Merging new notes into existing codes

When a trace codes file already exists, assign new observations to existing codes first. Create
a new code only when several observations fit none. Report what changed: counts that moved, new
codes, and codes that should now be split or retired. Keep code titles stable so earlier labels
stay valid.

## Knowing when to stop reading

If the last ten traces produced no new code, the reviewer has likely seen enough for this
version of the agent. Say so. Reading starts again whenever the agent changes in a meaningful
way: a new tool, a new prompt, a new model.

## Working notes

- Paraphrase examples. Strip names, emails and other personal data from anything quoted.
- A code that only one reviewer can apply is not finished. Rewrite the definition until a second
  person would give the same answer.
- Counts from ten traces tell you the order of the codes. They are too few to report as
  percentages of production traffic.
