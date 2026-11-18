**

# AI Evals Week 3 FAQ: automated evals

Answers to every question from the Week 3 chat and Q\&A on Nov 4, grouped by topic, including the ones we didn't get to live.

## Our favorite question

### Who decides whether a trace code gets a prompt fix, a harness fix or an eval, and which kind of eval? Is it an engineering decision?

It's shared, and the three questions from the session split the work. The PM or domain expert owns the first one: was the agent clearly told what to do? If not, that's a specification gap, and the PM updates the rubric so the prompt can be fixed. The second question is mostly engineering's: does the agent have what it needs (a tool, the right information, a harness step that passes it along)? If not, engineering changes the harness. If the answer to both is yes and it still works only some of the time, you write an eval. The PM says what good looks like and brings examples of passes and fails. Engineering helps decide how to check it reliably. One failure Justin sees often: PMs skip asking whether a code check could do the job. A domain expert can usually find a simple rule if they look for one.

## Fix, check or judge

### How does a harness fix work technically? Is it a code change?

Yes. The harness is the code around the model. For the dead links (TC-1), Mapper searched in one model call and wrote the map in a second call that can't search. The first call wasn't passing its sources to the second, so the second wrote links from memory. The fix changed the code between the two calls: it turns each search result into the real page address and hands the writing step a numbered list of sources to cite from. Dead links went from 28 to 0 across 30 test sessions, with no prompt change.

### For the broken links, did a tool call need to happen for the harness to pick up the real links?

The search tool call was already happening. The problem was that its results weren't passed from one model's work to the next. That's a very common error in multi-step agents, and it's why reading the trace (what each step actually saw) matters more than reading the final answer.

### How do trace codes relate to the rubric? I thought trace codes became part of the rubric, and then we wrote evals on them.

The rubric is a high-level summary of what good looks like, usually no more than a dozen lines. Trace codes are detailed and specific, and over time you may have hundreds. Each code maps roughly to part of the rubric, but it's not one-to-one. Some codes show a gap in the rubric. Mapper giving investment advice was one, so we added a line in rubric v2. Many codes are just bugs. The rubric won't say "don't make up links" or "ask the right scoping question", and it doesn't need to. Think of the list of trace codes as your issue backlog. Each one ends up as a rubric update, a prompt or harness fix, an eval, or some mix of the three.

### Once a judge shows a trace code scores low, is the PM's job done? Does engineering still have to fix the agent?

Yes, and the score is what makes that hand-off work. Without data, quality is subjective: you look at one session and say you don't like it, and an engineer may not see the problem. With a judge you can both trust, you can say "metric scope passes 33% today, and we don't release until it's at 80%". Engineering decides which experiments to run, since the cause may be a prompt, a tool call or something else in the harness. The same judge then tells everyone whether a change worked.

### Is this relevant for a new product that hasn't launched, or only after launch?

Both. You need traces either way. Before launch more of them will be synthetic, from your team, design partners and generated inputs. After launch you add real user sessions.

### What's the definition of a trace code again?

A short name for a recurring pattern you notice while reviewing traces, with real examples attached. Most are failures, but they can be things the agent does well. Justin's shorthand: it's your new backlog.

## Code checks

### Are code checks the same as harness checks?

No. A code check is an eval: a traditional software function, with no LLM involved, that reads an agent's output or trace and returns pass or fail. For example, is more than half of any column empty? A harness check runs inside the product while it works, for example dropping any link that isn't on the list of sources. The two often pair up: the harness prevents a failure, and a code check measures that it stays prevented.

### The half-empty columns check only tests whether numbers are present. How do you check that they're correct?

That needs a different eval. Correctness means comparing each figure with an authoritative source, so it takes judgment and usually an LLM judge that reads the cited page against the claim (rubric line O2, figures with no source behind them). This is why code checks and judges are used together: a map can pass every code check and still have wrong numbers.

### Why did the half-empty columns score drop from v1 to v1.1?

It was one session out of 30, so roughly 3 points. The v1.1 fixes targeted other codes (dead links, past and future years, investment advice), not empty columns. Mapper's output also varies from run to run, so a one-session swing on 30 sessions is noise. That's one reason Week 4 grows the dataset, so differences between versions mean something.

## LLM judges

### Is intent understanding a good candidate for an LLM judge? Did the agent understand the kind of question the user asked, especially when the input is a little ambiguous?

Yes. Intent handling is a common judge: did the response address what the user asked, and did it ask a clarifying question when it should have? Mapper's version is TC-5, asks the wrong scoping question, which needs a judge.

### Does a reference-free judge have a rubric?

Yes. It still has a rubric. What it doesn't have is a reference answer to compare against.

### If a reference-free judge compares the output against the rubric and the trace, doesn't that mean you already hold the right answer?

No. You've defined the standard, but you haven't supplied the answer. The judge uses the rubric plus the context and evidence in the trace (what the agent searched, what the pages said) to decide whether the output meets that standard. For metric scope, it doesn't know Oracle Health's revenue. It can still see that a figure is labeled as Oracle's total revenue and fail it.

