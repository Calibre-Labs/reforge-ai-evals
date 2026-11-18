# Ch 8: Measuring Judge Alignment

**In module 7, you built LLM judges. This module is about whether you should trust them and how much.**

An LLM judge that returns Pass or Fail with a reasoning string looks authoritative. It runs at scale. It's cheap relative to human review. But an LLM judge's verdict is an opinion, not a fact, and the quality of that opinion must be measured before you use it to make shipping decisions. **The process of measuring it is called calibration: comparing the judge's verdicts against human labels, trace by trace, and quantifying where they agree and disagree.**

This module covers the mathematical framework for calibration, the step-by-step workflow for aligning a judge, and what to do when alignment can't reach the bar you need.

#### **Why calibration is the whole game**

Teams skip this step constantly. They build a judge, run it on their dataset, see a pass rate of 85%, and treat that number as if it means something. It doesn't, yet. A pass rate tells you what the judge thinks. Calibration tells you whether the judge thinks the same way your domain experts do.

**An uncalibrated judge is worse than no judge.**

An uncalibrated judge means you think you have already automated evals, but the number on your dashboard might be meaningless. Your team is now making shipping decisions on judge scores that have never been validated against human assessment. Then they're surprised when user complaints don't track with the metrics that were supposed to catch quality problems.

The calibration workflow produces two numbers:

  - how reliably the judge catches good outputs (True Positive Rate) and
  - how reliably it catches bad outputs (True Negative Rate).

**When both are high, the judge is trustworthy.** When either is low, you know exactly where to focus your iteration.

### Calibration: The Confusion Matrix Method

Imagine you test your empathy judge on 100 customer service responses:

  - **You (human)** label 70 as "Empathetic" (Pass) and 30 as "Not Empathetic" (Fail)
  - **Your judge** labels 77 as Pass and 23 as Fail

At first glance, this looks promising. The pass rates are similar (70% vs 77%). But aggregate pass rates can hide massive disagreement at the individual trace level. The judge might be passing a completely different set of traces than the ones you passed. When you compare trace-by-trace: the judge agreed with you on 60 traces and disagreed on 40.

**This means your actual agreement is 60% - just a bit better than random.**

A judge that disagrees with you 40% of the time is unreliable at scale. You need a systematic way to measure and improve this alignment. That's what the confusion matrix gives you.

#### **The Confusion Matrix**

> *Diagram idea: diagram — confusion matrix for LLM judge calibration based on table below*

A confusion matrix breaks down exactly where the judge agrees and disagrees with human judgment. **Take this example below - the same 100 traces, organized by both the human label and the judge's verdict:**

|  |  |  |  |
| :-: | :-: | :-: | :-: |
|   | \*\*Judge - PASS\*\* | \*\*Judge - FAIL\*\* | \*\*Sub-total\*\* |
| \*\*Human - PASS\*\* | 55 | 15 | 70 |
| \*\*Human - FAIL\*\* | 22 | 8 | 30 |
| \*\*Sub-total\*\* | 77 | 23 | 100 |

**Reading the matrix:**

  - **True Positives (55):** Judge said Pass, human said Pass. Agreement on quality.
  - **False Positives (22):** Judge said Pass, human said Fail. The judge let bad outputs through. This is the dangerous quadrant for production.
  - **False Negatives (15):** Judge said Fail, human said Pass. The judge rejected good outputs. This wastes engineering time investigating non-problems.
  - **True Negatives (8):** Judge said Fail, human said Fail. Agreement on failure.

Each quadrant tells a different story about how the judge fails, and therefore what to fix. A judge that's heavy on false positives is lenient: it's waving through bad outputs. A judge that's heavy on false negatives is harsh: it's flagging good work as broken. Most uncalibrated judges are lenient, because LLMs default to positive assessment unless the prompt forces them to be critical.

### Calculating Reliability Metrics

From the confusion matrix, we calculate two critical metrics:

**True Positive Rate (TPR) = Sensitivity**

TPR = True Positives / (True Positives + False Negatives)

TPR = 55 / (55 + 15) = 55 / 70 = 79%

**What it means:** When a response truly is empathetic (human says Pass), the judge correctly identifies it 79% of the time. The judge misses 21% of good responses, flagging them as failures.

**True Negative Rate (TNR) = Specificity**

TNR = True Negatives / (True Negatives + False Positives)

TNR = 8 / (8 + 22) = 8 / 30 = 27%

**What it means:** When a response truly lacks empathy (human says Fail), the judge correctly identifies it only 27% of the time. The judge incorrectly passes 73% of bad responses.

