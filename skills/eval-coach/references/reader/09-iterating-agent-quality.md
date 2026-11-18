# Ch 9: Iterating to improve Agent Quality

You have code evals, LLM judges, a reference dataset, and calibrated reliability metrics. The infrastructure exists. Now what?

**Evals don't improve your product. Experiments do.**

Evals just tell you whether the experiment worked. This module teaches the iteration loop:

  - how to turn eval results into targeted improvements
  - how to run experiments that produce clear signal, and
  - how to decide between prompt changes, model swaps, and architectural fixes to get to the quality you need

The core principle is simple: diagnose the failure, form a hypothesis, make one change, measure the result, and ship or revert. Teams that iterate systematically outperform teams that make ad hoc changes and hope for the best, because every cycle produces either an improvement or knowledge about what doesn't work.

> *Diagram idea: diagram — the eval-driven improvement loop: Diagnose → Hypothesize → Experiment → Measure → Ship or iterate*

### From Eval Results to Diagnosis

When understanding your eval results, start with aggregate pass rates across your eval suite. Compare each eval for the new agent version to your baseline (the current production version).

> *Diagram idea: diagram — example eval dashboard showing pass rates across multiple evals with baseline comparison*

**First, identify which evals are failing most.** These are your highest-leverage improvement targets. An eval at 72% pass rate has more room for improvement than one at 94%, and the traces it's catching are the ones users are most likely to encounter.

**Second, look at failure distribution.** Are failures concentrated on specific input types, trace codes, or user segments? If 80% of category label failures come from multi-issue support tickets, you don't have a general category problem. You have a multi-issue handling problem. That's a precise diagnostic that maps to a targeted fix.

**Check cross-eval correlation.** When the empathy judge and the actionability judge both fail on the same traces, that usually signals a single root cause (the agent is producing terse, minimal responses), not two independent problems. Fix that root cause first.

#### **The diagnostic questions**

For each failing eval, ask three questions. The answer determines which lever to pull.

> *Diagram idea: diagram — diagnostic decision tree mapping eval failures to intervention types based on below*

**Is this a specification gap?** Did the prompt never address this scenario? If the agent mishandles API integration tickets because the prompt doesn't mention them, that's not a model failure necessarily. The instructions are incomplete. Fix the prompt.

**Is this an architectural gap?** Does the system lack the capability it needs? If the agent hallucinates ticket IDs because it doesn't have access to the ticket database, no prompt change will fix that. The system needs a new tool or data source.

**Is this a generalization failure?** Does the agent handle this scenario sometimes but not consistently? If the empathy judge passes on 70% of billing tickets but fails on 30% with similar characteristics, the agent knows what to do but doesn't do it reliably. This calls for prompt tuning, harness engineering, better few-shot examples, or as a last resort, a model upgrade.

**Review 10 specific failing traces and their reasoning strings.** The pattern in the failures tells you what to fix. Abstract pass rates point you to the problem. Concrete trace-level reading tells you why it's happening.

## Three Levers for AI Improvement

> *Diagram idea: diagram — cost vs. speed of three levers: Prompt (fast/cheap) → Model (medium/medium) → Architecture (slow/expensive)*

#### **Lever 1: Prompt engineering**

This is the fastest, cheapest intervention. Most early-stage improvements come from prompt changes.

**Common prompt fixes include:**

  - Adding explicit instructions for failure modes the prompt didn't address
  - Adding few-shot examples from the golden dataset for underperforming scenarios
  - Restructuring the prompt for clarity (system instructions, examples, constraints, output format)
  - Adding "I don't know" or fallback instructions for edge cases
  - Tightening output format constraints (exact labels, required fields)

**The experiment:** Make one prompt change at a time. Re-run the full eval suite. Compare to baseline. If the target eval improved and no other eval regressed more than 2 percentage points, the change is a candidate for shipping.

**The pitfall:** Don't change three things at once. You won't know which one helped. If you added two few-shot examples and restructured the system instructions simultaneously and the pass rate improved by 8 points, you have an improvement but no understanding of why. The next time a similar problem appears, you'll be guessing again.

#### **Lever 2: Model upgrades**

**When a new model is released, run your eval suite against it immediately.** The eval suite is your "model readiness test." If pass rates hold or improve across all evals, you can ship the upgrade within 24 to 48 hours. Without evals, a model upgrade is weeks of manual testing and uncertainty.

