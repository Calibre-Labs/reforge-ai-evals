**

# AI Evals Week 4 FAQ: aligning judges

Answers to every question from the Week 4 chat and Q\&A on Nov 11, grouped by topic, including the ones we didn't get to live.

## Our favorite question

### Can you walk through the whole process, from the AI PRD to an aligned judge, so I can put the pieces in the right order?

Think of it in phases, with the dataset growing at each one.

1.  Write the AI PRD, including the eval rubric: what the agent should do and what good looks like. Before you have traces, the rubric lines are your draft trace codes.
2.  Build a first version and use it yourself. That's your first human evaluation. Update the PRD and rubric as you find things you didn't expect. If an engineer builds the agent, the PRD is your contract with them, so keep it current. A handful of traces is enough here.
3.  Get more traces from alpha users, teammates or synthetic inputs (30 to 50). Read them, write trace codes, and fix what you can with the prompt or the harness. Sharpen the rubric as you go.
4.  When the obvious fixes run out and something still works only some of the time, write a code check or an LLM judge for it. Label at least 100 sessions for that one judge, split into train, dev and test sets, and align the judge until it agrees with you about 90% of the time on passes and on fails.
5.  Run it in production. Online evals and user feedback show you what your offline dataset missed (Week 5).

You'll loop back to earlier steps the whole time. Sycophancy is a good example: few teams expected it, users complained, and it went into the eval rubric after launch.

## Trusting a judge

### Even if the judge is right, isn't 37% too low to ship?

That's a separate question. If this score matters, 37% is too low to release to all your customers, though it might be fine for an alpha. But first you need to know whether 37% is real, which is what alignment tells you.

### How do TPR and TNR relate to precision and recall?

They come from the same confusion matrix, with "pass" as the positive class. TPR is recall: of the sessions you passed, how many the judge also passed (7 of 11, or 64%, in our example). TNR is the same idea for fails (16 of 19, or 84%). Precision asks the reverse question: of the sessions the judge passed, how many did you pass (7 of 10, or 70%). We report TPR and TNR because together they show whether the judge is too strict or too lenient, and you can move each one separately.

### Shouldn't the targets depend on the application? In a clinical setting you'd accept false positives to avoid missing anything, and in a nuclear setting you'd want none.

Yes. The cost of each kind of mistake should set your targets. Decide the acceptable trade-off, then write the judge to apply that policy. For our "don't give investment advice" check, we'd rather stop every piece of advice getting through and accept a few extra refusals.

### Who generated the hypotheses for why the judge disagreed with us, a human or AI?

The coding agent, by comparing the human notes with the judge's critiques. That's why detailed notes matter so much when you label: they're what the agent reasons from. As always, trust but verify.

### Have newer models ever made a judge worse? Any best practices when switching the judge's model?

Frontier models are close to each other, with differences at the margins for some use cases. Treat a model swap like any other change to the judge: re-run it on your labeled dev and test sets and check TPR and TNR before you trust the new scores. Use the cheapest model that reaches about 90% on both, since judges run on every session you score. We moved our metric-scope judge from Gemini Flash Lite to Gemini Flash only after prompt changes stopped improving its agreement.

### When data is so critical that you'd double-check it anyway, why not have the agent give sources and fill in the numbers yourself?

For one high-stakes decision, that's sensible, and Mapper shows its sources so people can check. But a product serves many people who won't all check. The judge measures how often the agent gets it right across thousands of sessions, and whether a change made it better. Checking every output by hand can't tell you either.

## Datasets

### By "train", do we mean training the judge's prompt?

Yes. The train set is where the examples in the judge prompt come from (in-context learning). No model gets trained. You can't measure agreement on those sessions, because the judge has already seen your answers.

### If we improve the judge several times, do we need a fresh test set each time?

No. The test set stays blind for each new version of the judge, as long as none of its sessions go into the prompt as examples and you don't change the judge to fix specific test failures. Once you do that, it's no longer blind, and you need fresh cases. For judges you depend on, keep labeling a sample of production sessions so you keep checking agreement over time.

### A hundred sessions feels small if the judge will run on millions of sessions.

A hundred is the minimum for one judge testing one aspect of the product. Going from 100 to 300 diverse rows gives diminishing returns for that judge. A real product needs a dozen or more judges, so the whole dataset quickly reaches a thousand traces or more, and broad general-purpose products need more than that.

### Should each judge have its own dataset, or should all judges run on one bigger, diverse dataset?

Both. Keep a shared, diverse core dataset that every judge runs on, and add targeted cases for each judge. The [uig skill](https://github.com/Calibre-Labs/reforge-ai-evals/tree/main/skills/uig) finds gaps in coverage, and the [ticket-to-eval skill](https://github.com/Calibre-Labs/reforge-ai-evals/tree/main/skills/ticket-to-eval) turns support tickets into new rows with personal details removed.

### How do we decide when an agent needs multiple judges?

Almost every agent will have several, each narrow and focused on one failure mode from your trace codes. Not every trace code needs a judge, though. Run the specification, system and generalization checks first, and use a code check wherever a rule works. A judge is itself an AI product that takes work to calibrate.

## Methods and tools

### Will you cover using Jev as the model for a pass or fail LLM judge?

Jev is the new model from Typesafe. We weren't planning to cover it, but we'll see if we can add it next week. The same workflow applies with any judge model: labeled traces, a clear rubric, and agreement measured on dev and test sets. The implementation differs because Jev doesn't give you a rationale for each call, so you have less to reason from when it disagrees with you.

### What about using GEPA to optimize judges?

We're teaching the same principles as [GEPA](https://arxiv.org/abs/2507.19457). GEPA adds an algorithm that explores many prompt revisions automatically, using reflection on failures. Either way, what matters most is a well-labeled dataset and a clear rubric.

### What's the first signal that our evals need revisiting? A drop in task completion rate?

A falling eval score is worth digging into, but the more common problem is drift: users do things your offline dataset never covered, so no eval catches them. That's why you keep reading production sessions. One example: with newly launched agents, as many as 30% of sessions can be people asking what the agent can do, and most teams never test for it.

### We're building a platform for about 100 product teams to see whether their agents are release-ready or drifting. Any best practices for a maturity scorecard like this?

Focus first on well-labeled traces. Make it as easy as possible for the teams building each agent to label their own traces, because they know what great looks like and a central ML team doesn't. Once teams label traces and have a clear rubric, much of the rest can be automated. The platform team's job is the scaffolding around that.

### Where's the line between product management and engineering on evals? Any references for a prototype?

The PM owns what good looks like: the rubric, the labels and the release thresholds. Engineering owns how the checks run and which fixes to try. For a prototype, partner with one pilot team and get them through trace analysis end to end before building infrastructure. Platforms built first often go unused. The skills in the [course repo](https://github.com/Calibre-Labs/reforge-ai-evals) cover each step once that team is labeling traces.