This judge has an asymmetric failure profile. It's decent at recognizing good outputs (79% TPR) but nearly useless at catching bad ones (27% TNR). In production, this means the judge would greenlight the majority of quality failures. You'd see a reassuring 77% pass rate on your dashboard while 73% of the outputs your domain experts would reject sail through undetected.

**TNR is almost always the harder metric to improve,** because LLMs are trained to be agreeable and positive. Getting a judge to reliably identify failures requires more deliberate prompt engineering than getting it to recognize successes.

## The Calibration Workflow

Calibration is not a one-time calculation. It's an iterative loop: label, run, measure, read disagreements, refine the prompt, measure again. The loop uses the train/dev/test dataset splits covered in module 8 to prevent overfitting.

> *Diagram idea: diagram — calibration workflow loop: label → run → measure → read disagreements → refine → validate*

#### **Step 1: Collect human labels**

Before you can measure alignment, you need a ground truth. Select 50 to 100 representative traces and have a domain expert label each one Pass or Fail for the specific criterion the judge evaluates. Two rules make this work:

**The labeler must apply the same criterion as the judge.** If the judge evaluates "empathetic acknowledgment before resolution," the human labels must evaluate exactly that, not "overall tone quality" or "I liked this response." Misaligned criteria between the judge and the labeler will show up as low agreement no matter how good the judge prompt is.

**Include the hard cases.** If you only label traces where the answer is obvious, you'll get artificially high agreement and no information about where the judge actually struggles. Deliberately include borderline traces where reasonable people might disagree. That's where calibration matters most.

Split the labeled set into dev (roughly one-third) and test (roughly two-thirds), following the approach from module 8. The train examples for the judge prompt should be drawn from the dev set or pulled separately. Never use test set traces to refine the judge.

#### **Step 2: Run the judge on the dev set**

Execute the judge on every trace in the dev set. Record three things for each trace: the judge's verdict (Pass/Fail), the reasoning string, and the human label. The reasoning string is what makes the next step possible.

#### **Step 3: Build the confusion matrix**

Organize the results into the four quadrants. Calculate TPR and TNR. On first calibration runs, don't be surprised by low numbers. Uncalibrated judges commonly score 60-75% TPR and 20-40% TNR. The 27% TNR in our empathy judge example is typical for a first pass, not an outlier.

#### **Step 4: Read the disagreements**

This is the most important step and the one most teams rush through. **Read every disagreement in the dev set.** For each one, the reasoning string tells you why the judge made its call. Categorize the disagreements into patterns like the 4 below:

**Criterion misunderstanding.** The judge interpreted the evaluation question differently than you intended. Example: the empathy judge treats "I'm sorry for the inconvenience" as specific acknowledgment when the human labels it as generic filler. This is a prompt clarity problem.

**Missing boundary examples.** The judge doesn't know where the line is for a specific edge case. Example: short, efficient responses to simple billing questions get flagged as lacking empathy, when a human would say the brevity is appropriate. The judge needs an example that teaches this boundary.

**Leniency bias.** The judge defaults to Pass on ambiguous cases. This is the most common source of low TNR. The judge's reasoning will often say something like "the response does address the customer's issue" while ignoring the specific criterion it was supposed to evaluate. The fix is to make the fail conditions more explicit and add examples of outputs that look superficially fine but fail the specific criterion.

**Domain knowledge gap.** The judge doesn't have enough context to evaluate the criterion. This is harder to fix with prompt engineering and may indicate a ceiling (covered later in this module).

#### **Step 5: Iterate on the prompt**

Based on the disagreement patterns, make targeted changes to the judge prompt. The key word is targeted. Don't rewrite the entire prompt after one calibration run. Change one thing at a time so you can measure the effect.

> *Diagram idea: diagram — common judge prompt fixes mapped to disagreement types based on below*

**The most effective single fix for low TNR is adding "near-miss" examples to the judge prompt.** These are traces that look like they should pass on surface inspection but fail the specific criterion. Three or four well-chosen near-miss examples typically improve TNR by 15-25 percentage points, because they teach the judge exactly what "not good enough" looks like for this criterion.

After each prompt change, re-run on the dev set and rebuild the confusion matrix. Track your metrics across iterations so you can see whether each change helped, hurt, or was neutral.

#### **Step 6: Validate on the test set**

Once you've reached your target TPR and TNR on the dev set, run the judge exactly once on the test set. This is your final validation. The test set result is the number you report and the number you use for production decisions.

**If the test set metrics are significantly lower than the dev set metrics, you've overfit to the dev set.** This usually means your prompt improvements are too specific to the particular traces in the dev set rather than generalizable. Go back, simplify the most recent changes, and re-validate.

