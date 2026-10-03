---
name: eval-rubric
description: >
  Write or update the eval rubric for an AI agent or AI feature: the pass/fail criteria that
  define good behavior, in four groups (outcome, trajectory, governance, experience), plus the
  release thresholds that belong in the PRD. Use this skill whenever someone asks to "write an
  eval rubric", "define what good looks like", "add evals to my PRD", "what should we evaluate",
  "turn this PRD into a rubric", "update the rubric from these traces", or shares a PRD, agent
  spec, system prompt or trace codes and wants evaluation criteria. Also use to audit an existing
  rubric. Output is an HTML page and a markdown file saved next to the PRD.
---

# Eval rubric skill

An eval rubric is the written definition of good behavior for one AI product. It is a section of
the PRD. Every line is a pass/fail check on a single trace. Numbers that hold across many traces
(cost, latency, failure rate) are release thresholds and live in their own PRD section.

This skill writes v1 before any traces exist, and v2 after traces have been read. It also audits
a rubric someone else wrote.

Read `references/worked-examples.md` before writing a rubric for the first time in a session. It
shows two products taken from v1 to v2.

## Pick the mode

| The user has | Mode |
|---|---|
| A PRD, spec, system prompt or a product description, and no traces yet | v1 |
| A v1 rubric plus trace codes or annotated traces | v2 |
| A rubric and wants feedback on it | Audit |

If it is unclear, ask one question: "Have you read traces from this agent yet?"

## The four kinds of lines

| Group | Question it answers | Comes from | Typical owner |
|---|---|---|---|
| Outcome (O) | What did it produce, and is it right? | Definition of success | PM, subject expert, engineering |
| Trajectory (T) | How did it get there? | Autonomy table, known risks | Engineering |
| Governance (G) | What must it never do, and always do? | Tool surface, policy, non-goals | Legal, finance, security |
| Experience (X) | How did it feel to the user in this channel? | User and channel | Design |

Rules for every line:

- One behavior per line. If a line has "and" joining two behaviors, split it.
- Pass or fail on one trace. A reviewer reading a single session can decide.
- Observable. The evidence is in the trace: an output, a tool call, an argument, a message.
- About the product, not one demo task. A line written for a coffee order should also hold for
  the pharmacy pickup. If it mentions the demo's subject, rewrite it.
- Specific to this product. Generic lines such as "is helpful" or "is safe" are not rubric lines.
- Governance lines start with "Never" or "Always".
- Give each line an ID: O1, O2, T1, G1, X1. IDs are stable across versions.

## Mode: v1, before traces

### Step 1. Find the inputs

Look for a PRD or spec in the working folder first. Read it fully. The rubric derives from four
parts of it, described in `references/prd-sections.md`:

1. Definition of success
2. Tool surface, with whether each action is reversible
3. Autonomy: for each action, does the agent act, confirm first, or escalate
4. Non-goals and any policy the agent must follow (spend, data, approvals)

Also note the user and channel, because that sets the experience line.

### Step 2. Fill the gaps by interview

If any of the four parts is missing, ask for it. Ask at most five questions, in one batch, and
only for what you could not find:

- What does the agent do when it works, in one sentence?
- Who uses it, through what channel, and what is success measured in (seconds, accuracy,
  auditability)?
- What can the agent do? List every tool or action, and say which ones cannot be undone.
- For the actions that cannot be undone, should it act, confirm first, or hand off to a person?
- What must it never do? Think spend, data, writes, and requests out of scope.

If the user has policy documents, tool definitions or a system prompt, read them instead of
asking. Do not invent tools or policies. If something is unknown, write it under Open questions.

If the PRD has no tool surface or autonomy table, draft both as tables and confirm them with the
user before writing the rubric. They are the source of most governance and trajectory lines.

### Step 3. Write v1

Write ten to fifteen lines in total, in this order:

1. **Outcome: one or two lines** from the definition of success. Task done as requested. Correct
   against ground truth where one exists.
