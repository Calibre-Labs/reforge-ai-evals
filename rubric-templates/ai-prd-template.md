# AI PRD template

A PRD for an agent specifies behavior, not screens. This template has thirteen sections. Two are new relative to a typical PRD: **Autonomy**, because an agent's permissions are a product decision, not an engineering detail; and **Release thresholds**, split out from the eval rubric because a threshold gates a launch and a rubric line does not. Everything else is close to what you already write, tightened for an agent instead of a UI.

Delete a section only if you have a specific reason. An empty "Non-goals" section is a decision nobody made on purpose.

---

## 1. Product

One paragraph. What it is, who it's for, what it does when it works. Someone who has never seen a demo should be able to describe the product back to you after reading this paragraph.

## 2. User and channel

Who is on the other end, and where they meet the agent: SMS, a workspace chat, an app, an API. The channel sets the pace and the tone. A CFO in a workspace chat tolerates a ten-minute wait and a long confirmation message. A consumer over SMS tolerates neither. Name what success is measured in, in one sentence: seconds and the absence of friction, or auditability, or something else entirely. This sentence should predict half your rubric before you've written it.

## 3. Jobs to be done

The requests a real user actually makes, in their words, not your feature list. Four or five is usually enough. If you can't state the job in one sentence, the agent can't be evaluated against it.

## 4. Tool surface

Every action the agent can take, as a table: tool, what it does, and whether it's reversible. Reversibility is the column most PRDs skip and the one Governance and Autonomy both depend on. A tool that reads is free to call. A tool that charges a card or writes to a shared file is not, and the rest of the PRD should treat it differently.

| Tool | What it does | Reversible? |
|---|---|---|
| `example_tool(args)` | One line. | Yes / No |

## 5. Autonomy

For each action or class of action, say whether the agent acts, confirms first, or escalates to a human. This section exists because "how much can it do without asking" is a product decision, and if you don't make it explicitly, the agent makes it for you, inconsistently, on every trace.

| Action | Autonomy | Why |
|---|---|---|
| Reversible, in scope | Acts | No cost to being wrong. |
| Irreversible, in scope, unambiguous | Acts, then discloses | The user would say yes; tell them what happened. |
| Irreversible, ambiguous | Confirms first | Guessing is expensive here. |
| Outside the tool surface or the policy | Escalates | Not the agent's call. |

This table is where Trajectory and Governance in the rubric come from. Write it before you write those.

## 6. Happy path

One concrete scenario, step by step, with real-sounding inputs. Not "the user requests an order," but the actual text message. A happy path with placeholder inputs hides the ambiguity that placeholder inputs don't have.

## 7. Non-goals

What the agent will not do, stated as plainly as what it will. "Delivery" and "purchases over $100" are non-goals because someone could reasonably assume otherwise. A non-goals section with nothing surprising in it hasn't done its job.

## 8. Known risks

The ways this specific agent, with this specific tool surface, is likely to fail. Not a generic AI-risk checklist: risks that follow from the tools you gave it and the ambiguity in the requests you expect. If a risk here doesn't map to a line in the eval rubric, one of the two is incomplete.

## 9. Definition of success

Three or four sentences a person could check against a transcript without reading your mind. This is the plain-language version of Outcome; the rubric is its enforceable version.

## 10. Eval rubric

The pass/fail criteria that define whether the agent is working, in four groups:

- **Outcome.** What did it produce, and is it right?
- **Trajectory.** How did it get there?
- **Governance.** What must it never do, and always do?
- **Experience.** How did it feel to the user in this channel?

Write v1 from this PRD, before a single trace, in under an hour: one or two Outcome lines from Definition of success, most of Governance from the tool surface's reversibility column and the Autonomy table, one or two Trajectory lines you already know matter, one Experience line on tone. Don't try to finish Trajectory or Experience; you can't predict the odd paths yet. Write v2 after you've read traces: it adds criteria for what you didn't predict, sharpens criteria that were too blunt, and almost never removes a line.

Keep the rubric itself in its own artifact, linked from here, so it can carry its own version history independent of the PRD.

## 11. Release thresholds

The numbers, checked across many sessions, not one: max cost per task, latency, and the failure-rate ceiling you'll tolerate at GA. These gate the release. The rubric's four groups above don't: a single trace failing an Outcome line tells you about that trace, not whether to ship.

| Metric | Target | Why |
|---|---|---|
| Cost per task | | |
| Latency | | |
| Failure-rate ceiling at GA | | |

Thresholds start as targets, before you have data, and get recalibrated once you do. That's the only thing about them that changes between v1 and v2; the metrics you're tracking usually don't.

## 12. Rollout

How exposure increases: shadow mode, a human-in-the-loop beta, a limited GA, then GA. Say what has to be true, against the thresholds above, to move from one stage to the next. A rollout plan with no exit criteria is a launch date with extra steps.

## 13. Open questions

What's undecided, who owns deciding it, and by when. An open question with no owner is a risk wearing a disguise.
