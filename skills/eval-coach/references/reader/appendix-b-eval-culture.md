# Appendix: Building an eval culture

## Three Shifts That Have to Happen Before the Tools Matter

You can have calibrated LLM judges, a clean reference dataset, and a well-structured release gate — and still ship regressions because the team argues by intuition in product reviews. The eval infrastructure doesn't work if the culture around it doesn't change. Three specific shifts separate teams that get compounding value from their evals from teams that treat them as a compliance exercise.

> *Diagram idea: Three cultural shifts as a progression — from opinion-driven to metric-driven, from post-launch to pre-build, from PM-owned to team-owned quality*

**Shift 1: Stop debating, start measuring.** The symptom is product review meetings that dissolve into "I think this is good enough" vs. "I think it needs more work," with the outcome determined by whoever argues most persistently. The fix is a forcing function: in every product review, show the current pass rate, show the threshold you agreed to in advance, and make the decision from that. "We're at 73% on the actionability judge, threshold is 80%, so we iterate or we re-examine the threshold and document why." After three or four meetings where data drives the decision, the pattern shifts. People start bringing metrics to the meeting instead of opinions.

When you're tempted to say "this feels off," convert it. "This feels off" becomes "47% of outputs are missing a concrete next step on escalation tickets." Now you have something measurable, and something that can be fixed.

**Shift 2: Evals start in prototyping, not post-launch.** The old pattern: build the feature, launch to beta, react to complaints, discover quality issues after users have already formed an opinion. The new pattern: run 20–30 representative queries before writing the PRD, define what good looks like before building, run offline evals during development, and ship knowing the quality is validated rather than hoping it is.

The mechanism that makes this stick is a pre-PRD requirement. Before a feature spec gets written, someone on the team runs representative traces and labels them. Without that, the PRD has no quality criteria and the evals have no baseline. When a PM comes to you with a spec that doesn't define what "good" looks like, send it back with the ask: "Run 30 test queries, label them, come back with pass/fail criteria." It feels like friction at first. After one launch where offline evals caught a regression before beta users saw it, the team becomes believers.

**Shift 3: Quality belongs to the whole team, not the PM.** When quality criteria live in one person's head, the eval suite is only as reliable as that person's attention. The alternative is collaborative trace labeling: PM, engineers, designer, and at least one domain expert independently label the same set of 20 traces, then meet to discuss the disagreements. Engineers catch technical fragility that PMs miss. Designers catch UX issues engineers don't notice. Domain experts catch factual errors that everyone else assumes are correct.

The disagreements are the valuable part. "Why did you mark this as Pass when I marked it Fail?" is a better product definition session than most PRD reviews. After 2–3 labeling sessions, quality becomes a shared language with documented criteria instead of implicit taste. The "silent labeling" approach — everyone labels independently and submits before seeing anyone else's results — prevents the loudest voice from anchoring everyone else. One team improved label agreement from 65% to 92% across three sessions just by enforcing independence before discussion.

## A 30-Day Plan for Teams Starting From Zero

Most teams don't fail at evals because the technical infrastructure is too hard. They fail because they try to build everything at once — a complete reference dataset, a suite of LLM judges, a calibrated release gate — before they have enough signal to make good decisions about any of it. This plan sequences the work to build momentum without getting stuck.

> *Diagram idea: Four-week timeline with deliverables per week — Week 1: baseline, Week 2: dataset, Week 3: first evals, Week 4: first improvement shipped*

**Week 1: Establish your baseline.** Before you change anything, measure where you are. Run 50–100 representative queries through your current production agent and label each output: acceptable, needs minor edits, or unacceptable. Don't optimize the labeling rubric yet — the goal is a raw baseline that tells you what the current distribution actually looks like. Track your task success rate (outputs accepted without significant revision) and identify the two or three failure categories that appear most frequently. At the end of the week, you should know your current quality level and have a clear picture of what's breaking most often.

**Week 2: Build a minimal reference dataset.** Take the 50–100 labeled outputs from Week 1 and turn them into a reference dataset. Expand to at least 30 examples that cover diverse scenarios — different ticket types, edge cases, the failure patterns you identified. Label each output explicitly with Pass or Fail and the category it represents. The goal is not a comprehensive dataset; it's a representative one that lets you measure whether a change made things better or worse. A 30-example dataset that reflects the real failure distribution is more valuable than a 300-example dataset that oversamples easy cases.

**Week 3: Write your first three evals.** Two code-based, one LLM judge. Start with the two failure categories from Week 1 that can be expressed as deterministic checks — format compliance, required field presence, response length bounds. Write them as Python functions, test them against your reference dataset, and target 95%+ reliability before moving on. For the LLM judge, choose the single most important subjective quality criterion — the one that, if consistently failing, would be a release blocker. Write the judge prompt with four or five boundary examples, split your dataset into train/dev/test sets, and run initial calibration. An 80% alignment with human labels is acceptable for Week 3; 90% is the eventual target.

By end of week, all three evals run automatically on every prompt change. The team knows what "passing" means for each one and how to read the results.

**Week 4: Ship one measurable improvement.** Go back to the baseline from Week 1. Identify the highest-frequency failure pattern and fix it — a prompt addition, a few-shot example, a constraint on output format. Re-run all three evals against the reference dataset to confirm the fix holds. Document what you changed and why. Set alert thresholds in production (a 10-point drop in pass rate triggers a review). Then ship.

The goal of Week 4 is not a perfect system. It's proof that the eval-to-improvement loop works. A 10–15% improvement in task success rate on your reference dataset, shipped with confidence because you measured it before you shipped — that's the flywheel starting to turn.

After Week 4, the work becomes maintenance and expansion: refreshing the reference dataset as the product evolves, adding judges for new quality dimensions as they're identified through trace analysis, and calibrating judges against human assessments before using them as release gates. The 30-day plan doesn't finish the eval infrastructure. It makes the infrastructure real enough to build on.