**If the test set metrics are close to the dev set metrics (within 5 percentage points), the judge is calibrated.** Document the TPR, TNR, the final prompt, and the date. This becomes your baseline for future recalibration.

### Case Study: Calibrating the Empathy Judge

In module 7, we built the empathy judge for the Support Triage Agent: a reference-free judge that checks whether the agent opens with a specific, empathetic acknowledgment before providing a resolution. Here's what a hypothetical calibration process might have looked like in practice.

**Round 1: First calibration run**

Suppose a domain expert labeled 90 traces (30 dev, 60 test).

Dev set results:

|  |  |  |
| :-: | :-: | :-: |
|   | Judge - PASS | Judge - FAIL |
| Human - PASS | 16 | 5 |
| Human - FAIL | 7 | 2 |

**TPR: 76%. TNR: 22%.**

The judge was catching most good responses but barely identifying any bad ones. Reading the 7 false positives revealed a clear pattern: the judge was treating any mention of the customer's issue as "acknowledgment," even when the response immediately pivoted to procedural steps with no emotional framing. "I see you were charged twice. Please follow these steps..." was getting a Pass.

**Round 2: Added near-miss examples**

Three false-positive traces from the dev set were added to the judge prompt as explicit Fail examples, with explanations: "This response references the issue but provides no empathetic framing. Acknowledging the fact is not the same as acknowledging the frustration."

Dev set results:

|  |  |  |
| :-: | :-: | :-: |
|   | Judge - PASS | Judge - FAIL |
| Human - PASS | 18 | 3 |
| Human - FAIL | 3 | 6 |

**TPR: 86%. TNR: 67%.**

Significant improvement. TNR jumped from 22% to 67%. The near-miss examples taught the judge the distinction between factual acknowledgment and empathetic acknowledgment. But 67% TNR still means one-third of genuinely bad outputs get through.

**Round 3: Strengthened fail criteria**

The judge prompt was updated to make the fail conditions more granular: "A response that acknowledges the problem factually but does not acknowledge the customer's experience or emotional state is a Fail. Phrases like 'I see that...' or 'It appears that...' followed immediately by resolution steps, with no expression of concern, understanding, or urgency, constitute a Fail."

Dev set results:

|  |  |  |
| :-: | :-: | :-: |
|   | Judge - PASS | Judge - FAIL |
| Human - PASS | 19 | 2 |
| Human - FAIL | 1 | 8 |

**TPR: 90%. TNR: 89%.**

Both metrics are now at or near the 90% target. The remaining 2 false negatives were borderline cases where the human labeler and the judge reasonably disagreed. The 1 false positive was a response that used empathetic language but in a formulaic way the human considered inauthentic, which is a genuinely hard call.

**Test set validation:**

Running the calibrated judge on the 60-trace test set produced TPR of 88% and TNR of 85%. Slightly below the dev set results, as expected, but within a reasonable margin. The judge was deployed to the eval pipeline.

Total effort: three iterations over two days, primarily spent reading disagreement reasoning strings and selecting the right near-miss examples.

#### **Interpreting and Using Calibration Results**

The reliability tier determines how to use the judge in your release workflow.

**A judge with TPR = 92% and TNR = 88% is reliable enough** for automated release gating. It catches most quality issues and doesn't false-alarm too often. Use it as a hard gate: if the pass rate on the test set drops below your threshold after a prompt change, the change does not ship.

**A judge with TPR = 95% and TNR = 65% will approve too many bad outputs.** Use it as a monitoring signal, not a release gate. Pair it with periodic human review on a sample of the traces it passes.

**A judge with TPR = 70% and TNR = 90% will be too conservative, blocking good work** and creating investigation overhead. It may slow your team down more than it helps. Consider loosening the judge's criteria or splitting it into two narrower judges where each can achieve balanced reliability.

#### **Tracking judge reliability over time**

**Judge alignment can drift as the product evolves and the user distribution shifts.** A judge calibrated on billing tickets from B2C users (the example from module 7) will lose reliability when the agent starts handling developer integration questions.

**Schedule quarterly re-calibration.** Label 50 fresh production traces, run the judge, rebuild the confusion matrix. Compare the new TPR and TNR against the baseline you set when the judge was first deployed.

## When LLM Judges Hit Their Ceiling

Most quality criteria in enterprise AI products can be turned into calibrated LLM judges with enough work on the prompt and example set. A few can't, and recognizing when you've hit that ceiling matters as much as the calibration work itself.

**Judges hit their ceiling when no existing model can reliably assess the quality dimension you care about.**

This shows up as TPR/TNR that won't break through 80% despite prompt iteration, or as judge reasoning strings that reveal the model doesn't have the domain knowledge to distinguish good from bad in your specific context. A judge evaluating advanced medical diagnosis, legal precedent analysis, or cutting-edge code generation against unreleased libraries is likely in this category.