2. **Governance: as many as the PRD supports.** One line for each irreversible action, each
   policy limit, each data boundary and each non-goal that a user could plausibly ask for. This
   group is nearly complete on day one.
3. **Trajectory: two lines at most.** Only the process rules already known to matter, such as
   confirming before an irreversible action or stating assumptions.
4. **Experience: one line** on tone or brevity for this channel.

Do not try to finish trajectory or experience. The odd paths and the friction are not knowable
until traces exist. Say so in the output.

For each line add two short fields:

- **From**: the PRD section it derives from.
- **Check**: `Code` if a rule on the trace can decide it, `LLM judge` if it needs judgment,
  `Human` if neither is practical yet. Prefer `Code`.

### Step 4. Write the release thresholds

Separately from the rubric, propose three to five thresholds for the PRD: cost per task,
latency, and the failure rate the team will accept at launch. Add a threshold tied to a
governance line if a single failure there is unacceptable (for example, zero unapproved writes).
Mark every number as a target until there is data. Never put a threshold inside the rubric.

### Step 5. Check the draft

Before showing it, test every line:

- Could two reviewers reading the same trace disagree on pass or fail? Tighten the wording.
- Does it contain a number that only makes sense across many traces? Move it to thresholds.
- Is it traceable to the PRD? If not, either the PRD or the line is wrong. Flag it.
- Would a vendor's default score cover it? If yes, it is probably too generic. Make it specific
  or cut it.

Then list what v1 cannot know yet: the trajectory and experience lines that only traces reveal.

## Mode: v2, after traces

Inputs: the v1 rubric and either trace codes (from the `trace-codes` skill) or annotated traces.

For each trace code or finding, decide which case it is:

| Case | What to do |
|---|---|
| An existing line caught it | Keep the line. Note the finding as evidence. |
| An existing line caused it (too blunt, too broad) | Sharpen the line. Keep its ID. Record the old wording. |
| Nothing covers it | Add a line in the right group with the next free ID. |
| The behavior is fine and the line is wrong | Rare. Remove the line only with the user's agreement. |

Rules for v2:

- Mark each changed line `New` or `Sharpened`, with the finding that motivated it.
- A v2 mostly adds and sharpens. If the draft removes more than one line, stop and check.
- New lines must still be about the product, not the trace that produced them.
- Recalibrate the release thresholds against real cost and latency if the traces include them.
  Propose a new threshold only when a finding justifies one.
- Open with a short paragraph: how many lines were added and sharpened, and what the traces
  showed that v1 missed.

## Mode: audit

Check an existing rubric against the rules above and report, per line: keep, rewrite (with the
rewrite), split, move to release thresholds, or cut. Then list what is missing by group. A rubric
with no governance lines for an agent that can write, spend or send is incomplete.

## Output

Save two files next to the PRD (or in the working folder if there is no PRD):

- `<product>-rubric-v<N>.md`: the rubric as a table per group, then the release thresholds, then
  open questions.
- `<product>-rubric-v<N>.html`: the same content as a page, built from
  `references/rubric-template.html`. Fill the placeholders and keep the structure.

In the reply, give the count of lines per group, the two or three lines most worth debating with
stakeholders, and what to do next:

- After v1: generate traces and read them, then run `trace-codes`.
- After v2: turn lines into scorers with `eval-code` (lines marked `Code`) and `eval-llm-judge`
  (lines marked `LLM judge`).

## Working notes

- The rubric is the PM's document. Draft it, then ask the user to decide the lines that involve a
  tradeoff. Do not present a rubric as final.
- Keep v1 short. A long v1 is usually trajectory and experience lines that were guessed.
- Who the product is for changes the rubric more than what it does. A consumer agent usually
  guesses and discloses. An enterprise agent usually asks and shows its work. See the two worked
  examples.
- If the agent has no irreversible actions, say that governance will be short and consists of
  policy lines only.