**What to watch for:** Some evals may improve while others regress. A new model may be better at reasoning but worse at following strict format constraints. Read the failing traces before deciding. A model that's better on 4 out of 5 evals but introduces a new category of failure on the fifth isn't necessarily an upgrade.

**Cost and latency also change.** A more capable model that doubles response latency may not be the right trade-off for a real-time triage agent. Run the latency SLA eval alongside the quality evals. The decision isn't "is this model better?" but **"is this model better on the dimensions that matter, at a cost and latency we can accept?"**

#### **Lever 3: Architectural changes**

This is sometimes an expensive intervention, but necessary. Examples: adding a retrieval step (with RAG or filesearch), connecting a new tool or API, splitting a single agent into specialized sub-agents, adding a pre-processing step, or changing the orchestration flow.

**Architectural changes should be preceded by clear evidence that the current architecture can't solve the problem.** "The agent hallucinates ticket IDs because it doesn't have access to the ticket database" is an architectural diagnosis. "The agent sometimes gets the category wrong" is not. The second is a prompt problem until you've exhausted those levers.

**After architectural changes, re-baseline all evals.** The new architecture may change the failure distribution entirely. Pass rates from the old architecture are no longer meaningful comparisons. Run the full eval suite on the new architecture, establish new baselines, and iterate from there.

### Running Experiments Systematically

Every change you make to the agent is an experiment. Document it. Your coding agents will get a lot of leverage out of this documentation as they give you eval leverage in the future.

> *Diagram idea: diagram — experiment log template with columns: Experiment ID, Date, Change Description, Hypothesis, Eval Results Before → After, Decision*

#### **The experiment log**

Over time, the experiment log becomes your team's institutional knowledge about what works and what doesn't. When a new engineer asks "have we tried adding few-shot examples for multi-issue tickets?" you can point to Experiment \#14, which tried exactly that and improved category accuracy by 12 points. When the PM asks "why don't we use the newer model?" you can point to Experiment \#22, which showed a 3x latency increase that violated the SLA.

#### **A/B comparison methodology**

For every experiment, compare the new version against the current production baseline on the **same reference dataset****.** This is non-negotiable. Comparing results across different datasets, or comparing to a baseline you set three months ago on a dataset that's been updated since, produces numbers that aren't comparable.

**Report pass rate changes per eval, not just aggregate.** "Category label accuracy improved 78% → 91%, but empathy judge dropped 88% → 72%" is actionable. "Overall quality improved" is not. Per-eval reporting tells you whether the change helped where it was supposed to and whether it introduced regressions elsewhere.

**For close calls (2 to 3 percentage point improvement), check for noise.** Increase dataset size or re-run the experiment to confirm the change is real. On a 50-trace dataset, a 2% improvement is a single trace flipping from fail to pass. That might be noise. On a 200-trace dataset, a 2% improvement is 4 traces, which is more likely to be a signal.

#### **When to ship, when to iterate**

**Ship** **when all evals meet their thresholds** and no eval has regressed more than 2% from baseline. Document the results in the experiment log and update the baseline.

**Iterate** **when the target eval improved** but other evals regressed. Don't ship a trade-off without understanding it. Investigate the regression. Often a prompt change that improves one quality dimension suppresses another, and a small adjustment can recover both.

**Revert** **when the change made things worse** or had no measurable impact. Don't ship on vibes. A change that felt like it should help but didn't produce measurable improvement is not an improvement. Revert, update the experiment log with what you learned, and try a different approach.

## The Role of the PM in the Iteration Loop

#### **You set the priority, engineers execute the fix**

**Great PMs always own prioritization** - the "what to fix next" decision based on eval data and user impact. Engineers own the "how to fix it" (the actual prompt change, model integration, or architecture work).

**Collaborative review works best.** PMs read the failing traces and reasoning strings, bringing product context ("this failure pattern maps to our highest-volume ticket category"). Engineers read the technical logs and system behavior ("the model is losing context after the third tool call"). Together you diagnose root causes faster than either can alone.

The PM's unique contribution to the iteration loop is this prioritization. Not every failing eval needs immediate attention. The PM decides which failure modes matter most based on user impact, frequency, and business risk. An empathy failure on 3% of tickets may be less urgent than a category routing failure on 15% of tickets, even if the empathy judge's pass rate is lower.

#### **When to update the PRD**

