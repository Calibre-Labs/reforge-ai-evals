# Ch 6: LLM-Judge based Evaluation

In this module, you will learn how to design narrow, binary LLM-as-Judge evaluators for the quality dimensions that code can’t reach — tone, actionability, and factual grounding.

**An LLM judge is essentially a second model call that evaluates the output of your first model call.**

  - It takes a trace as input — or more precisely, the agent's output plus whatever additional context the criterion requires
  - It returns a binary verdict: Pass or Fail, plus a reasoning string.
  - The verdict is not deterministic. Run the same judge twice and you may get a different result. That's the tradeoff.

You're buying the ability to measure subjective quality, at the cost of the perfect reproducibility that code evals provide.

**The economics are different from code evals.** An LLM judge costs inference on every run. On a 50-ticket dataset with three judges, that's 150 model calls per experiment. This means judges should run after code evals pass — not instead of them — and should be targeted at the specific quality dimensions you've identified through trace analysis.

This chapter covers what LLM judges look like, the two types you'll build, how to apply them to the Support Triage Agent, and how to integrate them into your release process.

### When to use LLM-as-Judge

A large share of quality metrics that users care about is not rule-like:

  - A support reply can be factually correct and still feel dismissive in a way that decreases CSAT.
  - A generated UX can be accurate but still feel like “slop”. A summary can contain the right points and still miss what the user actually needed.

In practice, teams hit this ceiling quickly. They can prevent obvious failures, but they still cannot answer questions like:

  - Would a user accept this without rewriting it?
  - Is this specific enough to take action on?
  - Is it appropriately asking for permissions - or doing too much or too little?

This is where LLM-as-Judge evaluators enter. **The model now also becomes your evaluator: reasoning about quality instead of just generating content.** But building a reliable custom judge is unglamorous, foundational work that teams are often tempted to skip in favor of "out-of-the-box" evals - that are rarely actionable.

### Common Categories for LLM-Judge Evals

> *Diagram idea: diagram — examples of trace codes that require LLM-judge evaluation, with contrast to code-based evals*

Not every subjective quality property is equally well-suited to LLM judging. Four categories show up across products and consistently require a judge rather than code.

**Tone and empathy gaps**
These appear when the agent's response is technically correct but fails the human interaction. A billing response that resolves the issue but ignores the customer's frustration. A support reply that's accurate but clinical when the situation calls for warmth. These properties have no regex equivalent.

**Directness and actionability failures** **
**These surface when the agent hedges, over-qualifies, or provides information without telling the user what to do next. "Your account may have been affected" where "Your account was charged twice — here's how we'll fix it" is what's needed. Code can check for the presence of a next step, but only a judge can assess whether it's genuinely actionable.

**Factual grounding & memory problems** **
**In search-based systems, lack of grounding results in the agent making claims that contradict retrieved context, overstating confidence, or omitting information that was in the retrieved documents and should have been included. Evaluating these requires reading both the output and the source material — called a reference-based LLM judge.

**Semantic completeness** **& context management****
**This matters when outputs must address all parts of a multi-part question or request. Did the summary cover all the key decisions from the document? Did the recommendation address both the immediate issue and the underlying cause? Did any context get lost after compaction or truncated? Pattern matching can check for keywords. A judge can determine whether the substance is there.

### What an LLM Judge Looks Like

> *Diagram idea: diagram — LLM judge anatomy based on below: inputs → judge prompt → LLM call → output*

**Every LLM judge has the same four-part anatomy.**

**Inputs: the trace plus optional reference.** An LLM judge takes two kinds of inputs: the agent's output (the trace) and, optionally, a reference — which is either the original user input, a ground truth answer, or retrieved context. What you pass in determines what the judge can measure:

  - A judge that only sees the output can evaluate tone, format, and directness.
  - A judge that sees the output and the user's original query can evaluate relevance and responsiveness.
  - A judge that sees the output alongside a reference document can evaluate factual accuracy and grounding.

**The judge prompt: role, criterion, standard, examples.** The prompt positions the model as an auditor, not an assistant. It defines the single criterion being evaluated, provides observable pass/fail standards, and includes boundary examples that teach the judge where the line is. A vague judge prompt produces unreliable scores.

