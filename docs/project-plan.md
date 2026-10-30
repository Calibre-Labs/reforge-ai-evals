# AI Evals plugin: plan

A plugin of skills for building, auditing and improving eval loops for AI products. Each skill is a folder with a `SKILL.md` that works on plain files, with no dependency on an eval platform.

## Skills

| Skill | Purpose | State |
|---|---|---|
| `eval-guide` | Entry point. Routes to the right skill and names the steps that stay human. | Available |
| `eval-rubric` | Write the eval rubric into a PRD: v1 before traces, v2 from trace codes, or audit one. | Available |
| `uig` | Build a User Input Grid, audit eval datasets, recommend new inputs. | Available |
| `trace-codes` | Cluster trace notes into yes/no codes, prioritize, propose rubric changes. | Available |
| `eval-code` | Write deterministic code-based evaluators. | Available |
| `eval-llm-judge` | Write LLM judge prompts for one criterion each. | Available |
| `llm-align` | Measure a judge against human labels (TPR/TNR), investigate disagreements, fix the prompt. | Available |
| `ticket-to-eval` | Convert support tickets or traces into regression and generalized dataset rows. | Available |
| `trace-review-app` | Design and build a one-file trace review app for one product: queue, notes, pass or fail labels, trace-code tags and exports for the other skills. | Draft (Week 5) |
| `eval-run` | Run an agent and its scorers over a dataset, save traces and a results report, compare two runs. | To do (Week 3) |
| `eval-trace` | Evaluate tool calls and multi-step traces: tool choice, arguments, order, task completion. | To do (Week 5) |
| `eval-monitor` | Sample production sessions on a schedule, score them, report drift, propose dataset rows. | To do (Week 5) |

Also to do: a local trace viewer the skills can generate. One HTML file served by a small Python server with no dependencies, for reading traces, writing notes and labeling. Notes save to disk so `trace-codes` and `llm-align` can read them.

## How the fall 2026 course uses the skills on Mapper

Mapper has three versions for the course: v1 (what Weeks 1 and 2 showed), v1.1 (three fixes shipped before Week 3: cite only retrieved links, decline investment advice, answer for the year asked; in production from Nov 2) and v2 (the metric-scope fix for Week 4; in production from Nov 11). Sharing is unchanged in every version: no confirm card. mapper3's `docs/demo-plan.md` is the record of which version each week shows and which known issues stay unfixed on purpose; its `PLAN.md` tracks the app work.

| Week | Version | What the cohort sees | Skills shown |
|---|---|---|---|
| 2, Oct 28 | v1 | Ten recorded traces, rubric v1, notes, trace codes | eval-rubric, uig, trace-codes |
| 3, Nov 4 | v1, then v1.1 | Three fixes shipped with no eval. Code checks written live: G2 (links that don't open) and half-empty columns (X2). Judges: metric scope live as the deep dive; O2, T1, G3 and T3 from prep. All scored in Braintrust on `w3-v1` and `w3-v1.1` (30 rows each) | eval-code, eval-llm-judge |
| 4, Nov 11 | v1.1, then v2 | Align the metric-scope judge against our labels and the cohort's, then compare v1.1 and v2: metric scope goes up. Switch the app live; production moves to v2 | llm-align, eval-run, uig, ticket-to-eval |
| 5, Nov 18 | v2 | Braintrust online scoring on the cohort's v2 sessions, and agent success rate in Amplitude Agent Analytics | eval-trace, eval-monitor, trace-review-app |

The course scorers are plain TypeScript files in mapper3's `scorers/course/`, written by the plugin's skills; the same file runs locally and in Braintrust. mapper3's batch runner records `mapper-trace/1` folders, `npm run score` logs each run as a Braintrust experiment and writes `scores.json`, and `npm run results` turns the scores into a self-contained results page, the fallback for both Week 3 demos. `compare-runs` stays code-only. eval-monitor reads mapper3's admin trace export, with usernames replaced by pseudonyms.

## Packaging

- `.claude-plugin/plugin.json` and `marketplace.json`: Claude Code plugin. Validated with `claude plugin validate`.
- `.codex-plugin/plugin.json` and `skills/*/agents/openai.yaml`: Codex. Not tested yet.
- `scripts/build-plugin.sh`: builds `dist/ai-evals.plugin` for the Claude desktop app.
- `scripts/install-skills.sh`: fallback that installs the skills as slash commands.

The plugin is named `ai-evals`, in the `calibre-labs` marketplace. Open before any public listing: a license file.

## Docs and examples

| Path | What it is |
|---|---|
| `templates/` | AI PRD template, and Corner, Ledger, Mapper and Support Triage as worked examples |
| `docs/uig-market-map.md` | Worked UIG for the Market Map agent |

To add: Mapper's v2 rubric, and worked UIG examples for two or three other product types.

To do before the cohort uses them: review the Mapper pages and the Week 2 trace set, and change what we don't like.

## Design principles

1. Each skill works with zero setup beyond installing the plugin.
2. No assumption about an eval platform. Skills read and write files, and can read from a platform when the data lives there.
3. No product-specific tuning. Examples are labeled as examples.
4. Inputs are "inputs", not "queries": instructions, records, actions and text all count.
5. Methodology lives in the skill folder itself, in `SKILL.md` or its `references/`.
6. Annotating traces and labeling for calibration stay with a person. No skill does either on the user's behalf.
