# Ch 10: User Monitoring

**Offline evals test what you know to look for. Online monitoring reveals what you didn't anticipate.**

Once your agent is live, the real diversity of user inputs will always exceed your reference dataset. New failure modes emerge, user behavior shifts, and the gap between offline scores and real-world experience grows unless you actively measure it. A team that only runs offline evals is flying with a pre-flight checklist but no cockpit instruments.

This module covers how to set up continuous monitoring, what to measure, how to detect the moment your offline metrics stop reflecting reality, and how to feed production signals back into the flywheel.

> *Diagram idea: diagram — the offline-online gap: offline evals (controlled dataset, known edge cases) vs. online monitoring (production traffic, unknown unknowns, real user diversity)*

#### **The core concept**

Online evals run your automated evaluators against a sample of live production traces.

**You don't evaluate everything.** You sample 1 to 10% of traffic depending on volume and cost. Results are aggregated into dashboards that track quality metrics over time.

> *Diagram idea: diagram — online monitoring architecture: Production traces → Sampler → Eval pipeline (code evals + LLM judges) → Dashboard + Alerting*

The conceptual shift is this: offline evals answer "does this version meet our quality bar before we ship it?" Online evals answer "is the product meeting our quality bar right now, with real users?" Both questions matter. They measure different things.

#### **What to score**

**Run the same evals you use offline against production traces.** The code evals from module 6 (category label, schema validation, hallucination guard) and the LLM judges from module 7 (empathy, actionability, factual grounding) should produce comparable scores in production. If they don't, that's a problem in itself.

**Add production-specific signals that don't exist in offline testing.** Latency distributions under real load. Error rates and timeouts. Token usage and cost-per-interaction. These operational metrics affect user experience even when quality scores are high. A response that takes 40 seconds to arrive may score perfectly on every eval and still frustrate the user in a real-time use case.

**Track user-level signals.** Thumbs up/down ratings (with the caveats about their limitations). User edits to agent outputs before accepting them. Retry rates (the user asked the same question again, which usually means the first answer was unsatisfactory). Session length and abandonment. Support ticket volume correlated with agent interactions.

None of these signals is reliable in isolation. Together, they form a composite picture of whether users are satisfied.

### Sampling Strategies for Production

#### **How to sample**

> *Diagram idea: diagram — four sampling strategies with trade-offs based on below*

Random sampling for baseline quality measurement. This is your ground truth for "how is the product doing overall." Random samples are unbiased by definition, so the pass rates you compute on them are representative of the full traffic distribution.

Stratified sampling by user segment, intent type, or product feature to ensure coverage. If 3% of your traffic comes from enterprise accounts, random sampling at 5% will barely capture them. Stratified sampling ensures you see enough from each segment to compute meaningful pass rates.

Failure-biased sampling using existing eval scores, confidence signals, or user feedback to surface likely problems faster. If a code eval flags a trace as failing, always run the LLM judges on it too. If a user gave a thumbs-down, that trace goes into the evaluation queue.

Combination approach: random sample for aggregate metrics plus failure-biased sample for debugging. The random sample tells you the overall quality level. The failure-biased sample tells you what's going wrong and where.

#### **How much to sample**

Cost determines the ceiling. LLM judge calls on every trace are expensive at scale.

**Code evals are cheap. Run them on 100% of traffic if possible.** They're deterministic, fast, and the compute cost is negligible. There's no reason to sample for code evals unless your traffic volume makes even microsecond-per-trace checks infeasible.

**LLM judges: sample 1 to 5% for high-traffic products, up to 10% for lower-traffic products or high-stakes domains.** The sampling rate should be high enough that your weekly sample produces at least 50 to 100 evaluated traces. Below that, you can't compute reliable pass rates or detect trends.

**Always run LLM judges on traces flagged by code eval failures or user complaints.** These traces are the most likely to contain quality issues, and evaluating them is the highest-ROI use of your judge inference budget.

## Detecting Drift: When Offline and Online Diverge

**Eval drift is when your offline eval scores say quality is improving but production experience is getting worse.** Your dashboard shows 92% pass rate on the reference dataset. Users are filing more support tickets. Something is off.

