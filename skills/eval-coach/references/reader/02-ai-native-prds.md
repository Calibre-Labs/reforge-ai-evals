# Chapter 2: AI-native PRDs

In this module, you will learn how to write an AI-native PRD that defines quality criteria, golden outputs, and an evaluation rubric before your engineering team writes a single line of code.

Traditional PRDs often have a list of features in the form of user stories, their role is to facilitate a backlog of capabilities that can be built and released over time. **This tells engineers what to build but not what good looks like.** An AI can generate infinite variations of an email draft. Which ones are great?

AI agents using frontier models come out of the box with most of their core capabilities already present - but performing with low reliability.

Let’s consider how Claude Code, a terminal based coding tool, has evolved over the past year since its February 2025 release. You’ll notice that **most of the releases (5 of 7) have been performance improvements for the core capabilities that already existed at launch** - ie agentic coding.

> *Diagram idea: - categorization of Claude Code product releases based on the table below*

|  |  |  |
| :-: | :-: | :-: |
| \*\*Date\*\* | \*\*Type\*\* | \*\*New Release / Feature\*\* |
| May | Net new  | MCP connectors for external tool integrations |
| Sept | Performance  | SKILL.md — files that Claude loads to perform specialized tasks within a project |
| Oct | Performance | Agent Skills beta — pre-built skills for PowerPoint, Excel, Word, and PDF; custom skills via Skills API |
| Nov | Net new capability | Background agents and named sessions — agents can run as background tasks; session forks + cloud handoff |
| Dec | Performance  | Prompt suggestions, .claude/rules/ support |
| Jan 2026 | Performance  | MCP Tool Search lazy-loads to reduce context usage |
| Feb | Performance | Claude Opus 4.6 with 1M token context window, multi-agent collaboration, automatic memories |

Since the v1 of an agentic product already has a lot of its underlying features present, **AI PRDs focus significantly on quality definitions and performance scores.**

AI PRDs are not the first step in the development cycle. They should be written only after initial "vibe checks" (manual prototyping) and prompt testing have been conducted to establish what's possible.

### Comparing PRD Approaches

The core shift is that a traditional PRD describes a system someone will build. An AI-native PRD describes the quality bar a probabilistic system has to meet — and the mechanism for knowing whether it does.

> *Diagram idea: - key differences between traditional and AI-native PRDs based on the table below*

|  |  |  |
| :-: | :-: | :-: |
| \*\*Traditional PRD section\*\* | \*\*AI-native equivalent\*\* | \*\*What changes\*\* |
| Goals and success metrics | Evaluation Rubric | Moves from engagement metrics (DAU, conversion) to criteria for quality (% accuracy, hallucination rate, latency in ms) |
| User stories / use cases | Golden outputs | Instead of describing what users want to do, you show concrete input/output examples of "great"  |
| Functional requirements | Prompt logic & tool specification | Instead of feature behaviors, you define system instructions, tool APIs the agent can call, and graceful failure rules |
| UX spec | – | Replaced upstream by a prototype  — design is implicit in the golden outputs |
| – | Edge case handling | What the model should do when it failsEarly findings from the prototype that already  |
| Open Questions | Dataset Strategy | Unknowns replaced by new datasets needed to improve the agent |

Here’s more about 3 vital new components of an AI-native PRD: golden outputs, eval rubrics and the dataset strategy:

**Golden outputs**

These anchor the team’s understanding of quality. Every feature should include concrete examples of both strong and weak outputs. Strong examples show what “great” looks like. Weak examples clarify boundaries and failure modes. These examples should include messy cases: incomplete inputs, contradictory instructions, and ambiguous context. Those are the situations where quality decisions matter most.

**Evaluation rubric**

translates intuition into shared standards. At this stage, rubrics are intentionally vibe-oriented. They describe what matters and why, not how measurement will be automated. A good rubric makes clear what accuracy means for your domain, what tradeoffs are acceptable, and which failures are never allowed. Automation comes later; clarity comes first.

In our sample AI PRD coming up below, you will see that the evaluation rubric is explicit: categorization accuracy above 92%, sentiment precision above 85%, latency under two seconds, hallucination rate at zero.

**Dataset curation strategy**

This begins as exploration. Early examples are never sufficient. As real users interact with the system, you will discover variation you did not anticipate. Your spec should include a plan for capturing and labeling these cases to better understand who your users are, how they differ, and where the system struggles. Over time, this exploration produces a dataset that reflects reality rather than assumptions.

Instead of being theoretical, **the PRD your engineering team starts working on should have golden output examples from a diverse set of inputs.** This makes it critical for PMs to be able to prototype and vibe check ideas before they write a formal PRD. **Learn more about managing these datasets and continuously updating our PRDs in module 8.**

> *Diagram idea: showing key components below of an AI-PRD with snippets as examples*