**Three signals that you've hit the ceiling, not a prompt problem:**

1.  **The reasoning strings show genuine confusion, not misapplied criteria.** If the judge is failing because it interprets the criterion differently than you intended, that's fixable. If it's failing because it literally can't assess whether a legal citation is relevant or whether a medical recommendation is clinically sound, no prompt will fix that.

2.  **Adding more examples stops improving metrics.** In a typical calibration loop, each round of near-miss examples and prompt refinement produces a measurable jump in TPR or TNR. When successive rounds produce less than 2-3 percentage points of improvement, you've likely extracted most of what the model can give you.

3.  **Inter-annotator agreement among humans is also low.** If your human labelers disagree on 20%+ of traces for this criterion, the criterion itself may be too ambiguous for anyone, human or model, to evaluate consistently. Tighten the criterion definition before concluding the judge has failed.

> *Diagram idea: diagram — decision tree for when a judge hits its ceiling based on below*

**When automation can't reach the quality bar, the answer is structured human review, not abandonment of measurement.**

The difference is how you structure it.

**Focus human effort where automation fails most.** Use code-based evals for structure and safety. Use LLM judges for the quality dimensions where calibration works. Reserve human review for the final quality gate on dimensions where calibration fails, and for periodic ground-truth validation of the judges that are running in production.

**Don't review everything.** Sample 5-10% of production traffic with a stratified approach: include both the best and worst outputs by automated score, and ensure the sample covers all major output types. Reviewing only low-scoring outputs creates blind spots about how the agent performs when it's working well.

**Build human review thresholds into the release gate alongside automated ones.**

If an output type requires human review before release because no judge can reliably evaluate it, specify that in the release workflow explicitly, with a minimum sample size and a documented rubric.

"A human reviewed it and it seemed fine" is not a threshold. "3 domain reviewers assessed 20 outputs and 90% met the quality criteria" is.

**The goal is to keep moving.**

Human review as a permanent fallback for a quality dimension is a signal to invest in a better judge or a simpler criterion, not to accept indefinite manual review overhead. Most teams that do this well cycle back to the judge after three or four product iterations and find they can calibrate it now that the output distribution has stabilized.

## Recap and Further Learning

### Key takeaways and definitions

  - **Calibration is non-negotiable.** An LLM judge that hasn't been validated against human labels is an opinion generator, not a quality measurement tool. The confusion matrix method gives you two concrete numbers (TPR and TNR) that tell you exactly how much to trust the judge.

  - **TNR is the hard metric.** LLMs default to positive assessment. Most uncalibrated judges have reasonable TPR (they recognize good outputs) but dangerously low TNR (they let bad outputs through). Improving TNR requires deliberate prompt engineering with near-miss examples that teach the judge what "not good enough" looks like.

  - **The calibration loop is iterative.** Label traces, run the judge, build the confusion matrix, read every disagreement, make targeted prompt changes, re-run. Most judges reach 90% TPR and TNR within 3-5 iterations. Track metrics across rounds to confirm each change helps.

  - **Near-miss examples are the highest-leverage fix.** Adding 3-4 traces that look superficially good but fail the specific criterion typically produces 15-25 percentage point improvements in TNR. These examples teach the judge the boundary between "adequate" and "good enough."

  - **Use the dev/test split religiously.** Iterate on the dev set. Validate once on the test set. If test set metrics are significantly lower than dev set metrics, you've overfit your prompt to the dev set's specific traces.

  - **Know when to stop.** If 5+ iterations can't push both TPR and TNR above 80%, the judge has hit its ceiling. Fall back to structured human review for that criterion, and invest human effort where automation fails most.

**Calibration**
The process of comparing an LLM judge's verdicts against human labels on the same set of traces to measure agreement and improve the judge's reliability.

**Confusion Matrix**
A 2x2 table that categorizes every judge verdict into one of four outcomes: True Positive (both agree Pass), False Positive (judge says Pass, human says Fail), False Negative (judge says Fail, human says Pass), and True Negative (both agree Fail).

**True Positive Rate (TPR) / Sensitivity**
The percentage of human-labeled Pass traces that the judge also labels Pass. Measures how reliably the judge catches good outputs. Formula: TP / (TP + FN).

**True Negative Rate (TNR) / Specificity**
The percentage of human-labeled Fail traces that the judge also labels Fail. Measures how reliably the judge catches bad outputs. Formula: TN / (TN + FP).

In the next chapter, we will learn how to use the eval infrastructure built in modules 4 through 9 to systematically improve your agent's quality through prompt iteration, model upgrades, and architectural changes.
