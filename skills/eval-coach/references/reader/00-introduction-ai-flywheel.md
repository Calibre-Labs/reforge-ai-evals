# Introduction: The AI Flywheel

You’ve built an AI feature that performed well in early demos.

**A small set of customers responded positively, internal stakeholders were aligned, and you decided to open it up to a broader audience.** Here’s what happens next to most agent teams:

  - Once users start trying it, the picture gets muddied - some love it, but others are complaining or never returning.
  - Product Review is tomorrow and you realize you’ve got a big problem: you have no idea if the AI is actually doing good work consistently.
  - Leadership asks you exactly how you are tracking progress and you don’t have a clear answer.

 > *Diagram idea: Show a transition from sankey flows to a distribution*

In the past, you would have relied on product usage metrics as the feedback loop after launch but this fails to work now:

  - Traditional software was designed to guide users through a single "happy path". AI-native products behave differently.
  - Each interaction produces a wide distribution of personalized outcomes for every user and they don’t work the same way 100% of the time.

<!-- end list -->

  - The usage metrics don’t tell you if an AI system gave the right answer, made a reasonable decision, followed policy or handled ambiguity well.

**This evaluation gap is the defining challenge of AI product development.**

### Measuring Usage vs. Measuring Work

The PM's challenge is no longer just getting a user to the end of a flow; it's ensuring that the work performed by the AI at the end of that flow meets a high-quality bar. That requires new questions:

  - Did the system actually resolve the user’s intent, not just respond?
  - Did it make the right tradeoffs under uncertainty?
  - Did it follow constraints that matter to this customer, in this context?
  - When it failed, did it fail in acceptable ways?

None of these show up cleanly in engagement metrics. **We need a new system called AI Evaluation.**

### Evaluating Models vs Applications

> *Diagram idea: 2 layer AI Eval stack for models and apps based on content below*

Evaluation is needed at every layer of the AI stack - models and applications.

**Model layer:** Model benchmarks evaluate what an LLM can do in isolation and whether it behaves responsibly. These assessments answer questions like whether the model can reason, follow instructions, or avoid harmful outputs. They are largely standardized, owned by model providers or research teams, and change slowly relative to product iteration.

**Application layer:** App or product quality is where judgment enters the picture. This layer needs to judge whether the system’s outputs meet user expectations in real contexts. It includes questions such as whether the output is accurate, whether it correctly identifies the user’s intent, whether it is clear and fast and helpful, and whether a reasonable user would accept it as “good.”

**This course on AI evaluation will primarily focus on evaluation of the application layer - measuring and improving product experience.** Experience is where applied AI products differentiate. No external out-of-the-box model benchmark can define accuracy or quality for your domain. That work belongs to product leaders.

### Your Role Has Changed

Building AI products requires you to transform yourself and your role as a PM. **You are no longer just focused on the problem being solved.** You're the person who defines what "good" work output looks like, builds the eval rubric to score it, and helps create a prioritized roadmap for improving the product’s performance against that score.

This requires new skillsets: an intuition for how agents work and the ability to measure their quality.