**The LLM call: reasoning before verdict.** Use a reasoning model where possible. The chain-of-thought that precedes the verdict is your debugging interface. When the judge disagrees with your human reviewer on trace \#23, reading the judge's reasoning tells you whether the judge misunderstood the criterion, hit an edge case the examples didn't cover, or is actually right and the human reviewer was inconsistent.

**The output: Pass or Fail, plus a reasoning string.** The reasoning string is not optional. "Fail" with no explanation is useless at scale. "Fail — response opens with account status rather than acknowledging customer frustration; no empathetic framing before resolution" tells you exactly what pattern failed and where to look in the prompt.

#### **Example 1: Tone check for Support Triage**

The trace analysis for the Support Triage Agent surfaced a specific failure pattern: on high-severity billing tickets, some responses were

  - Technically correct but tonally flat:

<!-- end list -->

  - No acknowledgment of frustration.
  - No urgency.

Code can confirm that a response includes the words "I understand" — but it can't tell whether that acknowledgment is specific to the customer's situation or generic filler.

> *Diagram idea: diagram — show the LLM judge prompt below for check\_empathetic\_acknowledgment, nicely formatted on a slide*

|  |
| :-: |
| SYSTEM: \\\#\\\# You are auditing support responses for tone appropriateness. Evaluate only whether the agent acknowledges customer frustration before providing a resolution.  USER: \\\[Customer ticket\\\]: > *Diagram idea: user\\\_input* \\\[Agent response\\\]: > *Diagram idea: agent\\\_output*  Does this response begin with a specific, empathetic acknowledgment of the customer's concern before providing a resolution?  \\\#\\\# Rules: \\- "I understand" or "I'm sorry to hear" alone does not qualify. The acknowledgment must be specific to the customer's situation. \\- Jumping directly to resolution without acknowledgment = Fail. \\- Generic sympathy without addressing the specific issue = Fail. \\- Specific acknowledgment followed by a clear resolution path = Pass.  \\\#\\\# Examples  \\\[PASS\\\]: "That's frustrating — being billed twice after an upgrade is exactly the kind of thing that shouldn't happen. Here's how we'll fix it immediately..."  \\\[FAIL\\\]: "I understand your frustration. Please follow these steps to reset your password."  \\\[FAIL\\\]: "Thanks for reaching out. Your account has been flagged for review." Think step by step. Then return JSON with exactly two keys: {"verdict": "Pass" or "Fail", "reasoning": "..."} |

The practical threshold: if a reviewer needs to hold the original user request in mind and compare it to the output — or reason about tone, intent, or quality — that's an LLM judge. If you can write the success condition as a Python function in under ten lines, it belongs in code.

### Reference-Free vs Reference-Based Judges

Every LLM judge falls into one of two categories, and the distinction shapes what evidence you need to build it.

> *Diagram idea: diagram — reference-free vs reference-based judge taxonomy, pros and cons with examples for each*

**Reference-free judges** evaluate the output on its own merits. They don't need to know what the correct answer looks like — they assess properties of the output itself:

  - Is it direct?
  - Is the tone appropriate?
  - Does it include a concrete next step?
  - Does it make an unsupported claim?

Reference-free judges can be built as soon as you have representative traces. You don't need a labeled dataset.

**Reference-based judges** compare the agent's output against something external — the original user query, a ground truth answer, or retrieved context chunks. The hallucination guard from module 6 was a code-based reference-based eval: it compared output ticket IDs against input ticket IDs. Reference-based LLM judges do the same thing for properties that can't be checked with a regex:

  - Does the response accurately reflect the content that was retrieved?
  - Does the category label match what a domain expert would assign?

**The practical implication:** reference-free judges can be built immediately from any representative traces. Reference-based judges require ground truth — either expert-labeled outputs or access to the retrieved context at inference time.

**If you're early in your eval development and don't yet have labeled data, start with reference-free judges.** Use them to build your dataset. Add reference-based judges once you have reliable ground truth to compare against.

## Principles of LLM-Judge Design

> *Diagram idea: diagram — principles of LLM-Judge design based on below: narrow scope, binary decisions, custom defintion*

The decision to build an LLM judge comes from module 5’'s diagnostic: you've identified a generalization gap where the system works sometimes but not consistently, and the quality criterion requires subjective assessment that code can't capture.

