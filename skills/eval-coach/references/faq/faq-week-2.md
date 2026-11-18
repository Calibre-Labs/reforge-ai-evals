**

# AI Evals Week 2 FAQ: eval rubrics and trace analysis

Answers to the questions from the Week 2 chat and Q\&A on Oct 28, grouped by topic.

## Our favorite question

### How do the rubric, release thresholds and agent success rate fit together, and when do you need each?

They answer three different questions at three stages. The rubric says what good looks like. Write it into the PRD before you build, as pass or fail lines that each judge one trace. A release threshold says how often a capability has to pass before it ships, measured on a dataset: for example, 90% of test sessions pass the line "every figure names its time period". Thresholds can rise as you go from alpha to general availability. Agent success rate is the production number: the share of real sessions that pass every outcome and governance line. It's often built from several lines, which is why it's a composite. Release thresholds are in Week 3, and agent success rate is in Week 5.

## Rubrics

### Good is subjective. How do you turn it into strict evals?

That's the job of the rubric. Start with concrete examples of good and bad outputs and write down what makes them different. Then turn each difference into a line that's pass or fail on one trace. "Leads with a highly readable map" is still a judgment call, so we rewrote it as "the output comes first, with at most two sentences around it", which code can check. When a line can't be made that concrete, an LLM judge checks it, and you measure how often the judge agrees with you (Week 4).

### One more time: what is a rubric? Is it the whole set of evaluation criteria, or a subset like a safety rubric?

A rubric is your written definition of good for one product: a short list of pass or fail lines in four groups (outcome, trajectory, governance and experience). Each line is checked against one trace, meaning the output and the steps that produced it. Safety rules are part of it. They go in the governance group as things the agent must always or never do.

### What are the sections of a rubric, and how many lines should each have?

