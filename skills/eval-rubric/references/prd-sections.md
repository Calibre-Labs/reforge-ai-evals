# The PRD sections a rubric derives from

The full template is `rubric-templates/ai-prd-template.md` in the repo. These are the parts the
rubric depends on. If a PRD is missing one, draft it and confirm it before writing rubric lines.

## Definition of success

Three or four sentences a person could check against a transcript without reading your mind.
This is the plain-language version of the outcome lines. The rubric is its enforceable version.

## Tool surface

Every action the agent can take, as a table: the tool, what it does, and whether it is
reversible. Reversibility is the column most PRDs skip, and governance depends on it. A tool that
reads is free to call. A tool that charges a card, sends a message or writes to a shared file is
not.

| Tool | What it does | Reversible? |
|---|---|---|
| `example_tool(args)` | One line. | Yes / No |

Each irreversible tool should produce at least one governance line.

## Autonomy

For each action or class of action, whether the agent acts, confirms first, or escalates to a
person.

| Action | Autonomy | Why |
|---|---|---|
| Reversible, in scope | Acts | No cost to being wrong. |
| Irreversible, in scope, unambiguous | Acts, then discloses | The user would say yes. Tell them what happened. |
| Irreversible, ambiguous | Confirms first | Guessing is expensive here. |
| Outside the tool surface or the policy | Escalates | Not the agent's call. |

This table is where trajectory lines come from.

## Non-goals and policy

What the agent will not do, stated as plainly as what it will. Each non-goal that a user could
reasonably ask for becomes a governance line ("Declines requests for ..."). Spend caps, data
boundaries and approval rules come from policy documents. Read them when they exist.

## User and channel

Who is on the other end and where they meet the agent. The channel sets pace and tone. Name what
success is measured in, in one sentence. That sentence predicts the experience line and the
balance between asking and guessing.

## Release thresholds

The numbers checked across many sessions: maximum cost per task, latency, and the failure-rate
ceiling the team will tolerate at launch. These gate a release. A rubric line does not: one trace
failing an outcome line tells you about that trace, not whether to ship.

| Metric | Target | Why |
|---|---|---|
| Cost per task | | |
| Latency | | |
| Failure-rate ceiling at launch | | |

Thresholds start as targets and get recalibrated once there is data.
