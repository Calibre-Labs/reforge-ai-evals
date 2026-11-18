# Drawing diagrams

Draw a diagram when the idea has a shape: a loop, a flow, a decision, parts of a whole, a 2×2 or
a matrix. Don't draw one for a definition or a yes/no answer. One diagram per answer at most.

## Two ways to draw

1. **In the reply (default for quick answers).** A small text diagram in a code block, at most
   about 12 lines and 72 characters wide. Boxes with `┌─┐`, arrows with `→` and `↓`. Use this in
   the terminal and for anything a learner asked in passing.
2. **As a page (for lessons, or when asked for an image or a diagram to keep or share).** Copy
   `assets/diagram-template.html` to `eval-coach-diagrams/<short-name>.html` in the learner's
   working folder, replace the placeholders and the example SVG, and open it (macOS `open`, Linux
   `xdg-open`, Windows `start`). In a desktop or web app that renders HTML or SVG directly, show it
   there instead. Tell the learner the file path.

Rules for page diagrams:

- Inline SVG only. No external images or scripts; the fonts link in the template is the only
  external request.
- Use the template's colors: navy `#172a49` for boxes and text, brass `#d4af37` for the one thing
  to notice, mid navy `#5a7ba3` for arrows and secondary labels, light blue `#9abcda` for fills,
  hairline `#dfe3ea` for dividers. Pass in navy or a muted green `#3f7d5a`, fail in a muted red
  `#b5473a`. Never colour alone: label pass and fail in words too.
- Sentence case labels, under five words a box. Write the takeaway as the caption, one sentence.
- Use the learner's own product or Mapper in the labels when you can, not abstract boxes.
- Credit the source in the footer line ("From Week 3 of the Reforge AI Evals course").

## The course's diagrams

Draw these the way the course did. Names in brackets point to where each idea is taught.

| Diagram | Shape | Content |
|---|---|---|
| Four parts of an agentic product [Week 1] | Goal → harness → result, with context and retrieval feeding the harness and systems underneath | Context: what the model sees each call. Retrieval: what gets brought in. Harness: what the loop code does. Systems: what it runs on, at what cost |
| Agent loop [Week 1] | Model ⇄ tools in a loop, a goal on top | Model, tools, loop, goal; stops when the goal is met |
| Errors compound [Week 1] | Line falling across ten steps | 95% per step → 60% after ten |
| Anatomy of an eval [Week 1, 2] | Trace + rubric line → scorer → pass or fail; many → metric | The template's example SVG |
| Four rubric groups [Week 2] | Four columns | Outcome, trajectory, governance, experience, each with its question and an example line |
| Trace analysis [Week 2] | Three steps left to right, with who does each | Build a dataset (uig, you review) → read and take notes (you) → group into codes (trace-codes, you edit) |
| User input grid [Week 2, ch 3] | Grid of two dimensions; filled and empty cells | Empty cells are the coverage gaps |
| What codes become [Week 2] | One box fanning out to four | Fixes, rubric v2 lines, more inputs, automated evals |
| Fix, check or judge [Week 3] | Decision tree of three questions | Q1 specified? no → fix the prompt. Q2 has what it needs? no → change harness or system. Q3 works only sometimes? yes → write an eval (code check if a rule works, else an LLM judge) |
| Four kinds of eval [Week 3] | Four cards | Code check, LLM judge, human review, user feedback; what each is best for |
| Confusion matrix [Week 4] | 2×2, human label on rows, judge call on columns | TP, FN, FP, TN with counts; TPR = TP/(TP+FN), TNR = TN/(TN+FP) |
| Train / dev / test [Week 4] | One bar split three ways | ~10 train (prompt examples), ~30 dev (fix disagreements), ~60 test (fresh check) |
| The eval loop [Week 4] | Cycle of four | Change one thing → re-record the same sessions → score with every scorer → compare |
| Where evals attach [Week 5] | Main agent with helpers; rubric groups pinned to each | Outcome at the end, per-helper checks, trajectory on the main agent, governance everywhere, experience at the user |
| Offline vs online [Week 5] | Two columns | When, inputs, reference answer, how many, read next to |
| Scores vs users [Week 5] | 2×2 | Pass+happy: keep. Pass+left: rubric missing something. Fail+happy: too strict. Fail+left: evals caught it, go fix |
| AI flywheel [Intro, Week 5] | Cycle of four around a north star | Traces → datasets → evals → monitoring, around agent success rate; starts from an AI PRD |
| Who does what [Week 5] | Eight steps in a row, two highlighted | The plugin does every step except reading traces and labeling, which stay with a person |

The reader chapters also mark diagrams as `> *Diagram idea: ...*`. When a learner asks about that
passage, draw that diagram.