**LLM-as-judge must be used in extremely narrow, well-defined ways. Generic "rate this output 1-10" judges are unreliable.** High-performing teams follow two strict rules:

**Binary Decisions - Judges should provide a single Yes/No decision, not a Likert scale (1-5 rating).**

  - Binary forces clarity: either this meets the bar or it doesn't
  - Binary labels are significantly easier to validate mathematically (covered later in calibration section)
  - Instead of one complex eval with a scale of 1-5, break down evaluations into several binary decisions

**Why not Likert - Likert scales (1-5 or 1-10 ratings) have several problems.**

  - They’re expensive to align with domain experts because you need agreement on what each number means.
  - Annotators tend to default to middle values to avoid making hard calls.
  - They encourage vague, broad criteria like “overall quality” instead of targeted failure modes.

**Narrow Scope - A judge should assess one custom trace category at a time.**

If a prompt lists more than a few criteria, it almost always becomes inconsistent. You’ll also lose the ability to diagnose what changed when scores move.

  - Focused tasks are easier for an LLM to reason about consistently
  - Narrower scope improves accuracy (typically 10-15% better than comprehensive judges)
  - Separate judges enable better root cause analysis (you can see exactly which quality dimension failed)
  - Easier to calibrate and validate each judge independently

### What to Judge: Start With What You Can Teach

Not every subjective category is a good judge candidate. **Start with categories where you can clearly “show” the ambiguous boundary between pass and fail with examples.**

Good candidates tend to look like:

  - “Does the response include a concrete next step?”
  - “Does the response directly answer the user’s question without deflecting?”
  - “Is the tone appropriate for a professional customer interaction?”
  - “Does the output make claims that are unsupported by the provided context?”

Bad candidates tend to be fuzzy:

  - “Is this high quality?”
  - “Is this delightful?”
  - “Is this insightful?”
  - “Is this creative?”

If you can’t write down what a pass looks like in plain language and then provide a few crisp examples, you’re not ready to automate it yet.

### Optimizing the Judge Prompt

> *Diagram idea: best practices for optimizing a judge prompt*

A judge prompt needs more structure than a typical agent prompt to reduce ambiguity. **A reliable judge prompt usually includes:**

  - **A clear role.** Position the model as a reviewer or auditor, not as the original system prompt’s assistant.
  - **A single evaluation question.** One attribute. One yes/no decision. This should be built from your trace category.
  - **A concrete standard.** Describe the standard as observable behaviors. Avoid abstract words unless you immediately operationalize them.
  - **Ambiguous examples** that teach the boundary. Include a few pass examples and a few fail examples, ideally drawn from the same domain and similar tasks. The most valuable examples are the borderline ones where reasonable people might disagree. That’s where the judge is most likely to drift.
  - **Self-Reflection.** Instructions should include "Think step-by-step" and "Check your reasoning" to force logical analysis before the final score. This significantly improves consistency.
  - **A strict output format.** Require the judge to return its evaluation as JSON or YAML, ensuring the data is parseable for dashboards and analysis. Include a predictable label and a short justification you can use for debugging.

### Running LLM Judges Across a Dataset

The mechanics of running LLM judges mirror running code evals: you execute each judge against each row in your reference dataset and record pass/fail plus the reasoning string. The differences are cost, interpretation, and what "low pass rate" means.

**LLM inference is not free.** A 50-ticket dataset with three judges is 150 model calls per experiment run. At current inference costs this is manageable — but it means judges should run after code evals pass, not in parallel with every trivial prompt change. Run code evals first, every time. Run LLM judges when the code evals are green and you're evaluating a substantive change.

> *Diagram idea: diagram — aggregate result metrics for LLM judges across a dataset*

**Pass rate as a signal, not a verdict.** If the empathy judge pass rate drops from 88% to 62% after a prompt change, something in the new prompt is suppressing the acknowledgment behavior. Before concluding the agent got worse, read ten failing cases and their reasoning strings.
Example: A pattern like "response opens with account status rather than acknowledgment" across 80% of failures points to a specific prompt clause redirecting agent behavior — not a general quality decline.

**Failure distribution over raw pass rate.** If 90% of actionability judge failures come from tickets classified as Feature Request, the agent is missing next steps specifically for feature escalations, not for billing or technical issues. That's a precise diagnostic. It maps directly to a targeted prompt fix rather than a broad revision.

