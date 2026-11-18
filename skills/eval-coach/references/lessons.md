# Learn mode: the lessons

Eight short lessons that walk the eval loop on Mapper, the course agent, using files already in
this repo. Each lesson runs a real skill, so by the end the learner has used every skill in the
plugin once. A lesson takes 10 to 20 minutes.

Mapper files live in the plugin's `templates/mapper/`. If the plugin was installed without
templates (some installs copy only `skills/`), point the learner to
https://github.com/Calibre-Labs/reforge-ai-evals and have them clone it, or switch to their own
product.

## How to run any lesson

1. **Why (1 minute).** Open with the lesson's question, in one or two sentences. Ask the learner to
   guess before you explain.
2. **Idea (3 minutes).** Teach the core idea in under 150 words, from the sources listed. Draw the
   lesson's diagram (see `diagrams.md`).
3. **Do.** Load the lesson's skill and run it on the Mapper files. Follow that skill's own
   workflow; don't shortcut it.
4. **Your turn.** The learner does the person's part. For lessons 3 and 6 this is the human step
   (reading and labeling): never do it for them, and never put your own judgment in as a label.
5. **Check (2 questions).** Ask the check questions one at a time. Let the learner answer first,
   then compare with the answer key, in a sentence or two. A wrong answer gets the right idea and
   one pointer to read, not a lecture.
6. **Save progress** and offer the next lesson, or the same lesson on their own product.

## Progress file

Keep progress in `eval-coach-progress.md` in the learner's working folder, so "continue" works in
a later session:

```markdown
# Eval coach progress
Role: PM | engineer | other      Own product: yes/no (name)
| Lesson | Status | Date | What they made |
|---|---|---|---|
| 1 Define good | done | 2026-11-18 | mapper-rubric-v1-mine.md |
```

## Placement

Ask two questions, together, before lesson 1: (1) what's your role, and (2) do you have an AI
product with traces you can read? Then:

- New to agents → start with lesson 0.
- Has a PRD or rubric already → start at lesson 2.
- Has traces and notes → offer lesson 4.
- Has judges but doesn't trust them → offer lesson 6.

## The lessons

### 0. How agents work (optional)
- **Question:** if each step of an agent is right 95% of the time, how often are all ten steps right?
- **Sources:** `course-sessions.md` Week 1, `faq/faq-week-1.md`, reader `00`, `01`.
- **Diagram:** the four parts of an agentic product.
- **Do:** open `templates/mapper/mapper-trace.html`; have the learner find one step in each part.
- **Check:** (a) Where does a harness bug show up, and how do you check for it? *It doesn't show in
  the final answer; check the steps in the trace.* (b) What three things make up an eval? *A trace,
  a rubric line and a scorer, giving pass or fail.*

### 1. Define good: the eval rubric
- **Question:** two coffee homepages, both "good". How do you decide which is better?
- **Sources:** Week 2, reader `02`, FAQ week 2 "Rubrics".
- **Diagram:** the four rubric groups with a Mapper line in each.
- **Do:** `eval-rubric` on `templates/mapper/mapper-prd-detailed.md`. Then compare with
  `mapper-rubric-v1.html`.
- **Your turn:** add one must-never line of their own.
- **Check:** (a) Which group does "declines investment advice" belong to? *Governance.* (b) When do
  you write v1? *From the PRD, before reading any traces.*

### 2. Build test inputs: the user input grid
- **Question:** what kind of request would a real user send that your test set doesn't have?
- **Sources:** Week 2 step 1, reader `03` (UIG section) and `07`, `docs/uig-market-map.md`.
- **Diagram:** a grid of two dimensions with filled and empty cells.
- **Do:** `uig` on Mapper's PRD and `templates/mapper/traces/sessions.json` inputs.
- **Check:** (a) How many inputs to start with? *10 to 20, growing to 50 to 80 as you find
  failures.* (b) Where do inputs come from before you have users, and after? *A UIG before; then
  production traffic, tickets, thumbs down and user corrections.*

### 3. Read traces (the human step)
- **Question:** why read traces before automating anything?
- **Sources:** Week 2 step 2, reader `03`, `13`.
- **Diagram:** trace analysis in three steps (dataset → notes → codes).
- **Do:** open `templates/mapper/traces/index.html`. The learner reads at least five traces and
  writes notes in the page, then exports the CSV. If they want a better viewer for their own
  product, offer `trace-review-app`.
- **Your turn:** the notes are theirs. You may summarize a long trace or point at a tool call. You
  may not write the notes.
- **Check:** (a) What goes in a note? *What worked, what went wrong, what should have happened; no
  verdicts or codes yet.* (b) Why start from the user's intent? *To judge the steps against what
  they were trying to do.*

### 4. Find failure modes: trace codes
- **Question:** you have 50 notes. What should you fix first?
- **Sources:** Week 2 step 3, `mapper-case.md`, FAQ week 2 "Trace codes".
- **Diagram:** codes become fixes, rubric lines, inputs and evals.
- **Do:** `trace-codes` on the exported notes; compare their codes with Mapper's TC-1 to TC-11.
  Then `eval-rubric` in v2 mode.
- **Check:** (a) What makes a code well-formed? *A short name, a yes/no definition for one trace,
  two or three examples with evidence.* (b) How do you prioritize? *Impact, frequency, evidence.*

### 5. Automate checks: fix, check or judge
- **Question:** a code shows up in half your traces. Do you write an eval?
- **Sources:** Week 3, reader `04`, `05`, `06`, FAQ week 3.
- **Diagram:** the fix / check / judge decision tree.
- **Do:** run the three questions on two Mapper codes. Then `eval-code` for TC-8 (half-empty
  columns) and `eval-llm-judge` for TC-4 (metric scope), on `templates/mapper/traces/sessions.json`.
- **Check:** (a) TC-11, investment advice, the prompt never forbade it. Fix or eval? *Prompt fix: a
  specification gap.* (b) Why binary judges? *A yes/no is easy to check against your own label;
  a 1 to 5 score is not.*

### 6. Trust the judge: alignment (the human step)
- **Question:** your judge says 37% pass. Do you believe it?
- **Sources:** Week 4, reader `08`, FAQ week 4.
- **Diagram:** the confusion matrix, then train / dev / test.
- **Your turn:** the learner labels at least 10 sessions pass or fail on the judge's criterion.
  Their labels only.
- **Do:** `llm-align` on their labels and the judge's verdicts.
- **Check:** (a) TP 7, FN 4, FP 3, TN 16: TPR and TNR? *64% and 84%.* (b) Why a separate test
  set? *Improvements on examples you studied may not carry over to fresh cases.*

### 7. Keep it growing: tickets and monitoring
- **Question:** offline scores went up, users are still unhappy. What's wrong?
- **Sources:** Week 5, reader `09`, `10`, `11`.
- **Diagram:** offline vs online, or the scores-vs-users 2×2.
- **Do:** `ticket-to-eval` on a made-up support complaint about Mapper (write one with the
  learner, e.g. "it said Oracle Health made $67B").
- **Check:** (a) What's a good agent success rate? *Outcome-based, covers every session, objective
  and per-session.* (b) Scores pass but users leave. What does that tell you? *The rubric is
  missing something; read those sessions and write a new code.*

## After the last lesson

Offer to run the same loop on their own product, starting with `eval-guide`. Point to the
Week 5 "what to do next at work" list: pick one agent, read 20 traces, write one evaluator, label
20 sessions and align it.
