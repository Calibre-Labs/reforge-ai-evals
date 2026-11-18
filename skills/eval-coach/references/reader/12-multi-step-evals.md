# Ch 12: Visualizing Multi-step Evals

**A single "72% task success rate" is not actionable. It doesn't reveal where requests fail or which steps bottleneck a complex agent pipeline.**

Module 12 covered how to decompose complex agents into evaluable components. This chapter covers how to visualize those evaluations in a way that makes cascading failures visible, bottlenecks obvious, and improvement priorities clear.

The tool is the failure funnel: a sequential visualization that measures success at each step and shows exactly where requests fall out of the pipeline.

**Failure funnels turn abstract quality scores into concrete engineering priorities.** Instead of "our agent needs to be better," you get "Column Selection is failing 24% of the time and accounts for nearly half of all end-to-end failures. Fix that step first."

### Why Headline Metrics Are Insufficient

A 55% end-to-end success rate sounds bad. But the number alone doesn't tell you what to do about it. If the bottleneck is one step with a 76% pass rate, and every other step is above 95%, the fix is targeted and the path to 72% end-to-end success is clear. Without step-level visibility, teams waste time optimizing steps that aren't the problem.

> *Diagram idea: diagram — headline metric (55% success) vs. funnel view showing the specific step causing most failures*

The pattern is common. A PM presents "55% task success" to leadership. Leadership asks "what are we doing about it?" The honest answer without a funnel is "we're working on it."

The answer with a funnel is "Column Selection accounts for 47% of failures. We have a targeted prompt fix in testing that should bring end-to-end success to approximately 72%. We'll ship it next week."

One answer gets a follow-up meeting. The other gets a nod.

### Building a Failure Funnel

#### **Step 1: Map your pipeline steps**

**List every distinct step your agent performs in sequence. Be specific.** "Process the request" is not a step. "Identify the user's intent from the query," "select the relevant database tables," and "generate the SQL WHERE clause" are steps.

> *Diagram idea: diagram — example pipeline step mapping for two agents: Support Triage (5 steps) and Text-to-SQL (7 steps)*

For the Support Triage Agent: Parse input → Identify intent → Assign category → Detect sentiment → Determine urgency → Format output.

For a Text-to-SQL agent: Intent understanding → Table identification → Column selection → JOIN logic → WHERE clause → Query compilation → Execution.

The right level of granularity is the level at which a failure at one step can be diagnosed and fixed independently. If two "steps" always fail together and can only be fixed together, they're really one step for funnel purposes.

#### **Step 2: Define binary success criteria per step**

**Each step gets a Pass/Fail criterion that can be evaluated independently.** These criteria should use the same eval types from modules 6 and 7 (week 2).

  - "Did intent understanding correctly interpret the user's goal?" LLM judge with a labeled dataset of intents.
  - "Did the agent select the correct database tables?" Code eval comparing selected tables against ground truth.
  - "Is the generated SQL syntactically valid?" Code eval using a SQL parser.
  - "Did the query execute without errors?" Code eval checking execution result.

The criteria should be specific enough that a Pass at Step 3 and a Fail at Step 4 tells you "Column selection was correct but JOIN logic was wrong," not "something went wrong somewhere in the middle."

#### **Step 3: Measure the funnel**

**Run your reference dataset through the pipeline**. At each step, evaluate Pass/Fail. Only traces that passed the previous step proceed to the next.

> *Diagram idea: diagram — funnel measurement showing traces narrowing at each step, with pass count and pass rate at each stage*

Record three numbers at each step: how many traces entered the step, how many passed, and the step-level pass rate. The pass rate at each step should be computed against the number of traces that reached that step, not against the original total.

## Case Study: Text-to-SQL Failure Funnel

#### **The 7-step pipeline**

Suppose 100 queries enter the pipeline and here's where they fall out.

|  |  |  |  |
| :-: | :-: | :-: | :-: |
| \*\*Step\*\* | \*\*Entering\*\* | \*\*Passing\*\* | \*\*Step pass rate\*\* |
| 1\\. Intent understanding | 100 | 95 | 95% |
| 2\\. Table identification | 95 | 87 | 91% |
| 3\\. Column selection | 87 | 66 | 76% |
| 4\\. JOIN logic | 66 | 63 | 95% |
| 5\\. WHERE clause | 63 | 60 | 95% |
| 6\\. Query compilation | 60 | 58 | 97% |
| 7\\. Execution success | 58 | 55 | 96% |