As you iterate, new failure modes are discovered and old ones are resolved. The AI PRD from module 3 should evolve with every iteration cycle.

**Update the PRD with:** **revised eval thresholds** (if you've raised or lowered the bar), new trace codes discovered during iteration, updated golden outputs that reflect the current quality standard, and new edge case examples from production.

**The PRD is a living document.** A PRD that hasn't been updated in two months while the team has run 15 experiments is out of sync with reality. The experiments produced knowledge. Capture it. Your coding agents can finally make your teams as systematic as you always wanted to be - this rigor no longer adds “overhead” to the process.

#### **When to update the dataset**

Every iteration cycle should produce new labeled examples for the dataset as we covered in module 8.

**Failing traces that expose new patterns should be added to the reference dataset.** They expand the coverage of input types your evals can measure. Without this, you'll keep discovering the same failure modes because your evals never learn to test for them.

**Traces that the fix resolved should stay in the dataset as regression tests.** The next prompt change might re-introduce the failure. Keeping the trace ensures you'll catch it.

### Case Study: Improving the Support Triage Agent

Below is a hypothetical journey for how a team might iterate on improving an agent

> *Diagram idea: diagram — eval pass rates over four iterations showing improvement trajectory based on below*

**Starting point:** Consider this baseline - offline evals show 78% category accuracy, 65% empathy judge pass rate, 100% latency compliance.

**Iteration 1 (Prompt fix): Let’s add sarcasm handling.** **
**Trace analysis revealed that sarcastic tickets ("Oh great, another billing error, just what I needed") were being misclassified as positive sentiment. Five sarcasm examples were added to the few-shot section. Result: empathy judge jumped to 79%. Category accuracy unchanged. Ship.

**Iteration 2 (Prompt fix): Let’s add multi-issue handling.**
Category accuracy was stuck at 78% because multi-issue tickets (containing both a billing question and a feature request) confused the agent. Explicit instructions were added: "If a ticket contains multiple issues, classify by the primary issue the customer is asking you to resolve." Result: category accuracy improved to 86% on multi-issue tickets, 82% overall. Ship.

**Iteration 3 (Model upgrade): Let’s try the new model release.** **
**A new model version was released. The full eval suite was run against it. Results: category accuracy 91%, empathy judge 84%, latency still compliant. All evals improved, no regressions. Shipped within 48 hours. Total testing time: 2 hours (running the eval suite and reading 10 failing traces).

**Iteration 4 (Architecture): Add Jira API for known-bug matching.** **
**Trace analysis revealed that 12% of technical tickets were about known bugs already tracked in Jira, but the agent couldn't check. A Jira API tool was added to the agent's toolkit. A new eval was created: "known bug detection rate." First measurement: 72%. The team continues iterating on the tool call prompt to improve retrieval accuracy.

Total elapsed time: 3 weeks. Four experiments.

  - Category accuracy from 78% to 91%.
  - Empathy from 65% to 84%.
  - One architectural expansion in progress.

Each experiment was documented in the log, each result was measured against the same reference dataset, and each decision (ship/iterate/revert) was made on data.

## Recap and Further Learning

### Key takeaways and definitions

  - Evals don't improve products, experiments do. Evals tell you whether the experiment worked. The iteration loop is: diagnose, hypothesize, change one thing, measure, ship or revert.

  - Diagnose before fixing. Read failing traces and reasoning strings to determine if the problem is specification, architecture, or generalization. The diagnosis determines which lever to pull.

  - One change at a time. Make a single change per experiment so you know what caused the improvement or regression. Multiple simultaneous changes produce improvements you can't understand or reproduce.

  - Log everything. Maintain an experiment log with hypotheses, changes, and results. This becomes your team's institutional knowledge about what works for your specific product.

  - Update the system. After each iteration cycle, update the PRD with new thresholds and edge cases, add failing traces to the dataset, and keep the golden outputs current. The iteration loop improves the agent and the eval infrastructure simultaneously.

**Experiment Log** **
**A documented record of every change made to the agent, including the hypothesis, the specific modification, eval results before and after, and the ship/iterate/revert decision.

**Regression** **
**A decline in pass rate on a previously passing eval, introduced by a new change. Regressions must be investigated before shipping.

In the next chapter, we will learn how to extend evaluation to live production traffic: monitoring real user experience, detecting drift, and closing the loop on the AI Flywheel.