### Why don't we annotate the judge's decisions to steer it?

We do. That's the agree or disagree step on the results page in the demo. Those labels show how closely the judge matches your judgment and tell you how to change the judge prompt. It's the AI quality flywheel applied to the judges themselves. Week 4 covers the full process with the [llm-align skill](https://github.com/Calibre-Labs/reforge-ai-evals/tree/main/skills/llm-align).

### Human review isn't scalable. How do you scale?

You review enough to set the standard, then hand the volume to checks and judges that can run on millions of sessions. Human labels are what you measure a judge against, so you keep reviewing a sample. For truly cutting-edge capabilities, human review is sometimes the only thing that works. Sandhya's example: Google relied on it to get face consistency right in its Nano Banana image model.

### Next week, are we improving the low scores, like metric scope?

First we make sure we can trust the judges: aligning each LLM judge so it scores the way a person would. Then we use them to improve Mapper and check whether each change worked.

## Tools and setup

### Can I use Codex?

Yes. The skills work with any coding agent, including Codex and Cursor. Point your agent at the [course repo](https://github.com/Calibre-Labs/reforge-ai-evals), or install the skills with [npx skills](https://github.com/Calibre-Labs/reforge-ai-evals#install).

### My company doesn't allow third-party plugins, and I use Cursor. Can I use the skills directly?

Yes. Copy any folder in skills/ into your agent's skills directory. The skills read and write plain files (markdown, CSV, JSON, HTML), so you don't need an eval platform account. See the [Install section](https://github.com/Calibre-Labs/reforge-ai-evals#install) of the repo README.

### Were the pages Sandhya showed generated by the eval plugin?

Yes. The check page, the judge page and the scores page all came from the [eval-code](https://github.com/Calibre-Labs/reforge-ai-evals/tree/main/skills/eval-code) and [eval-llm-judge](https://github.com/Calibre-Labs/reforge-ai-evals/tree/main/skills/eval-llm-judge) skills, run in Claude. The templates ship with the skills, and you can change the design however you like.

### What are some examples of AI ops tools?

Arize Phoenix, Langfuse, LangSmith and Braintrust are common choices for storing traces, datasets, annotations and eval runs. We're vendor agnostic, and we'll start showing a couple of tools next week. Most connect to a coding or coworker agent through an MCP server, so you can keep doing the work in the setup from today's demo.

### Do you follow a spec-driven development (SDD) method when building AI features?

A lightweight version: write the PRD and rubric first, then iterate. The key difference for AI products is that the spec has to keep changing as you learn from traces. A classmate pointed out that most SDD methods also link intent to code, which this doesn't do on its own. Human review fits in as the step that tells you when the spec needs to change.

### How do you stay on top of which model to use for which task?

Start with public benchmarks, then try a few models yourself and run your own evals. Justin runs evals from this course on the tasks his personal agents do most often. Sandhya's current favorite is Opus 5.5. She uses medium effort for step-by-step work and high effort when she wants the agent to do all the work and come back with results.

### Can we get the prompts from the demo?

Here are the ones that did the work, with Mapper's names swapped for placeholders. Paste them into a session with the ai-evals plugin installed and your dataset and trace codes where the agent can read them.

1.  Summarize your understanding of trace code \[N\] for me. I want to use our AI Evals plugin to write a code-based check for it.
2.  Use the eval-code skill to write a code check for \[trace code\]. Fail a session if \[rule, for example: any column in a market map has more than half its cells empty, where empty means blank, N/A, "Not specified", "Not disclosed", "Unknown" or a dash\]. Pass sessions where it doesn't apply. Don't run it yet.
3.  In three short bullets: what does your check read, what does it count as \[failing\], and what's the rule?
4.  Run it on all \[30\] rows of the dev dataset. Give me the pass rate, which sessions fail, and why.
5.  I want to write an LLM judge for trace code \[N\]. Summarize the code for me, and let's plan the judge together.
6.  Use the eval-llm-judge skill to write the judge. \[What passes and what fails, in a sentence or two.\] Use \[a real failing example from your traces\] as a fail example. Pass or fail, with a short critique first. Don't run it yet.
7.  Walk me through your judge prompt in six lines: the context, the question, what passes, what fails, the examples, and what it returns.
8.  Run the judge on the dev dataset. Show me each session's verdict with one line on why, and hide the full critiques for now.

### I'm new to Claude Code. What should I do before next week to get hands-on?

Start small and build up. First, ask ChatGPT or Claude a question where you can judge the answer thoroughly, and write down why it was good or bad. That's the core skill. Next, write a skill for something you do repeatedly, run it over a handful of sessions, evaluate them, change the skill and compare. Then build a very simple agent. The use case doesn't matter, you're learning the plumbing. You can also open Claude, say what you want to learn, give it the course repo and this course, and ask it to walk you through it step by step. Give yourself an hour.