Below is what a **brief but complete AI PRD (written after prototyping and combined with a 50 row golden dataset)** for our Support Triage Agent would look like. It has the following sections:

*1. Problem & Business Value*

*2. Prompt Logic & Dataset*

*3. Tool Specification*

*4. Evaluation Criteria*

*5. Edge Cases Handling*

*6. Prototype & Early Findings*

*7. Technical Constraints*

|  |
| :-: |
| \#\#\# Sample AI PRD: Support Ticket Triage (v1.0)\*Owner:\* \*\\\[Name\\\]  \|\* \*Status:\* \*Prototyping  \|\* \*Default Model:\* \*Gemini 3 Flash Preview\*\*\*\*1. Problem & Business Value\*\*\*\*Support leads spend about 4 hours per day manually tagging tickets. This creates a lag before specialists can see high-priority issues. Our solution is a background agent that autonomously classifies tickets in real time by Intent, Sentiment and Urgency\*\*\*\*2. Prompt Logic & Dataset\*\*\*\*System Instruction Summary - You are a support analyst. Categorize incoming tickets into one of three buckets: Technical, Billing, or Feature Request. Assign a sentiment (Positive, Neutral, Frustrated, Angry) based user frustration. If sentiment is Frustrated or Angry, immediately flag for human override, regardless of category.\*\*Golden Dataset:\* \*Attached: 50 historical tickets with "Gold" labels for few-shot prompting.\*\*\*\*3. Tool Specification\*\*\*\*The agent should have access to the following APIs before making a triage decision:\*\|  \|  \|  \|  \|&#10;\| :-: \| :-: \| :-: \| :-: \|&#10;\| \\\*\\\*\\\*Tool Name\\\*\\\*\\\* \| \\\*\\\*\\\*Action\\\*\\\*\\\* \| \\\*\\\*\\\*Input Param\\\*\\\*\\\* \| \\\*\\\*\\\*Purpose\\\*\\\*\\\* \|&#10;\| \\\*User\\\\\\\_Lookup\\\* \| \\\*Query internal database\\\* \| \\\*user\\\\\\\_email\\\* \| \\\*Check whether the user is a VIP or Enterprise customer to escalate priority.\\\* \|&#10;\| \\\*Subscription\\\\\\\_Check\\\* \| \\\*Stripe/Billing API\\\* \| \\\*customer\\\\\\\_id\\\* \| \\\*Confirm active paid plan before routing to Priority Tech Support.\\\* \|&#10;\| \\\*Jira\\\\\\\_Search\\\* \| \\\*Jira API\\\* \| \\\*keyword\\\\\\\_string\\\* \| \\\*Check for an existing Active Incident or Known Bug matching the complaint.\\\* \|&#10;\| \\\*CRM\\\\\\\_Write\\\* \| \\\*Salesforce/\\\*\\\*  &\#10;\\\*\\\*HubSpot API\\\* \| \\\*ticket\\\\\\\_id, tag\\\* \| \\\*Write final classification and sentiment score to the CRM record.\\\* \|&#10;\*\*\*4. Evaluation Criteria\*\*\*\|  \|  \|  \|&#10;\| :-: \| :-: \| :-: \|&#10;\| \\\*\\\*\\\*Metric\\\*\\\*\\\* \| \\\*\\\*\\\*Target\\\*\\\*\\\* \| \\\*\\\*\\\*Why It Matters\\\*\\\*\\\* \|&#10;\| \\\*Categorization Accuracy\\\* \| \\\*\\\\\\\> 92%\\\* \| \\\*Avoid routing Billing issues to Dev teams.\\\* \|&#10;\| \\\*Sentiment Precision\\\* \| \\\*\\\\\\\> 85%\\\* \| \\\*Avoid false alarms on frustrated users.\\\* \|&#10;\| \\\*Latency\\\* \| \\\*\\\\\\\< 2s\\\* \| \\\*Must be faster than manual triage.\\\* \|&#10;\| \\\*Hallucination Rate\\\* \| \\\*0%\\\* \| \\\*It should never invent ticket IDs or usernames.\\\* \|&#10;\*Course Note: standard out-of-the-box evals like LLM tone/helpfulness are not primary success metrics for this workflow.\* \*\*\*5. Edge Cases Handling\*\*\*  - \*\\\*Low-confidence fallback: If model confidence is \\\\\\\< 0.7, do not auto-tag. Move ticket to Needs Human Review.\\\*\*&#10;  - \*\\\*Drift monitoring: Run a weekly manual audit on 5% of AI-tagged tickets.\\\*\*&#10;  - \*\\\*User feedback loop: Add a support-side prompt: Is this tag correct? \\\\\\\[Yes/No\\\\\\\].\\\*\*\*\*\*6. Prototype & Early Findings\*\*\*\*Link to Internal Demo and Early findings:\*  - \*\\\*Very short inputs (for example, "Help\\\\\\\!") cause category hallucinations. Add a clarification-needed mode.\\\*\*&#10;  - \*\\\*About 20% of tickets contain two issues (for example, "I can't log in and I need to update my billing info"). The current model picks only the first issue, so we need multi-label classification instructions.\\\*\*&#10;  - \*\\\*The model struggled with sarcasm. We added 5 sarcastic complaint examples to the Golden dataset for few-shot learning via the system prompt.\\\*\*\*\*\*7. Technical Constraints\*\*\*  - \*\\\*Data privacy: Scrub all PII (email addresses, phone numbers) with a regex preprocessor before sending to the LLM API.\\\*\*&#10;  - \*\\\*Cost per ticket: Keep categorization cost below $0.01 to maintain ROI.\\\*\* |

