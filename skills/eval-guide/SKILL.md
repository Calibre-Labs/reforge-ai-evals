---
name: eval-guide
description: >
  Entry point for eval work. Use when someone asks for help with evals in general, does not know
  where to start, asks "what should I do next", or asks for something no other skill in this
  plugin matches. Do NOT use when a more specific skill in this plugin already matches the
  request. Load that skill directly.
---

# Eval guide

This plugin splits eval work into skills, one per step. This skill only routes. Find the row that
matches the user's situation, say which skill you are loading and why, then load it and follow
its workflow. Do not improvise your own version of a step.

| The user's situation | Skill |
|---|---|
| Has a product, PRD or prompt, and no written definition of good | `eval-rubric` (v1) |
| Has a rubric and needs test inputs, or wants to know what a dataset is missing | `uig` |
| Has read traces and written notes | `trace-codes` |
| Has trace codes and a v1 rubric | `eval-rubric` (v2) |
| Has a rubric line or trace code that a rule can check | `eval-code` |
| Has a rubric line or trace code that needs judgment | `eval-llm-judge` |
| Has an LLM judge and human labels, and wants to know if the judge can be trusted | `llm-align` |
| Has a support ticket, complaint or bad trace to turn into test data | `ticket-to-eval` |

## The order, for someone starting from nothing

1. `eval-rubric`: write v1 from the PRD.
2. `uig`: build a diverse set of inputs and run the agent on them.
3. The user reads the traces and writes notes.
4. `trace-codes`: cluster the notes into codes, then `eval-rubric` again for v2.
5. `eval-code` and `eval-llm-judge`: one scorer per rubric line worth automating.
6. The user labels a sample pass or fail.
7. `llm-align`: measure each judge against those labels and fix it.
8. `ticket-to-eval`: keep the dataset growing from real feedback.

## Two steps stay with a person

Reading and annotating traces (step 3) and labeling for calibration (step 6) are done by the
user. Do not do them on the user's behalf, and do not treat your own judgment as a label. If the
user asks to skip either one, explain what the later steps lose: codes that reflect the model's
guess about quality, and judges nobody has checked.

When in doubt about which row fits, ask one question instead of guessing.
