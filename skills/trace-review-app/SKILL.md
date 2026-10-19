---
name: trace-review-app
description: >
  Design and build a custom trace review app for one AI product: a single-page tool where the
  team reads traces, writes notes, labels pass or fail, tags trace codes and exports the results
  for other skills. Built around that product's own trace shape, rubric and failure modes, and
  set up so reviewing becomes a habit (a queue, progress, streaks, quick keys). Use this skill
  whenever someone asks to "build a trace viewer", "make an annotation tool", "set up a review
  page for our traces", "make trace review less painful", "build a labeling app", or says the
  team isn't reading traces because the tool is clunky.
---

# Trace review app skill

Generic trace tools show every trace the same way and leave the judging to the reader. Teams
open them, spend too long learning them, and stop reviewing. A review app built for one product
shows what matters for that product first, asks the questions its rubric asks, and makes a
review session short enough to do every day.

This skill designs that app and builds it as one HTML file that opens from a folder, with no
hosting and no account. The person still does the reading and the judging. The app makes that
faster and keeps the results in a shape the other skills can use.

## Inputs

| Input | Required | Typical form |
|---|---|---|
| Sample traces | Yes | A folder of trace files (JSON or JSONL), five or more |
| What the product does | Yes | The PRD, or a few sentences from the user |
| Rubric | Helpful | The eval rubric, so labels can be per rubric line |
| Trace codes | Helpful | A trace codes file from `trace-codes`, used as tags |
| Who reviews | Helpful | PMs, domain experts, support leads, and how many |

Look for these in the working folder before asking. Read at least five traces before designing
anything: the shape of the trace decides the layout.

## Workflow

### Step 1. Learn the product and its traces

Write down, in a few lines each:

- What one session is: one turn or many, which tools, what the user sees at the end.
- What the final output looks like (a table, an email, a booking, code, a chart) and how to
  render it so a reviewer sees what the user saw.
- Where the failures worth finding sit: in the final answer, in a tool call, in what was
  retrieved, in cost or latency. Use the rubric and trace codes if they exist.
- Which parts of a trace a reviewer can skip.

### Step 2. Ask three questions

Ask only what the files don't answer:

1. Who reviews, and how much time do they have? (Five minutes a day and an hour a week need
   different designs.)
2. What do the reviews feed? Free-text notes for `trace-codes`, pass or fail labels for
   `llm-align`, new dataset rows for `ticket-to-eval`, or all three.
3. Is there anything a reviewer must never see, such as personal data that should be masked?

### Step 3. Write the design

Write a one-page design and show it before building. Cover:

- **The queue.** What order traces come in (newest, flagged by a judge, random sample, least
  reviewed) and how a reviewer picks up where they left off.
- **The trace view.** What shows first: the user's request and the final output, rendered the
  way the user saw it. Then the steps, collapsed by default, with the product's own labels
  (for an agent: model calls, tool calls, retrieved content, tagged by part of the product).
  Highlight what the rubric cares about, such as sources next to the figures they support.
- **The review panel.** A notes box, pass or fail per rubric line or overall, trace-code tags
  with a way to add a new one, and a "flag for discussion" button. Keyboard shortcuts for
  every action.
- **Keeping it a habit.** A daily goal (for example ten traces), a progress bar for the queue, a
  streak for days with a review, a short summary at the end of a session (traces read, codes
  used most, disagreements with the judge), and per-reviewer counts when more than one person
  reviews. Keep it calm: no points for speed, nothing that rewards labeling without reading,
  and celebrations small and rare.
- **Codes back in the app.** If the app keeps notes in a shared store, add a Codes tab that shows
  what `trace-codes` writes to `codes/current` (see that skill), and the codes on each trace. Then
  nobody has to export notes to cluster them.
- **Exports.** Notes as CSV for `trace-codes` (trace id, input, reviewer, note), labels for
  `llm-align` (trace id, rubric line, label, reviewer), and flagged traces as candidate dataset
  rows. One click each.
- **Where it keeps data.** In the browser for one reviewer, or a shared store if several people
  review the same traces. Say which and why.

### Step 4. Build it

Build one self-contained HTML file that loads trace files the user picks from a folder (or
reads them from a path next to the file). Follow the product's own trace format; don't force it
into a generic schema. Keep the design plain and readable: the trace is the content.

### Step 5. Test it on real traces

Open it with the sample traces and do a short review session yourself: label five traces, tag
two codes, export each file and check the exports load in the skills that read them. Fix what
gets in the way. Then hand it over with one paragraph on how to use it and the keyboard
shortcuts.

## Output

1. The design, as a short markdown file next to the app.
2. The app, as one HTML file.
3. A sample export of each kind, from the test session.

## Example

The fall 2026 course's Mapper trace review page is a small version of this: nine Mapper
sessions, the market map rendered the way the user saw it, the steps tagged by part of the
product, a notes box saved under each reviewer's name, and a Codes tab that `trace-codes` writes to. A full
version would add pass or fail labels per rubric line, code tags, a queue and a daily goal.
