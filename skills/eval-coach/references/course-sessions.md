# The live sessions, synthesized

What each live session of the Reforge AI Evals course (fall 2026) taught, rewritten as notes. The
slides themselves are not included. Mapper, the course agent, runs through every week; its numbers
are in `mapper-case.md`.

The course is one loop, the AI flywheel: traces, datasets, evals and monitoring, all aimed at one
north star, the agent success rate. It starts before the loop with an AI PRD, an eval rubric and a
prototype.

| Week | Theme | Skills shown |
|---|---|---|
| 1 (optional primer) | How agents work, and what an eval is | none |
| 2 | Define good: eval rubrics and trace analysis | eval-rubric, uig, trace-codes |
| 3 | Measure it: code checks and LLM judges | eval-code, eval-llm-judge |
| 4 | Improve it: judges you can trust, a better agent | llm-align, uig, ticket-to-eval |
| 5 | Run it live: complex agents, online evals, monitoring | trace-review-app, eval-guide |

---

## Week 1: How agents work, and what an eval is

**An agent is a goal-oriented model running in a loop with tools.** Built up in four steps on a
"book dinner for four on Friday" task:

1. A model alone: text in, text out. It can describe how to book, but nothing gets booked.
2. Add tools (`search_restaurants`, `check_times`, `book_table`): one tool call, then it stops.
3. Add a loop: each tool result goes back to the model until the table is booked.
4. Add a goal: you name the outcome; the model picks the steps and decides when to stop.

**An agentic product has four parts**, and each fails differently:

| Part | Question | Why it matters |
|---|---|---|
| Context | What does the model see on each call? | If it isn't in the context (or training data), the model doesn't know it. |
| Retrieval | What information gets brought in? | The answer can only be as good as what retrieval brings in. |
| Harness | What does the loop code do? | If the harness never sent an instruction, the model never saw it. |
| Systems | What does it run on, and at what cost? | Cost, latency and reliability are set here. A right answer can still be too slow. |

**Three implications of the loop.** The context only grows. A tool call is text the model wrote,
so it can be wrong like any sentence. The agent decides for itself when it's finished. So a
mistake in one step is read as fact in every step after it.

**Small error rates compound.** At 95% per step, the chance all ten steps are right is
0.95^10 = 60% (assuming independent steps).

**An eval checks the agent's work against a written standard.** Three parts: the trace (a record
of what the agent did in one session), the rubric (what good looks like, written down) and the
scorer (compares the two on one criterion). The verdict is pass or fail. One trace on one rubric
line gives a pass or fail; many traces give a metric, the share of sessions that pass.

**A trace holds turns, and a turn holds spans.** A turn is one user message and everything the
agent did in response. A span is one unit of work inside a turn (a model call, a search). A tool
call is the model's request to run a tool, with its arguments.

**The trace shows problems the final answer hides.** A Mapper session that looked fine on screen
had one finding per part: retrieval (Intercom's company revenue shown as Fin's), context (asked to
rank by revenue, ranked a company with undisclosed revenue second), harness (nothing checks that a
source link opens; one pointed at a logo image), systems (12 seconds, about 10,000 tokens: fine).

**Each part needs a different check.** Context and retrieval problems show in the output: read the
output against its sources. Harness problems don't show in the final answer: check the steps in
the trace. Systems problems show only in cost, latency and error rates: track them across many
sessions.

---

## Week 2: Eval rubrics and trace analysis

**Why PMs should learn evals.** Traditional products have a set path (visit, sign up, activate,
convert), so funnels show where users get stuck. AI products give a different answer every time;
every user gets their own version of the product. The job becomes moving the whole spread of
output quality toward great. The fundamentals carry over:

| What you do today | The AI version |
|---|---|
| User research | Trace analysis: read what the agent actually did |
| Funnels and analytics | Online evals: score live sessions |
| A/B tests | Agent experiments: score two versions on the same inputs |
| QA against the spec | Eval rubric: the spec for good, line by line |
| Regression and smoke tests | Offline evals: score fixed inputs before every release |

