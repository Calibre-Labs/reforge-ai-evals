# Ch 4: Principles of Automated Evaluation

In this module, you will learn when to automate evaluation, how to choose between code-based and LLM-judge methods, and which common mistakes make eval suites unreliable.

In Module 4, trace analysis produced a taxonomy of quality: “trace codes” that capture what makes your product's output "good" or "bad." **Now you face a different problem: manual review doesn't scale past hundreds of users.**

You can personally review perhaps 100 traces/week to understand patterns. You can't personally review 100,000 production traces to verify every output meets your quality bar. **You also don’t want to slow down new releases with extensive (and slow) human review needed for every issue previous releases have had.**

Automated evaluators are the essential mechanism that turns initial qualitative observations into a repeatable, scientific measurement of performance against stated goals. It speeds up your shipping and iteration cycle along with helping you monitor live user experiences in production.

But automation isn't easy. **Build it too early, and you waste time measuring the wrong things. Build it wrong, and you create false confidence in a system that's quietly failing.**

This chapter teaches you when to automate and how to choose the right automation method.

### Not Every Problem Needs an Eval

> *Diagram idea: diagram on generalization vs specification gap based on below*

The primary signal to move from manual review to automation is the generalization gap: the dip in performance if you go from a small set of ideal test inputs to a larger, diverse, real-world dataset.

|  |
| :-: |
| Identifying Specification vs Generalization gaps: A core distinction in AI failure modes - a Specification Gap occurs when the system fails because the original prompt or instructions were incomplete for that scenario, while a Generalization Gap is a failure where the system works inconsistently across a diverse dataset despite clear instructions. |

Not every trace category needs automation. Some issues are better addressed by first updating your prompt. Others require architectural changes to your agent harness. **Only generalization errors, where your system works sometimes but not consistently, are good candidates for automated evaluation.**

> *Diagram idea: diagram - flowchart for when to build evals*

For each trace category you identified in module 4, apply this decision framework:

**Question 1: The Specification Check:** *Was the prompt clearly supposed to handle this situation?*

  - If NO → You have a specification gap, not an eval problem
  - Action: Update the instructions in your system prompt
  - Example: Your email drafter never includes subject lines because you forgot to mention them in the prompt

**Question 2: The System Check**: *If the prompt’s clear, does the agent ever work in this scenario?*

  - If NO (never works) → You have an architectural issue
  - Action: Engineering fix required (missing integration, incorrect tool definition, model capability limitation)
  - Example: Your agent is supposed to check calendars, but the calendar API isn't actually connected

**Question 3: The Generalization Check:** *Does the system work in some scenarios but fail in others?*

  - If YES → You have a generalization error
  - Action: This is your automation candidate
  - Example: Your email drafter sometimes includes personalized context from previous messages, but only when those messages are recent and clearly related

## When and how to write Automated Evals

Good automated evaluators do three things well.

> *Diagram idea: diagram - reasons for writing automated evals*

**First, they let you ship faster.** When you can test changes against a known quality bar in minutes, debates disappear. You don’t argue whether a new prompt is better. You run it.

**Second, they keep quality from drifting.** Production traffic always finds edge cases your initial dataset missed. Automated checks are how you notice regressions before users do.

**Third, they create leverage.** Once a behavior is measurable, it becomes improvable. You can tune prompts, swap models, or change architecture without re-learning everything from scratch.

None of this requires measuring everything. It requires measuring the right things.

### Choosing the Automation Method: Code-Based vs. LLM-as-Judge

**Once you've identified a generalization gap that warrants automation, you must choose the appropriate evaluation method.** The default path should always be code-based evaluation because it's faster, cheaper, and 100% reproducible (deterministic).

> *Diagram idea: diagram - why code-based evals are more convenient based on below*

Why default to code-based over LLM-as-Judge:

  - Speed: Executes in milliseconds, not seconds
  - Cost: Free compute vs. LLM API calls
  - Determinism: Same input always produces same result (no LLM variability)
  - Critical path: Can run during request processing to auto-retry on failure
  - Debuggability: Easy to understand why an eval passed or failed

**Example: If a Python function or regex can validate the output, use code.** Only when a metric requires subjective nuance should you consider moving to the more complex LLM-as-Judge approach. **We’ll dive deeper into both in modules 6 and 7.**

However, there’s a clear boundary where deterministic checks aren’t possible to build. They can’t tell you whether an answer is actually helpful for a specific type of user. They can’t judge whether an explanation is logically consistent or sufficiently persuasive. They can’t assess brand alignment, or nuanced correctness across several criteria.

**When your trace codes depend on subjective judgment rather than strict rules - LLM-based evaluators or LLM-Judges are helpful.**

The important point here is sequencing. Exhaust simple checks first. Every subjective evaluator you build should sit on top of a foundation of deterministic ones.

### Avoiding Common Evaluation Mistakes

**Teams new to automated evaluation tend to fall into predictable traps.**

> *Diagram idea: diagram - typical mistakes made while writing evals*

1.  Automating unclear requirements. If humans can’t agree on what “passing” looks like, an eval won’t fix that. It will just encode the confusion.
2.  Reaching for complex evaluators too early. If you can describe the requirement as “must include X” or “must not violate Y,” start there.
3.  Trying to automate everything at once. One well-chosen eval that clearly improves velocity or quality is more valuable than ten half-trusted ones.