**Cross-judge correlation reveals root causes.** When the empathy judge and the actionability judge both fail on the same ticket, it usually signals a single failure mode — the agent prioritized efficiency and produced a short, terse response that satisfied neither criterion. Fix the root cause; don't address each judge's failure independently.

**Always compare to your production baseline.** A new version scoring 72% on the factual grounding judge sounds concerning in isolation. If the production baseline was 68%, that's a measurable improvement. Set your baseline on the current production version before you start iterating, and compare every new result against it.

**When a pass rate is unexpectedly low, read the reasoning strings before diagnosing the agent.** A judge that returns "Fail - response is not a support interaction" on 40% of traces may have a scope problem in its prompt, not a reflection of agent quality. Verify the judge logic before drawing conclusions about the model.

### Failure Modes to Watch For

> *Diagram idea: diagram — key failure modes for LLM judges based on below*

Even calibrated judges break in predictable ways. Knowing the failure modes in advance means you can design around them.

**They become easy to game.** If the agent's outputs are also being optimized against the judge, they can drift toward patterns the judge rewards rather than patterns users actually prefer.
**Example:** after several iterations toward a passing empathy judge, the agent starts opening every response — including routine password resets — with "I completely understand how frustrating this must be." Judge score improves. CSAT doesn't. Users start editing out the boilerplate. The signal: judge metrics improve while user edits or explicit complaints increase.

**They drift when the product changes.** Judges are calibrated on examples from one distribution. When the product expands to new user segments, new domains, or new ticket types, yesterday's examples stop representing today's distribution.
**Example:** the empathy judge was calibrated on 50 billing tickets from B2C users. The agent expands to handle technical integration questions from developer accounts. Developers don't want empathetic preambles — they want precise technical answers. The judge flags accurate, appropriately concise developer responses as failing, because its examples were all consumer billing interactions. Fix: refresh the example set whenever your user distribution changes materially.

**They break down on genuinely novel outputs.** When there's no stable definition of "good" for a new output type, the judge defaults to rewarding fluency and polish.
**Example:** the team launches a proactive outreach feature — the agent flags accounts likely to churn and drafts personalized messages. There's no existing example set for this output type. The judge rewards responses that "sound supportive" because that's what its training examples rewarded, even though the success criterion for outreach is specificity and relevance, not warmth.

**They fail when quality requires deep domain expertise.** Judges catch surface-level issues but miss errors that require specialized knowledge.

**They reward style over substance.** Verbose responses that mention timelines, escalation paths, and resolution steps look "actionable" to a model even when they avoid the actual question.
Example: the actionability judge learns to reward responses that include the phrase "will be resolved within 2–3 business days," regardless of whether the response actually addresses the customer's specific issue. Judge score: high. Actual actionability: the customer still doesn't know what to do.

The best judges are paired with disciplined usage: they measure a specific quality boundary you care about, they get their examples refreshed as the product evolves, and they trigger concrete investigation when they fail.

## Recap and Further Learning

### Key takeaways and definitions

  - **When to use an LLM judge:** When you've identified a trace category through trace analysis that requires subjective assessment — tone, intent, relevance, completeness — and you can write down what pass and fail look like in plain language, with examples. If you can check it in ten lines of Python, use code instead.
  - **Binary over Likert:** LLM judges should return yes/no verdicts with reasoning strings, not scores on a scale. Binary labels are easier to validate against human assessments, easier to set release thresholds on, and harder to game through prompt optimization.
  - **One criterion per judge:** Narrow scope produces more reliable, more debuggable judges. A judge that evaluates tone and actionability and factual accuracy in a single call will drift on all three. Separate judges enable precise root cause analysis — you can see exactly which quality dimension changed between versions.
  - **Reference-free vs reference-based:** Choose based on what evidence you have. Reference-free judges evaluate the output on its own merits and can be built from any representative traces. Reference-based judges compare output against ground truth and require either labeled data or access to retrieved context.
  - **Failure modes are predictable:** Gaming, drift, and style-over-substance failures are common. The mitigations are to refresh examples when the user distribution changes, track user edits alongside judge scores, and always read reasoning strings rather than acting on pass rate alone.

In the next module, we will learn how to build and maintain the reference datasets that make your eval suite reliable as your product evolves and your user distribution shifts.