**Who does what.** Needs judgment: you. Done every week: a tool. Follows a recipe: a skill. You
decide what good means, read and annotate some share of traces, align judges and prioritize
fixes. Tools you can build: a trace viewer with notes, an annotation workflow, a dashboard of
scores. Skills: draft a rubric, build test inputs, cluster notes into codes, write and run evals.

**You already have a rubric in your head.** The coffee homepage exercise (Starbucks vs Philz):
both can be "right"; it depends on whether the goal is a familiar purchase or discovery of a
differentiated offer. The rubric makes "great" explicit.

**An agent rubric has four kinds of lines:**

| Group | Question | Mapper example | Usual stakeholders |
|---|---|---|---|
| Outcome | What did it produce, and is it right? | Every figure has a source that supports it. | PM, domain experts, engineering |
| Trajectory | How did it get there? | Confirms scope, then delivers what was confirmed. | Engineering |
| Governance | What must it never do, and always do? | Declines investment advice, and says what it can do instead. | Legal, finance, security |
| Experience | How did it feel in this channel? | Leads with a readable map or table, not an essay. | Design |

Write rubric v1 from the PRD before any traces (eval-rubric reads the PRD, asks what it leaves
open, drafts; you decide). Mapper's v1 had nine lines.

**Trace analysis has three steps**, repeated whenever the agent changes significantly:

1. **Build a dataset** (uig drafts, you review). Cover everyday requests and product boundaries.
   Once you have users: production traffic, support tickets, thumbs down, user corrections.
   Before users: a user input grid (list the ways requests differ, cross them, pick inputs that
   cover the grid). Start with 10 to 20 inputs; grow to 50 to 80 as you find failures. Mapper's
   grid: query type × market × style × time, about 360 combinations; ten inputs each from a
   different part of it (basic category, jargon, historical, company-anchored, strategic, vague,
   future-dated, off-limits).
2. **Read and take notes** (you, in a trace viewer). Start with the user's intent, follow the
   agent's steps, write what worked, what went wrong and what should have happened. Free-text
   notes first; no verdicts yet.
3. **Group into codes** (trace-codes drafts, you edit). A trace code is a short name, a yes/no
   definition for one trace, and two or three example traces with evidence.

**Codes become fixes, rubric lines and evals.** Some you just fix in the prompt; some sharpen or
add rubric lines (v2); some show where to add inputs; some are worth an automated eval.
**Prioritize by impact** (could it mislead users or break a must-never?), **frequency** (how often
in this reviewed set?) and **evidence** (can we reproduce it, is the expected behavior clear?).
Counts describe the selected traces, not live traffic.

Recap: an eval scores a trace against a rubric. Write v1 from the PRD before traces. Read traces
before you automate anything. Notes become trace codes; codes become your roadmap.

---

## Week 3: Automated evals (fix what's obvious, check what follows a rule, judge the rest)

Lessons carried over from the Sierra bonus session: turn real failures into tests; use rules and
a judge together; agree on success before you build.

**Not every trace code gets an eval.** For each code, ask three questions in order:

1. **Specification check:** was the prompt clearly supposed to handle this? If no, it's a
   *specification gap*: fix the prompt (add the instruction to the context).
2. **System check:** does the agent have what it needs to get it right? If no, it's a *missing
   capability*: change the harness or system (a harness step, a tool, retrieval or the model).
3. **Generalization check:** does it work only some of the time? If yes, it's a *generalization
   gap*: write an eval, measure the rate, then improve it.

Only generalization gaps are worth an automated eval. Fix the obvious first; then a check or a
judge keeps it fixed. (Mapper: TC-11 investment advice and TC-9 past/future years were spec gaps
fixed with prompt lines; TC-1 dead links was a missing capability fixed in the harness.)

**Four kinds of eval, used together:** code check (a rule in code; best for anything you can state
as a rule), LLM judge (a model answers one yes/no question; for cases that need judgment), human
review (the standard the others are checked against), user feedback (thumbs, edits, what users do
next; signal from real use).

**Use a code check wherever a rule works.** Fast, cheap (no model call), the same answer every
time, safe to run in CI. Write a check first; reach for a judge only when you can't write the
rule. Four common types: structure (right shape), required content (something that must be there
is there), format (a value follows a pattern), tool use (the agent used its tools correctly). Read
the code before you trust it.