**Finally, watch for false confidence.** An eval that passes noisy or incorrect outputs is worse than no eval at all. Automation should make failures louder, not quieter.

## Effective Evaluation Practices

**Not only does evaluation quantify errors; it should also be driving real business success. A strong evaluation practice should enable three specific outcomes:**

> *Diagram idea: diagram - the 3 characteristics of effective evaluation*

### 1\. Rapid Rollout Speed

**Target: Deploy new models or major prompt changes within 24-48 hours**

A reliable offline evaluation process should allow your team to test and ship updates in days, not weeks. This speed has become a key differentiator in the competitive AI landscape. Users increasingly expect the latest model capabilities immediately upon release. If your competitor ships Opus 4.6 based features on launch day and you're still "evaluating" it three weeks later, you've lost mindshare.

Companies like Notion and Figma are great examples of this.

**How evals enable speed:**

  - Automated regression testing removes the need for manual QA cycles
  - Confidence in your quality bar allows faster decision-making
  - Quantitative comparison ("78% vs 88% task success") eliminates subjective debates

If you can't ship fast, you're either under-invested in evaluation infrastructure or over-cautious about risk. Both are solvable.

### 2\. Feedback Alignment

**Target: Real-world user feedback improves your evaluation dataset**

Simple "thumbs up/down" metrics are often biased and inaccurate. Users click thumbs up when they're satisfied with the experience (fast response, friendly tone), even if the underlying work was low-quality. They click thumbs down when they're frustrated by unrelated issues (slow loading, confusing UI), even if the AI output was perfect.

**Instead, you should integrate qualitative signals from multiple sources:**

  - Support ticket themes ("users report incorrect data in exports")
  - User comments on outputs ("this summary missed the key risk")
  - Subject matter expert review ("the legal language here is imprecise")
  - Session replay analysis (users heavily edit before accepting)

These signals feed back into your offline dataset. When a support ticket reveals a new failure mode, you add that query and the corrected output to your reference data. Now your offline evals catch that error before it reaches more users.

**This prevents "eval drift"—a failure mode where you optimize a metric that no longer reflects real-world user problems.** If your offline evals say quality is improving but support tickets are increasing, you're measuring the wrong thing.

### 3\. Playing Offense (Shipping Frontier Features)

**Target: Ship risky, innovative features by setting clear quality thresholds**

Evals shouldn't just prevent bad releases—they should enable ambitious ones. You can ship experimental "frontier" features by explicit quality thresholds for different stages (alpha, beta, GA).

For example, Braintrust, the 3P tool we use to demo eval workflows in this course, shipped their own agentic interface **as soon as their evals crossed 60% with Opus 4.5.** They had been scoring it with previous models but waiting to hit this threshold and be first to market.

Without evals, every launch decision is subjective and contentious. With evals, you have a forcing function: "We agreed 70% is the bar for beta. We're at 68%. Ship or iterate?"

**This framework allows you to take calculated risks.** A feature with 55% success rate might be unusable as a default experience but incredibly valuable as an opt-in power-user tool. Evals let you quantify the risk and make informed trade-offs.

### Starting Small, Scaling Deliberately

> *Diagram idea: diagram - how to start small with evals and why*

You don’t need all of this at once. Start with vibe checks. As patterns stabilize, add offline testing. Online monitoring becomes critical once you have production traffic.

**Teams often wait to build evaluations until they “have enough data.” In practice, evaluation is how you learn what data you need.**

Small, imperfect datasets are far more valuable than shipping blind. Leverage the user input grid methodology we shared in module 4 to create/source inputs and get started\!

## Recap and Further Learning

### Key takeaways and definitions

  - **Prioritize generalization gaps:** only automate evaluation for generalization errors. Specification gaps (prompt updates) and architectural issues (engineering fixes) are better handled first before measuring.
  - **Automate key evaluators:** these are essential for accelerating the shipping and iteration cycle, monitoring live user experiences, and preventing quality drift.
  - **Default to code-based evaluation:** choose code-based evals first for their speed, cost-efficiency, and determinism. Only use the llm-as-judge approach when a metric requires subjective nuance.
  - **Effective evaluation drives success:** a strong evaluation practice enables three outcomes: rapid rollout speed, feedback alignment, and playing offense - shipping risky, innovative features by setting clear quality thresholds.
  - **Start small:** evaluation is how you learn what data you need. Start with small, imperfect datasets using the user input grid methodology.

**Specification Gap****
**A system failure where the original prompt or instructions were incomplete for a given scenario.

**Generalization Gap****
**A system failure where the system works inconsistently across a diverse, real-world dataset despite having clear instructions.

**Code-Based Evaluation (Deterministic)**
An evaluation method that applies explicit, non-subjective rules (like a Python function or regex) to measure agent outputs, valued for speed, cost, and 100% reproducibility.

**LLM-as-Judge****
**A method using a large language model (the judge) to evaluate the subjective quality (e.g., tone, helpfulness, consistency) of another AI model’s output, typically used when deterministic checks are not possible.

In the next module, we will learn how to write deterministic, code-based evaluations that run automatically on every prompt change and never produce a false positive.