The causes are predictable: your reference dataset no longer reflects real-world input distribution. New user segments have different needs. User language and expectations have shifted. Seasonal patterns changed the traffic mix. The agent is being used for workflows you didn't design for.

#### **The three drift signals**

> *Diagram idea: diagram — drift detection showing offline vs. online pass rates diverging over time, with annotation of when to investigate*

**Signal 1: Score divergence.** Offline pass rate is 90% but online pass rate on the same evals is 72%. The gap means your reference dataset doesn't represent production. The traces users are sending differ meaningfully from the traces in your test set.

**Signal 2: New failure modes.** Online traces reveal error patterns that don't exist in your reference dataset. You have coverage gaps. The agent is encountering input types, workflows, or edge cases your evals were never designed to measure.

**Signal 3: User feedback contradiction.** Online eval scores are high but user satisfaction metrics (thumbs-down rates, support tickets, churn) are rising. This is the most insidious signal because it means you're measuring the wrong thing. The evals pass, but users aren't happy. Your eval criteria need updating.

#### **Responding to drift**

**For score divergence:** Add production traces to the reference dataset. Re-balance the dataset to reflect the actual distribution of inputs in production. This is the dataset refresh process from module 8.

**For new failure modes:** Run a fresh trace analysis cycle (module 4). Create new trace codes for the patterns you discovered. Build new evals for the failure modes that matter. This is the flywheel in action: production signals drive eval expansion.

**For user feedback contradiction:** Your eval criteria need updating. Go back to trace analysis. What are users unhappy about that your evals don't measure? This often reveals subjective quality dimensions (clarity, brevity, specificity) that the team assumed were covered but weren't. Build new LLM judges for the missing criteria.

## Building the User Feedback Loop

Simple thumbs up/down is biased. Users who are mostly satisfied might not click thumbs up. Users who are very dissatisfied might not click thumbs down. The result is a skewed signal that can be useful as a trend but not as a reliable metric.

**Better signals exist.**

Support ticket themes tied to agent interactions reveal systemic quality issues. User edits to agent outputs before accepting them show where the agent is close but not quite right (these edited outputs become golden examples). Session replays showing heavy editing or multiple retries indicate frustration without explicit feedback. Explicit in-context prompts ("Is this category correct?") collect targeted feedback at the moment the user can evaluate it.

**Best practice: combine multiple feedback channels into a composite signal.**

No single channel is reliable. Together, thumbs-down rate plus edit rate plus retry rate plus support ticket correlation gives you a composite picture that's much more trustworthy than any individual metric.

#### **From feedback to dataset**

The feedback loop closes when production signals flow back into the reference dataset.

**When a support ticket reveals a new failure mode,** add that query and the corrected output to your reference dataset. One support ticket is an anecdote. Five support tickets about the same failure pattern is a trace code.

**When users consistently edit a specific type of output,** those edited outputs become golden examples. The user is showing you what "good" looks like for that input type. Capture it.

**When online monitoring flags a regression,** pull the failing traces, label them, and add them to the dataset. The regression becomes a regression test: if a future change re-introduces the failure, the eval will catch it.

> *Diagram idea: diagram — the complete flywheel loop: Production → Monitor → Detect drift → Trace analysis → Update dataset → Improve agent → Deploy → Monitor*

**This is the flywheel closing.** Production experience generates new labeled data. Better labeled data enables better evals. Better evals drive better improvements. Better improvements produce better production experience. The Introduction to this course described the AI Product Flywheel. Online monitoring is how you spin it.

### Setting Up Alerting and Thresholds

#### **What to alert on**

> *Diagram idea: diagram — alerting thresholds for key metrics based on below*

Not every metric needs an alert. Alert on the signals that require immediate investigation.

  - **Code eval pass rate** drops below threshold. As an example from our support triage agent, if category accuracy falls below 85%, alerts are needed.
  - **LLM judge pass rate** drops more than 10 points from trailing average. A sudden drop in the empathy or actionability judge signals a regression or a distribution shift.
  - **Latency P95 exceeds SLA.** If the 95th percentile response time crosses 2 seconds, the user experience is degrading even if quality scores are fine.
  - **User complaint rate spikes** (3x baseline). A sudden increase in thumbs-down, support tickets, or retry rate means something broke that your evals might not be catching.
  - **Refusals or "I don't know" rate** goes above 30% or below 5%. Too many refusals means the agent is being too conservative. Too few means it's overconfident and likely generating unreliable outputs (from the module 3 confidence framework).