### When the Agent Should Say "I Don't Know"

Most PRDs define what the agent should do when things go well. Fewer define what it should do when it doesn't know. **That gap produces hallucinations — not because the model is broken, but because no one told it that admitting uncertainty was an option.**

The "I don't know" threshold is a product decision- it belongs in the PRD, and it differs by domain:

  - A legal document assistant that fabricates a case citation is a liability.
  - A brainstorming tool that hedges on every suggestion is useless.
  - The right threshold depends on the failure mode you're most afraid of.

> *Diagram idea: Two-axis matrix for Agent Response in Low Clarity Scenarios — confidence threshold vs. failure cost. Conservative (admit uncertainty early) for high-stakes domains; permissive (synthesize and caveat) for exploratory domains.*

The conservative approach applies to legal, medical, financial, and compliance-adjacent products. The agent declines to answer:

  -  if the relevant information isn't in the top retrieved documents
  - if retrieved sources contradict each other, or
  - if the evidence is ambiguous.

 "I don't have enough information to answer this accurately" is a success state, not a failure.

The permissive approach applies to research, brainstorming, and exploratory tools.

**How to specify this in your PRD:** Define the confidence threshold per query type and the exact language the agent should use when declining. "Your question falls outside what I have reliable information on" is more useful than "I don't know." Also specify what the agent should surface instead:

  - a fallback path
  - a suggested query reformulation, or
  - an escalation

**How to measure it: Track the "I don't know" rate in production.** A rate above 30% means retrieval is failing and users are hitting dead ends. A rate below 5% in a knowledge-bounded system is a signal the agent is filling gaps with fabrications rather than admissions. For most enterprise applications, 10–20% is the target range.

### The Solution-space shift and Trace Analysis

AI product work requires more time **defining and refining the solution** than traditional PM roles did. You still need to own the primary understanding of the problem, but the heavy lifting is in defining and measuring quality. Spending time prototyping and building an intuition for the failure modes of an agent is very much solution-focused.

This brings us to Trace Analysis - reviewing the full record of an interaction between a (user) input and LLM generated outputs.

**As we dive into module 4,** we’ll see that PMs working on AI products spend significant amounts of time not just testing prompt variations but also

  - Personally reviewing traces to identify patterns

<!-- end list -->

  - Writing and iterating on evaluation rubrics
  - Labeling datasets to calibrate automated judges

Teams that let ML engineers exclusively own this work discover quickly that "product taste" matters and development is slowed down. An engineer can implement your rubric, but they can't define what "great" means for your users. As a PM that's your job.

## Recap and Further Learning

### Key takeaways and definitions

  - **Focus on Quality, Not Features:** Traditional PRDs list features and user stories, telling engineers *what* to build. AI-native PRDs focus on quality definitions and performance scores, telling them *what good looks like*.
  - **The Development Cycle Shifts:** AI PRDs are written *after* initial "vibe checks" (manual prototyping) and prompt testing have established what's possible.
  - **PM Role Changes:** AI product work requires Product Managers to spend significant time defining and refining the solution by prototyping, personally reviewing traces, writing evaluation rubrics, and labeling datasets.
  - **Performance is the Primary Release Type:** Most releases for AI-native products are performance improvements for existing core capabilities, reflecting the need for continuous quality refinement.

**AI-native PRD****
**Describes the bar a probabilistic system has to meet, focusing on quality definitions and performance scores, and should be written after initial prototyping.

**Golden outputs****
**Concrete examples of strong and weak input/output pairs used to anchor the team's understanding of quality and clarify failure modes.

**Evaluation rubric**
Shared standards that translate product intuition into measurable criteria like accuracy, hallucination rate, and latency. Clarity of the rubric precedes automation.

**Dataset curation strategy****
**A plan for capturing and labeling real user interaction data to continuously discover variation and improve the agent.

**Trace Analysis****
**The process of reviewing the full record of an interaction between a user's input and the LLM's generated outputs.

### Recommended articles

  - [How to write a good Agent spec](https://addyosmani.com/blog/good-spec/) by Addy Osmani, Google

In the next module, we will learn how to read agent traces systematically — clustering failure patterns into codes and knowing when you’ve seen enough to move to automation.