**Use a judge when the check needs judgment.** A code check can confirm a figure is there; it
can't tell whose it is. A good judge answers one clear yes/no question, says when to fail, gives
examples (a fail and a pass), and returns pass or fail with a one-sentence reason. Binary because
a yes/no is easy to check against your own label and a 1 to 5 score is not. Narrow, one judge per
code, so a failure points at one thing. Four common kinds: faithfulness (is each claim backed by
its sources?), task completion (did it do what was agreed?), policy and safety (did it stay inside
its limits?), domain correctness (is it right in ways only an expert would catch?).
**Reference-based** judges compare with an answer you hold; **reference-free** judges check the
output against the rubric and the trace when there's no single right answer.

**Release thresholds: how good is good enough to ship.** Set the bar for each check before you see
results, set it higher for a must-never, and decide now what a miss means. Mapper's PRD: under
$0.10 per session, median time to first map under 30s, zero sessions failing any governance line
at launch.

Setup used live: Claude (Cowork or Code) with the plugin, a shared folder for datasets and labels,
and the agent's repo for scorers and runs. To do it yourself: install the plugin, keep datasets
and traces where Claude can read them, and connect your AI ops tool through its MCP server if you
have one. The plugin's `templates/eval-pages` make a results page and a scorer page.

Recap: fix what's obvious before you write an eval. Write evals only for what's specified but works
only sometimes. Code checks wherever a rule works; one yes/no question per judge. Set the threshold
before you see the results.

---

## Week 4: Aligning evals (measure the judge against people, fix it, then improve the agent)

**The question:** your judge says 37% pass. Is the score low because the agent is wrong, or
because the scorer is?

**Compare the judge's calls with human labels in a confusion matrix.** True positive: both pass.
False negative: the judge fails a good session. False positive: the judge passes a bad session.
True negative: both fail. Then two rates, keeping both kinds of mistake visible:

- **TPR** (true positive rate): of the sessions you pass, how many does the judge pass too?
- **TNR** (true negative rate): of the sessions you fail, how many does the judge fail too?
- Accuracy (overall agreement) hides which way the judge is wrong.

Worked example (illustrative labels, 30 sessions): TP 7, FN 4, FP 3, TN 16. TPR 7/11 = 64%,
TNR 16/19 = 84%, accuracy 23/30 = 77%. **Align until both TPR and TNR reach 90% or more:** read
the disagreements, change the judge, measure again.

Live with llm-align on Mapper's metric-scope judge: v1 TPR 69% / TNR 81%; v3 after alignment TPR
91% / TNR 93%. What changed: clearer rules and new examples, steps in order instead of a list
(stop at the first fail), and a stronger judge model (the steps only worked on the bigger model).

**Managing datasets.** Improve a judge on one set, check it on another. Roughly 100 human-labeled
sessions at minimum: **train ~10** (examples in the prompt that show where the line is), **dev ~30**
(disagreements show where instructions need to be clearer), **test ~60** (fresh cases show whether
the changes carry over). Teach with examples you don't test on. Grow the dataset where it's thin:
uig finds empty cells in the grid (Mapper's 30 sessions: 19 tech/SaaS, 26 about today, one each for
healthcare and financial); ticket-to-eval turns a piece of user feedback into a regression row and
a generalized row.

**Improve the agent one change at a time.** Change one thing aimed at one score, re-record the same
sessions on the new version, score with every scorer (not just the one you aimed at), and compare:
did it move, did anything else drop? Put the fix in the right part (context, retrieval, harness,
systems), one kind of change at a time.

**Three signs your evals are working:** you ship a model change in a day or two; user feedback
matches the evals (what people complain about, your scores already caught); risky launches have a
threshold decided before the results.

Recap: trust a judge only when TPR and TNR are both high. Read a code check's calls too. Teach with
examples you don't test on. One change at a time, then check every score.

---

## Week 5: Run it live (complex agents, online evals, monitoring)

**Every scorer maps back to a trace code**, and every code ends somewhere: fixed, checked by code,
judged, or read in monitoring.

