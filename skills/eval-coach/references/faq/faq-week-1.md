# AI Evals Week 1 FAQ: how agents work

Answers to the questions from the Week 1 chat on Oct 21, grouped by topic.

## Our favorite question

### Is a harness still needed with frontier reasoning models?

Yes. Harnesses used to hard-code the decision making with step-by-step workflows, routing logic and prompts tuned for each tool. Models now do that deciding themselves. They choose which tool to use, what order to go in, when to retry or run calls in parallel, and when they're finished. The thinking has moved into the model, but the plumbing stays in the harness.

The harness reads the model's tool call requests, makes the API calls that run each tool, sends the result back to the model, and repeats until the task is done. That loop is also where the context window and compaction get managed, user permissions get enforced, and long runs (across sessions or days) are kept alive with wake-on triggers.

## Agents, harnesses and context

### If an agent can just do text in, text out (like sending a reminder every day), is the loop what makes it an agent?

Yes, the loop with tools is what makes it an agent. A model on its own reads text and writes text once. An agent gets a goal, calls tools, reads the results and picks its next step until it decides it's done. A daily reminder is a scheduled automation: the harness runs it on a schedule, and each run may be a single model call. It becomes agentic when the model chooses steps on each run, like checking your calendar before deciding what to remind you about.

### What's a simple definition of a harness?

The harness is the code around the model that runs the loop. It sends the model the instructions, the conversation and any tool results, runs the tool calls the model asks for, sends back the results, and repeats until the model is done. It also manages the context window, permissions, retries and scheduling. If the model is the engine, the harness is the rest of the car. One classmate put it as "the room the agent can walk around in".

### Is context the same as the system prompt?

The system prompt is one part of the context. Context is everything the model sees on one call: the system prompt, the conversation so far, saved preferences or memory, retrieved documents and earlier tool results. If something isn't in the context or the training data, the model doesn't know it.

### Are Cursor, VS Code, ChatGPT or Claude Code harnesses?

Cursor, Claude Code, the ChatGPT and Claude apps, and GitHub Copilot's agent mode are all harnesses. Each runs the loop, provides tools and lets you pick from several models. VS Code on its own is an editor that hosts agent harnesses, and [you can choose between several of them](https://code.visualstudio.com/docs/agents/run/agent-harnesses).

### If retries and the degree of autonomy are written in the system prompt, what's left for the harness?

The prompt can tell the model what to do when a booking slot isn't available, but only the harness can carry it out. Instructions are text the model reads. The harness is the code that calls the booking API, catches the error, sends it back to the model, enforces timeouts and permissions, and decides what goes into the next call. If the harness never sends an instruction, the model never sees it.

### Is a harness like a trigger that knows when to run the model, and retries if it fails?

That's part of it. Triggers and retries are harness jobs, along with running tool calls, managing the context and enforcing permissions.

### Why define an agent as one model in a loop? Can't an agent use more than one model?

It can. The definition describes one unit so the parts are easy to see. A product can run many agents on different models, with one agent handing work to helpers. Mapper, our course project, makes two Gemini calls per turn.

### If the wrong model is picked, isn't that a harness problem? The harness decides which model to call.

Model choice is a harness setting, so that's where you fix it. In the exercise we put models under systems, because that's where you see the cost and latency of a wrong pick. What matters is knowing where to look in the trace and where to make the change.

### How tightly are harnesses coupled to models? Are well-designed harnesses model-agnostic?

Mostly. A well-designed harness keeps the same loop and uses a small adapter per model for tool-call formats, context limits and structured output. Support for a new model can lag its release by a little while that adapter and the prompts get tuned. Either way, run your evals before you switch: the same harness can work better with one model than another.

### Do we need a harness to deal with the probabilistic nature of LLMs in deterministic use cases?

The harness can't make the model deterministic, but it can keep deterministic work out of the model. If a step has one right answer (a calculation, a lookup, a format), do it in code or a tool and let the model handle the judgment calls. The harness can also run code checks on the model's output, like making sure a link opens or the output matches a schema.

### Where do sub-agents fit in? Do we tell the harness to create them, or does it decide?

It depends on the harness. Coding agents like Claude Code start sub-agents on their own for some tasks, and you can configure when they do. Sub-agents help with parallel work and specialized tasks, and they keep the main agent's context small. The trade-off is quality, cost and latency: they use more tokens and can make a simple task slower.

### When should an agent ask a scoping question, and when should it just go?

Ask when the intent isn't clear and the task will take a lot of effort, since a wrong guess on a long task costs more than one question. Mapper asks one scoping question before it searches. For quick tasks that are easy to redo, it's better to just start.

### As a PM, when do you build an agent versus a skill?

A skill is a set of instructions and files an agent loads when it needs them, like a playbook for one kind of task. Write a skill when an existing agent needs to do a task better or more consistently, such as always sending email from Outlook. Build a new agent when you need a new goal, new tools or permissions, or a product surface of its own.

## Diagnosing problems

### Are there easy ways to tell when a model has started losing earlier context?