#### **Alert hygiene**

**Set thresholds before you launch, not after the first alert fires.** The decision about what constitutes a problem should be made when you're thinking clearly about quality standards, not when you're reacting to a number you just saw.

**Use trailing averages (7-day rolling) to avoid false alarms from daily noise.** A single bad day in a small sample can trigger an alert that doesn't represent a real trend. Rolling averages smooth out the noise and alert only on sustained shifts.

**Every alert should have a documented response procedure.** Who investigates? What do they look at first? When does it escalate? An alert without a response procedure is just noise that trains your team to ignore alerts.

### Case Study: Online Monitoring for the Support Triage Agent

Below is a hypothetical scenario for what monitoring our support triage agent might look like within a team:

**Setup:** **5% random sample scored by all code evals plus two LLM judges.** Code evals run on 100% of traffic. Alerts configured for category accuracy below 85%, empathy judge below 75%, and P95 latency above 2 seconds.

**Week 1:** **Online category accuracy is 89% (offline baseline was 92%).** The gap is expected: production has more diverse inputs than the reference dataset. Empathy judge online: 81%, consistent with offline. No alerts.

**Week 3:** **A new ticket type emerges:** API integration issues from a recently launched developer platform. These tickets don't map to any of the three existing categories (Technical, Billing, Feature Request). Category accuracy drops to 81% on this segment while other segments remain stable.

**The action needed:** The team runs trace analysis on 30 API-related tickets. A new trace code is created. 15 examples are added to the reference dataset. The prompt is updated with an "API Integration" category. Offline evals are re-run with the updated dataset to establish a new baseline. The updated agent is shipped.

**Week 5:** **Online accuracy recovers to 90% overall,** **85% on API tickets specifically.** The team continues monitoring the new category to ensure stability and adds 10 more production traces per week to build out the API-specific slice of the dataset.

The ideal elapsed time from detection to fix should be less than 10 days. Without online monitoring, this failure would have been invisible until enough developers filed support tickets to trigger a manual investigation.

## Recap and Further Learning

### Key takeaways and definitions

  - **Offline evals test what you know. Online monitoring reveals what you don't.** Both are required for a complete quality system. Offline evals are the pre-flight checklist. Online monitoring is the cockpit instruments.

  - **Sample strategically.** Use random sampling for aggregate metrics and failure-biased sampling for debugging. Run code evals on all traffic. Limit LLM judges to 1 to 10% of traffic, but always evaluate traces flagged by code eval failures or user complaints.

  - **Detect drift early.** When offline and online scores diverge, your dataset needs refreshing. When new failure modes appear, your evals need expanding. When user feedback contradicts eval scores, your criteria need updating.

  - **Close the loop.** Every production insight should flow back into the reference dataset, the eval suite, and the agent. This is the flywheel. Production experience generates labeled data, which enables better evals, which drive better improvements.

  - **Alert on what matters.** Set thresholds before launch. Use rolling averages. Every alert needs a documented response procedure.

**Online evaluation** **
**Running automated evaluators (code-based and LLM judges) against a sample of live production traces to continuously monitor quality in the wild.

**Eval drift**
The divergence between offline evaluation scores and real-world production quality, caused by dataset staleness, new user segments, or misaligned evaluation criteria.

**Composite North Star**
A quality metric that combines multiple feedback channels (thumbs up/down, support tickets, user edits, session behavior) to approximate true user satisfaction more reliably than any single signal.

**Failure-biased sampling**
A sampling strategy that prioritizes traces likely to contain quality issues (flagged by code evals, low confidence, user complaints) for LLM judge evaluation, maximizing the return on inference spend.

In the next chapter, we will learn how to evaluate complex, multi-step agentic systems where quality breaks at the routing, skill, and full-path levels.