**End-to-end: 55 out of 100 queries fully succeeded.**

> *Diagram idea: diagram — funnel visualization showing 100 queries narrowing through each step, with Step 3 highlighted as the bottleneck*

### **Reading the funnel**

The bottleneck is Step 3: Column Selection with a 76% step-level pass rate. This single step accounts for 21 of the 45 total end-to-end failures (traces that entered Step 3 but didn't pass: 87 minus 66 = 21).

Later steps have high pass rates (95 to 97%), but they never see most of the queries that fell out at Step 3. Their high pass rates are calculated only on the traces that survived the bottleneck. If Step 3 were fixed, those later steps would see more (and possibly harder) traces, and their pass rates might drop slightly. That's expected and healthy.

**The improvement math:** If Column Selection improved from 76% to 95% (matching the other steps), approximately 16 additional traces would pass Step 3. Even assuming later steps maintain their current pass rates, end-to-end success would jump from 55% to approximately 70%. One step, one fix, 15-point improvement. No other single change to the pipeline would produce this result.

**Fix upstream first:** This is the core lesson of the failure funnel. The earliest bottleneck step has the highest leverage. Improving Step 7 from 96% to 99% would save approximately 2 traces. Improving Step 3 from 76% to 95% saves approximately 16. Always prioritize the earliest failing step.

### Transition Failure Matrices

The failure funnel shows where traces drop out of the pipeline. The transition failure matrix shows a complementary view: which specific step-to-step transitions produce the most failures.

A transition failure matrix maps the last successful step against the first failing step across a set of traces. Each cell counts how many traces passed one step but failed at the next. The cells with the highest counts are your improvement targets.

> *Diagram idea: diagram — transition failure matrix with hotspot highlighting based on example below*

**Example:** A text-to-SQL agent's 4 step transition matrix shows that the GenSQL → ExecSQL transition has 12 failures while the DecideTool → PlanCal transition has only 2. The hotspot is clear: the SQL generation step produces queries that look correct but fail on execution. That's the transition to focus on. Without the matrix, you'd see 14 failures spread across the pipeline and not know which transition to prioritize.

**Building the matrix:** Examine each failing trace. Which step last succeeded? Which step first failed? Aggregate across all failing traces. The cells with the highest counts tell you where to apply the iteration loop from module 9.

Funnels and matrices complement each other. The funnel tells you which step has the lowest pass rate and how many traces it costs you. The matrix tells you which transition is producing the failures and helps distinguish between independent step failures and cascading failures. Use the funnel for stakeholder communication and improvement math. Use the matrix for engineering diagnosis.

## Advanced Funnel Techniques

Run separate funnels for different query types or user segments. The aggregate funnel might show a 76% pass rate at Column Selection, but the segmented funnels reveal that simple single-table queries pass at 95% while complex multi-table queries pass at 52%.

> *Diagram idea: diagram — segmented funnels: simple queries (high pass rates throughout) vs. complex queries (steep drop at Step 3)*

This prevents you from optimizing for the average when the problem is concentrated. A prompt fix targeting multi-table column selection will produce much larger gains than a generic column selection improvement, because the simple queries are already working.

#### **Cumulative vs. step-level pass rates**

Two different pass rates serve two different audiences.

**Step-level pass rate:** "Of traces that reached this step, what percentage passed?" This tells you about the step's intrinsic quality. It answers: is this step doing its job? Use step-level rates for engineering prioritization.

**Cumulative pass rate:** "Of all original traces, what percentage have passed up to this point?" This tells you the user-facing reality. It answers: at this point in the pipeline, how many users are still on a path to success? Use cumulative rates for stakeholder communication.

Both are useful. Step-level rates guide where to invest engineering effort. Cumulative rates communicate how the user experience improves as you fix each step.

### Tracking funnels over time

Run the funnel on your reference dataset after every major change. Plot step-level pass rates over time. You should see the bottleneck step improving as you iterate.

> *Diagram idea: diagram — funnel pass rates tracked over 4 iterations, showing bottleneck improving from 76% to 91%*

**If a previously solid step starts failing after a change, you've introduced a regression.** Investigate before continuing. The iteration pattern from module 10 applies: ship when the target step improved and no other step regressed. Revert when the change made things worse.

**Funnels also reveal when the bottleneck shifts.** After three iterations improving Column Selection from 76% to 93%, the new bottleneck might be Table Identification at 91%. The funnel adapts your priorities as the pipeline improves.

### Communicating with Stakeholders

Leadership doesn't need to understand evals. They need to understand where quality breaks and what you're doing about it.

**Present the funnel as a narrative.**

"Our end-to-end success rate is 55%. The bottleneck is column selection at 76%. We have a targeted fix that should bring end-to-end success to approximately 72%. We'll ship it next week and monitor." This is dramatically more actionable than "we're working on improving quality."

**Funnels also set realistic expectations.**

If there are 7 steps in the pipeline and each needs to be at 95% to achieve 70% end-to-end success, leadership can see why 99% end-to-end isn't realistic for a complex agent. The math is transparent.

#### **Reporting cadence**

**Weekly:** Internal team reviews funnel metrics, identifies the current bottleneck, and plans the next experiment.

**Bi-weekly or monthly:** Stakeholder report showing end-to-end success rate, bottleneck identification, improvement trajectory (the funnel tracked over time), and next steps. Keep the stakeholder report to one page. The funnel visualization is the centerpiece.

### Using Funnels in Practice

#### **Start simple**

Identify 3 to 5 major pipeline steps. Define binary success criteria at each. Measure where requests fall out. Fix the earliest failure first. Only move downstream once upstream reliability improves.

You don't need a sophisticated visualization tool. A table with step names, entry counts, pass counts, and pass rates (like the one in the case study above) is a perfectly adequate failure funnel. A spreadsheet works. A Jupyter notebook works. If you're building a custom trace analysis app (module 14), the dashboard pattern is the natural home for funnel visualization, with drill-down from the aggregate view to individual failing traces. The value is in the measurement, not the presentation.

#### **When funnels don't apply**

Funnels work best for sequential pipelines where each step's output feeds the next. They're the natural visualization for multi-step systems evaluated in module 12.

For parallel multi-agent systems, use per-agent eval suites and an orchestration eval instead of a funnel. The agents don't form a sequence, so there's no "funnel" of traces narrowing through steps.

For single-turn agents, the standard eval suites are sufficient. A one-step pipeline doesn't need a funnel.

## Recap and Further Learning

### Key takeaways and definitions

  - **Headline metrics hide bottlenecks.** A 55% success rate doesn't tell you what to fix. A failure funnel shows exactly which step to prioritize.
  - **Fix upstream first.** The earliest bottleneck step has the highest leverage. Improving it lifts every downstream metric. Improving a late step with a high pass rate has minimal end-to-end impact.
  - **Segment your funnels.** Run separate funnels by query type or user segment to find concentrated failure modes. The aggregate may hide that the bottleneck only exists for complex queries.
  - **Track over time.** Plot funnel metrics after every change to verify improvements hold and catch regressions. Watch for the bottleneck to shift as you improve each step.
  - **Use funnels to communicate.** A funnel visualization translates complex eval results into a narrative that leadership can act on: where we break, what we're fixing, and what improvement to expect.
  - **Transition matrices complement funnels.** Funnels show step-level pass rates. Matrices show which step-to-step transitions produce the most failures, giving engineers a precise diagnosis target.

**Failure funnel** **
**A sequential visualization that measures the pass rate at each step of a multi-step pipeline, revealing where requests fail and which step is the highest-leverage improvement target.

**Bottleneck step** **
**The pipeline step with the lowest pass rate, which disproportionately limits end-to-end success and should be prioritized for improvement.

**Step-level pass rate**
The percentage of traces that reached a given step and passed it. Measures the step's intrinsic quality, independent of upstream failures.

**Cumulative pass rate**
The percentage of original inputs that have successfully passed all steps up to a given point, representing the user-facing success rate at each stage.

**Transition failure matrix**
A diagnostic tool that maps the last successful step against the first failing step across a set of traces, revealing which transitions are the highest-leverage targets for improvement.

#### **Recommended articles**

  - [Failure is a Funnel](https://youtu.be/R_HnI9oTv3c) by Bryan Bischof, full talk on transition matrices and funnel visualization

In the next chapter, we will learn how to vibecode custom trace analysis applications that give your team superpowers for reviewing, labeling, and understanding agent behavior.