Watch for repeated work, an instruction from earlier that gets dropped (the "nine turns in, it forgets turn three" case), or questions you've already answered. A quick check is to ask it to restate your constraints. The reliable check is the trace: see whether the token count was near the limit, whether compaction ran, and whether the earlier instruction was still in the context on the call that failed.

### How could a retrieval process be upgraded?

Take the agent that quoted last year's menu. You could make it search the restaurant's own site instead of an old index, add dates to what it retrieves and prefer recent results, re-index more often, or improve how documents are split and labeled in a RAG store. Anthropic's [contextual retrieval post](https://www.anthropic.com/news/contextual-retrieval) is a good example of the last one.

### Where would last year's menu even come from?

Three likely places: the model's training data (it answered from memory without searching), a stale search result or cached page, or an old document in a RAG store. The trace tells you which. No tool call means it came from the model's weights. A search that returned an old page means retrieval. For public data that changes often, like a menu, a live web search is usually better than storing a copy.

### If an agent is slow to respond, where would you look, and what would make it faster?

Open the trace and look at the time for each span. Common causes are too many loop turns, a large context (the model rereads everything on every call), a slow tool or API, a large reasoning model on a simple step, or sub-agents. Fixes include a smaller model for simple steps, running independent tool calls in parallel, trimming the context, prompt caching, and lower reasoning effort.

### Errors compound over a loop. Where should error reduction live in an agentic product?

In a few places. Code checks in the harness catch known mistakes (a link that doesn't open, output in the wrong format). Tools that return clear errors let the model retry. Clean context keeps one mistake from being reread as fact on every later step. Evals on traces show where errors start. At 95% per step, a ten-step task succeeds about 60% of the time, so each step matters.

### So do you first work out whether the issue is in the harness or the systems, and then, within the harness, whether it's retrieval?

Yes. Read the full trace and work out which part the problem came from: context, retrieval, harness or systems. Each needs a different check, and Weeks 2 to 5 cover how to write them.

## Evals, skills and models

### Do you run evals on skills, or only on agents?

Both. Evals check behavior in traces, and a skill changes behavior. You can check that the agent loaded the skill when it should have, and that it followed it. For example, a skill tells the agent to send email from Outlook, and an eval checks whether the email was actually sent from Outlook.

### If I have lots of skills and a new agent sometimes doesn't call them, is that a harness problem? How do I build skills for a harness?

Usually the skill's description is the problem. Until it loads a skill, the agent sees only the skill's name and short description, so a vague description doesn't get picked. Check the trace: if the skill wasn't listed in the context, it's a harness setup issue (the skill isn't installed or visible to that agent). If it was listed and not used, rewrite the description to say when to use it, in the words people will use. Then add an eval with prompts that should trigger the skill and check that it loads.

### Can our AI agents create these evals, or do you recommend a tool?

Coding agents can do a lot of the eval work: draft rubrics, write code checks and LLM judge prompts, and run them. You need to know what to ask for and what to look for in the result. That's what Weeks 2 to 4 cover, using the evals plugin in the [course repo](https://github.com/Calibre-Labs/reforge-ai-evals).

### Do we rely on LLMs to create our evals?

To draft them, yes, with human review. The rubric (what good means for your product) has to come from you and from reading real traces. LLMs help write the checks. An LLM judge has to be checked against human labels before you trust it, which is Week 4.

### How do you decide when it's the right time to put evals in place?

Earlier than most teams do. Write the rubric into the PRD before you build. Start reading traces as soon as a prototype runs on realistic inputs. Automate a check once you see the same failure more than once, and have evals running before you change models or prompts in production.

### Are there resources to help choose a model?

Public leaderboards are fine for a shortlist, but the best guide is your own eval. Use it to find the smallest, cheapest model that completes your tasks correctly: define the eval, run it on 3 to 5 models, and compare quality, cost and latency. Auto mode in a tool picks for you, which is fine for personal use. In a product you want to know which model runs each step and why.

### Do all models show a reasoning trace?

No. Most closed models now return a summary of their reasoning rather than the full chain of thought. The trace still shows every tool call with its arguments and result, plus the model's output, and that's what most evals use.

### Thoughts on Langfuse versus Braintrust for evaluating traces?

Both log traces, run code checks and LLM judges on them, and track scores over time. Langfuse is open source and can be self-hosted. Braintrust is a hosted product built around eval experiments. We'll cover trace tools in Week 5.

## Traces and Mapper

### What's a span within a trace?

One unit of work, such as one model call or one tool call. A trace is one session. A turn is one user message and everything the agent did in response, and a turn usually holds several spans.

### How do we define a session?

The developer defines it. For Mapper, a session is the whole back and forth with one user, and it ends after 5 minutes of inactivity. Other products use a conversation thread, or one task from start to finish.

### Why is "Mapper" a separate category in the trace? Can you go into detail on mappers?

Mapper is the name of our course project agent, so the trace viewer labels the agent's own output "Mapper". It isn't a type of component. Mapper takes a tech category and returns a ranked market map with sources, using five tools: get\_preferences, web\_search, read\_page, build\_market\_map and publish\_share\_link. Its PRD and traces are in the [course repo](https://github.com/Calibre-Labs/reforge-ai-evals).