Engineering a consistently high-quality AI experience that stands up to real-world scrutiny is incredibly difficult. It requires a new approach to the product development lifecycle - what we call the [AI Flywheel](https://blog.calibrelabs.ai/p/building-an-ai-product-flywheel) - A system for consistently improving AI product quality over time, that combines analytics, user research and evaluation.

### Designing the AI Flywheel

The best AI products don’t magically start great, they build the flywheel system to consistently improve over time. Here’s what that roughly looks like in practice (no one-size-fits-all) starting with a new north star metric to track success.

> *Diagram idea: 5 phase AI Flywheel based on the content below*

This AI Flywheel has 5 phases:

1.  Agent Success Rate - a composite metric that measures agent output and serves as the primary goal/north star metric
2.  Trace Analysis - the process of reviewing the product logs to find patterns within them
3.  Reference Datasets - comprehensive datasets across different user intents that indicate edge cases and golden outputs
4.  Offline Evaluation - tests that help calibrate improvements or regressions in the new versions of an agent before release
5.  Online User Monitoring - scoring live user experience against our evaluation criteria and gathering feedback

**⭐️ Agent Success Rate - the new north star metric**

To measure work, your new north star metric should be a composite metric that can take into account user feedback (thumbs up/down), user actions (download/ accept), and semantic analysis of the conversation (repeated prompts, frustration, etc). You will still be left with a significant portion of sessions with an unknown level of success - that’s ok, this uncertainty is our new reality.

For products where there is a verifiable outcome, the metric can be simpler for eg: % ticket resolution rate for customer support or % code suggestions accepted without edits.

**ð Trace Analysis - the new source of truth**

A trace is the full record of user inputs and LLM outputs in every product session. Analyze a sample of traces aligned to each of the primary user intents you are designing your agent for.

Coding traces allows us to build a view of what error modes matter - and which to prioritize to most quickly improve our Agent Success Rate\!

**ð️Reference Datasets - golden outputs and edge cases**

Trace analysis reveals the gap between what you thought users are doing and the actual diversity of their interactions. A term borrowed from search analytics, user intent mapping allows you to categorize natural language inputs based on the user’s goals. For eg: the user intents for a customer support bot would include things like getting replacements, refunds, information vs updating sensitive information like payment.

Use these to create comprehensive reference datasets - including golden outputs and edge cases for evaluation.

**ðOffline Evals - unit tests for agents**

Evals are unit tests for your agent and you must have them. It’s hard to make offline evals (especially for long running agents) realistic but the closer you can get, the faster you can ship.

Without reasonable offline evals, you simply can’t test small changes to your agent architecture and prompts. Realistic and well maintained offline evals are essential for getting better at context engineering as a team.

**⏺️ User Monitoring & Feedback - logging the signals**

Real world AI usage is messy and often surprising for new features. Nothing can replace actual monitoring and (anonymized) semantic analysis of user sessions to make sure your agent is working in the wild. This observability layer should drive how you track Agent Success Rate, closing the loop on our AI Flywheel.

### Leading AI Evaluation

Evals are central to the new AI product Flywheel. As product managers, you must "lead from the trenches," personally reviewing traces and writing evaluation rubrics rather than delegating these tasks solely to ML engineers.

## Recap and Further Learning

### Key takeaways and definitions

  - **Workflows to Work:** The transition to AI-native products requires evaluating the quality of work performed by the AI, shifting away from measuring usage paths.
  - **Judging output:** AI Evaluation addresses this gap by judging outputs based on user expectations and real-world contexts.
  - **Quality leaders:** PMs must transition from problem focused to quality architects who define "great” output and build evaluation rubrics.
  - **The AI Flywheel:** build the core system for improvement, encompassing five key components: Agent Success Rate (north star), Trace Analysis (source of truth), Reference Datasets, Offline Evaluation, and Online User Monitoring.

**Golden Outputs**
A set of ideal, human-verified responses or outputs that define the quality standard for an AI system

**AI Flywheel****
**A system for consistently improving AI product quality over time, that combines analytics, user research and evaluation.

**Context Engineering**
The process of defining and refining the input context provided to an AI agent, including its system instructions, tool specifications, and realistic few-shot examples

### Recommended articles

1.  [AI flywheel by Calibre Labs](https://blog.calibrelabs.ai/p/building-an-ai-product-flywheel)
2.  Independent agent and model evals that represent new frontiers:

    1.  [METR](https://metr.org/)
    2.  [GDP-Val](https://openai.com/index/gdpval/)
    3.  [Terminal-Bench](https://www.tbench.ai/)
3.  [Role of traces in AI software by Langchain](https://blog.langchain.com/in-software-the-code-documents-the-app-in-ai-the-traces-do/)

In the next module, we will learn how the three stages of the AI eval lifecycle — vibe checks, offline evals, and user monitoring — map to the stages of building an AI product.