**Complex agents use the same four parts, with more agents in the harness.** A main agent hands
work to helpers, each one an agent. Each helper gets its own context; helpers often do the
searching; the harness decides who does what; systems can mix many models. Examples: Anthropic's
multi-agent research system (a lead agent plans and runs search subagents in parallel, a
citations subagent checks sources; beat a single agent by 90% on their eval at about 15× the
tokens); xAI's Grok Bot (bots that pull, draft and review, with a person approving); Sierra
(supervisor agents for input, policy and quality around every task agent, over 15 models each
picked for its task; governance is itself an agent, and each is evaluated alone).

**Start with one agent; add one only for a reason.** Multi-agent costs 3 to 10× the tokens and is
often slower. Three good reasons: the context is getting polluted, the work splits into parallel
parts, or one agent has too many tools and picks the wrong one.

**Where rubric lines attach in a bigger agent:** outcome at the end of the run (right result,
whatever the path); per-helper checks on each helper or tool (did this step do its job?);
trajectory on the main agent (right helper, right inputs, sensible order, asked only when it had
to); governance everywhere, often as its own agent; experience on what the user saw. One agent's
outcome is the next agent's input: test each helper alone first, then score the whole run, and
start with the main agent because its mistakes spread.

**Two harnesses: code decides, or the model decides.** Mapper loop v1 always asked a scoping
question and used rules in code to pick the output; loop v2 asks only when unclear, lets the model
pick the output, and makes research a tool it calls.

**Offline and online evals answer different questions.**

| | Offline | Online |
|---|---|---|
| When | Before you ship | After you ship |
| Inputs | A dataset you chose | Real sessions |
| Reference answer | Sometimes | Never |
| How many | Every row, every run | Every session, or a sample |
| Read next to | The last version's scores | What users did |

Offline says a change is safe to ship. Online says what users got. Your dataset is a guess about
your users; production shows how good the guess was. **Coverage gap**: no row, too few rows, or no
scorer for what users ask. **Drift**: the mismatch moving, as the mix shifts or one kind of request
starts doing worse.

**Agent success rate is the north star.** Some agents have a clean done state (a ticket resolved,
code accepted); most, Mapper included, don't, so you build one. Three principles: outcome-based
signals (what the session produced, not activity like turn count), full coverage (score every
session; explicit thumbs cover only 1 to 2%), objective and per-session (one number you can
hill-climb). A session with no user feedback succeeds when all critical evals pass: a silent user
with a clean run is a success. Count honestly: a silent user isn't a failure, and a missing eval
isn't a success. Keep cost and latency as separate guardrails.

**One number hides where it's failing.** Split by intent and rubric group. In a lender's customer
agent, "researching" sessions had the best experience scores and the worst trajectory: the agent
stalled and users left without complaining.

**Where scores and users disagree, read the sessions.** Scores pass and users leave or complain:
your rubric is missing something, write a new code. Scores fail and users are happy: the line is
too strict or doesn't matter, check it with users. Those two boxes are where the next dataset rows
come from. Then: real request → new row or criterion → fix → regression case → check on fresh cases.

**From the course reader:** sample 1 to 10% of live sessions (at random, by failure signals, and by
outliers in time or tokens); watch the gap between offline and online scores; refresh the dataset
from thumbs, tickets and the evals. If offline scores improve and online scores don't, fix the
evals. A failure funnel (one yes/no question per step, read as a funnel) shows where multi-step
sessions fall out. One analytics team built its review tool in a day and found eight failure modes
from 45 sessions of notes.

**The plugin does every step except two:** you read and annotate seed traces (that's where trace
codes come from) and you label examples to check the judges (that's what makes a score worth
trusting). Everything else follows a recipe, so a skill can do it.

**What to do next at work:** pick one agent; read 20 traces and write rubric v1 (notes, then codes,
then the rubric); write one evaluator for the code that matters most; label 20 sessions and align
the judge before you trust its number.

Recap: bigger agents use the same rubric lines; what changes is where they attach. Start with the
main agent's trajectory. Your dataset is a guess about your users. Track one agent success rate and
split it by intent. Let skills do the recipe work; keep the reading and the labeling.
