# Glossary

The course's terms, as the course uses them. One or two sentences each. For more, the source in
brackets says where to read.

| Term | Meaning |
|---|---|
| Agent | A goal-oriented model running in a loop with tools. You name the outcome; the model picks the steps and decides when to stop. [Week 1] |
| Agentic product | Context, retrieval, a harness and systems around one or more agents. [Week 1] |
| Context | The full text sent to a model for one call. The model knows nothing else (beyond training data). [Week 1] |
| Retrieval | The searches, lookups and reads from memory or files that bring information into the context. [Week 1] |
| Harness | The code around the model that runs the loop: sends instructions, conversation and tool results, runs tool calls, manages context, permissions and retries, and can hand work to helper agents. [Week 1, FAQ week 1] |
| Systems | The models, tools, memory, stored files and infrastructure behind the agent. Cost, latency and reliability live here. [Week 1] |
| Trace | The record of one session: what the model was sent, every tool call and result, what the harness decided, tokens, time and cost. [Week 1] |
| Turn / span | A turn is one user message and everything the agent did in response. A span is one unit of work inside a turn, like a model call or a search. [Week 1] |
| Session | One conversation with the agent from start to close; the unit a trace records. [FAQ week 1] |
| Eval | A check of one trace against one rubric line, giving pass or fail. Run over many traces, it gives a metric. [Week 1, ch 4] |
| Eval rubric | The written definition of good, line by line, in four groups: outcome, trajectory, governance, experience. Lives in the PRD. Skill: `eval-rubric`. [Week 2, ch 2] |
| Outcome / trajectory / governance / experience | What it produced and whether it's right / how it got there / what it must never and always do / how it felt in this channel. [Week 2] |
| Release threshold | The pass rate a check must reach to ship, set before you see results; higher for must-nevers. [Week 3] |
| AI PRD | A PRD that defines what good looks like (rubric, autonomy, thresholds), not just features. Template: `templates/ai-prd-template.md`. [ch 2] |
| User input grid (UIG) | The dimensions along which real requests vary, crossed to pick a diverse set of test inputs and find coverage gaps. Skill: `uig`. [Week 2, ch 3] |
| Trace analysis | Build a dataset, read traces and write free-text notes, group the notes into trace codes. [Week 2, ch 3] |
| Trace code | A named pattern across traces with a yes/no definition for one trace and two or three examples with evidence. Skill: `trace-codes`. [Week 2] |
| Specification gap | The prompt was never told to handle it. Fix the prompt; no eval needed. [Week 3] |
| Missing capability | The agent lacks what it needs (a tool, a harness step, retrieval, a better model). Change the harness or system. [Week 3] |
| Generalization gap | Specified and possible, but works only some of the time. The only kind worth an automated eval. [Week 3] |
| Code check (code-based eval) | A deterministic rule in code that returns pass or fail: structure, required content, format, tool use. Skill: `eval-code`. [Week 3, ch 5] |
| LLM judge | A model that answers one narrow yes/no question about a trace, with a reason. Skill: `eval-llm-judge`. [Week 3, ch 6] |
| Reference-based / reference-free judge | Compares to an answer you hold / checks the output against the rubric and the trace when there's no single right answer. [Week 3] |
| Human labels | A person's pass/fail calls on a sample of sessions: the standard judges are checked against. [Week 4] |
| Confusion matrix | Human label against judge call: true positive, false negative, false positive, true negative. [Week 4, ch 8] |
| TPR / TNR | Of the sessions you pass, the share the judge passes / of the sessions you fail, the share the judge fails. Align until both are 90%+. Skill: `llm-align`. [Week 4, ch 8] |
| Judge alignment (calibration) | Read disagreements with human labels, change the judge, measure again. [Week 4, ch 8] |
| Train / dev / test | ~10 labeled examples in the judge prompt / ~30 to find disagreements and improve it / ~60 fresh ones to check it carries over. [Week 4, ch 7] |
| Regression row / generalized row | A dataset row close to a real failure / an abstracted version for broader coverage. Skill: `ticket-to-eval`. [Week 4, ch 7] |
| Offline eval | Scores a fixed dataset before you ship: is this change safe? [Week 5, ch 10] |
| Online eval | Scores real sessions after you ship, every session or a sample: what did users get? [Week 5, ch 10] |
| Coverage gap / drift | No row, too few rows or no scorer for what users ask / that mismatch moving over time. [Week 5, ch 10] |
| Agent success rate | One per-session north star built from outcome signals: a session succeeds when every critical eval passes, with user actions and sentiment counted where they exist. [Week 5] |
| AI flywheel | Traces → datasets → evals → monitoring, repeated, aimed at the agent success rate. [Intro, Week 2, Week 5] |
| Vibe check | Informal testing at the prototype stage; the first of three lifecycle stages (vibe checks, offline evals, user monitoring). [ch 1] |
| Failure funnel | One yes/no eval per step of a multi-step agent, read as a funnel to see where sessions fall out. [ch 12] |
| Trace review app | A review page built for one product's traces, with notes, labels, codes and exports. Skill: `trace-review-app`. [Week 5, ch 13] |