Outcome (what it produced, and is it right), trajectory (how it got there), governance (what it must always or never do) and experience (how it felt to the user). Start with 2 or 3 lines per group, so about 8 to 12 in all, and add lines as trace analysis turns up new failures. Most PRDs we review have no rubric at all, so a short one is a big step. The [eval-rubric skill](https://github.com/Calibre-Labs/reforge-ai-evals/blob/main/skills/eval-rubric/SKILL.md) drafts one from your PRD.

### Isn't one PM writing the rubric a single point of failure?

It can be, so bring other people in. Write v1 yourself from the PRD, then get a prototype in front of your team, design partners and domain experts, read traces together, and write v2 from what you all find. Week 2's prep run is an example: two of us annotated the same ten traces and compared notes.

### If the users of my AI product change, for example from B2C to B2B, should I update the rubric or the LLM judges?

The rubric first. It encodes what your target users want, so a new audience usually means some new or changed lines. The judges follow from the rubric lines, so update the ones whose lines changed, then check them again against fresh human labels.

### What do the trajectory lines and the autonomy table mean?

Trajectory lines describe the steps you want the agent to take, not just the result. For Mapper, "searches before stating a figure" is a trajectory line: the agent decides when to search, but you want it to search whenever it's in doubt. The autonomy table in the PRD says what the agent does on its own, what it confirms with the user first, and what it declines. Critical guardrails (always do this, never do that) go in the governance group.

### "Every figure in the output names its time period." Does that mean 100% accuracy?

No. Each line is pass or fail on one trace: a session passes if every figure in it names a period. Run it over many sessions and you get a pass rate, say 85%. The release threshold is the pass rate you decide is good enough to ship. Naming a period also isn't the same as being right. Whether a source supports the figure is a separate line (O2).

### Should the rubric include a target percentage for each line? Are there best practices for thresholds?

Targets live in the PRD as release thresholds, next to the rubric. How high to set them depends on how new the use case is. If you're first to market, 60% to 70% can be enough for early adopters. If you're the sixth or seventh product doing this, users expect around 90%. Set must-never lines (governance) close to 100%. Set each number before you see the results, and decide what a miss means. Week 3 covers this in detail.

## Traces and trace analysis

### Do evals replace unit and end-to-end tests, or only cover the probabilistic parts of a product?

They work together. Keep unit, integration and end-to-end tests for software behavior that should always be the same. Add evals to measure the quality of the model's output across many different inputs, where the answer can vary from run to run.

### Does trace analysis always include the user's prompt?

It always includes whatever started the run. Often that's a user message, but it can be a click, a scheduled task or a system event.

### Do you have to tell the agent to keep traces?

Usually you configure your app or a tracing tool to record them automatically. If you're prototyping without one, ask your coding agent to save each run's input, steps, tool calls and output to a file.

### How do you set a baseline for token use?

Run a set of representative inputs and look at the spread of tokens per session. That spread is your baseline. Then look at the expensive outliers to see what made them long, and set a cost threshold in the PRD (Mapper's is under $0.10 a session).

### How do trace evals differ from outcome evals?

Outcome lines judge the result: is every figure sourced? Trajectory lines judge the steps: did it search before stating a figure? You need the trace for both, because it shows what the agent read and did, not only what it said.

### Mapper uses a custom review page. Wouldn't a tool like Arize Phoenix be easier? Which tracing tools do companies use?

Use a tracing tool to record and store traces. Common ones are Arize Phoenix, Langfuse, LangSmith and Braintrust, and we'll demo a few later in the course. For reading and annotating, we recommend a review page built for your product, since it shows your trace in the shape your team thinks about it. Week 5 builds one with the trace-review-app skill, and it can sit on top of any of those tools.

### If I use Claude, or a homegrown AI app, how do I do trace analysis on a session?

You can ask Claude to critique a session, but read and annotate it yourself first. That's where you learn what good means for your product. For your own app, save each run (the input, the steps, the tool calls and the output) to files or a tracing tool. The trace-review-app skill in the [course repo](https://github.com/Calibre-Labs/reforge-ai-evals) builds a review page, and the trace-codes skill groups your notes into patterns.

### Where are the notes saved on the trace review page you showed?

That page is a small web app hosted on Claude that saves each reviewer's notes under their login. A shared sheet works too for a simple prototype and a small team. It gets harder in a sheet once many people review many traces. Week 5 covers building your own.

### My company doesn't allow Claude.ai. Can I still use the Mapper traces and skills?

Yes. The Mapper traces are in the [course repo](https://github.com/Calibre-Labs/reforge-ai-evals), and the skills work with any coding or coworker agent. Share the repo with your agent and ask it to help you use it.

### Is Mapper internal to Calibre Labs? Can we try it?

It's public at [mapper.calibrelabs.ai](https://mapper.calibrelabs.ai). Try any technology category.

### Can I use this with Azure Databricks, where I run evals today?

If you have a coding agent that can work in that environment, share the course repo with it and ask it to adapt the skills. The traces in the repo are plain files, so they load anywhere.

### My product is a skill or an MCP server that runs in my customers' Claude. I don't get server-side traces. What can I do?

MCP passes very little user context to your server, so you can't get the full trace from there. Log the requests and responses your server does see, and ask a few users or teammates to share full session transcripts from their agent (Claude Code can export them). That's how we evaluate our own skills.

## Datasets and inputs

### How do you build a dataset of everyday requests before you launch?

Start from real sources: your own team using the product, support tickets, sales calls and search logs from related features. Then use a user input grid to list the ways requests differ (who asks, how vague, which edge cases) and fill the gaps. The [uig skill](https://github.com/Calibre-Labs/reforge-ai-evals/tree/main/skills/uig) does this from a short description of your product.

### After mapping the user input grid, how do we generate the inputs? Can I give the grid to an LLM?

Yes. Give it the grid plus a few real examples from your own use or your team's, and ask for the format your prototype reads. For example, a JSON file of 10 inputs that you run through the agent one at a time, saving each output to a file. Real examples matter: without them, generated inputs all sound alike.

### How do you generate trustworthy synthetic trace data at scale without access to product traces?

Seed it with whatever real data you can get, even a little. The frontier labs do the same for enterprise use cases: they can't use customer data, so they build synthetic environments. A coding agent can generate the data, but without real seeds it lacks the variety of real users. Collect seeds from dogfooding, design partners and your sales team. Then ask for synthetic users that vary along the dimensions in your user input grid.

## Trace codes

### AI clusters notes well, but it can get it wrong. Should we evaluate the clustering too?

Check it yourself rather than build another eval. The review page has an accept and reject step for each draft code, so you keep the ones that hold up. A classmate's tip works well too: ask for two or three different clusterings, pick the best fit, and ask the AI to explain how they differ.

### Is one trace code one fix?

Not always. A code names a problem. Some codes need several fixes to go from 50% right to 90% right, and some fixes clear more than one code.

### What does a pass or fail label on a trace code mean?

Whether that problem happened in a trace. Your first read is open-ended, with no codes in mind. Once you have codes, you label more traces yes or no for each one, for example "did it mix time periods?". That tells you how often each problem happens. Those labels also become the reference an automated judge is checked against, so it can label many more sessions the way you would.

### How do we decide between a code check, an LLM judge, a person, or a mix?

That's Week 3. The short version: use a code check wherever a rule works, since it's cheap and gives the same answer every time. Use an LLM judge when the check needs judgment. People set the standard both are measured against.

### Does this apply to agents that aren't conversational?

Yes. The input is a document, a chart or an event instead of a chat message, and the trace still records the input, the steps, the tool calls and the output. Write the rubric, read traces and code them the same way.
