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

The course demos follow two Mapper failures from Week 2 to Week 5. The same plan is in mapper3's `PLAN.md`, which also tracks the app work each step needs.

| Week | Grounding: cites sources it never retrieved (rubric G2) | Governance: publishes a link nobody asked for (rubric G3) | Skills shown |
|---|---|---|---|
| 2, Oct 28 | The cohort finds made-up links in nine recorded traces | | eval-rubric, uig, trace-codes |
| 3, Nov 4 | eval-code writes the check; eval-run runs it over 30 recorded sessions (grounding in `log` mode) | eval-code writes the check; a must-never at 100% | eval-code, eval-llm-judge, eval-run |
| 4, Nov 11 | llm-align aligns the judge; the harness fix (`SOURCE_GROUNDING=enforce`) is re-run and compared | | llm-align, uig, ticket-to-eval, eval-run |
| 5, Nov 18 | eval-monitor runs the Week 3 checks and Week 4 judge nightly on the cohort's production sessions | The confirm card live in production | eval-trace, eval-monitor, trace-review-app |

eval-run reads folders of `mapper-trace/1` files written by mapper3's batch runner. mapper3's `compare-runs` report stays code-only; eval-run adds the judges and writes the results page. eval-monitor reads mapper3's admin trace export, with usernames replaced by pseudonyms.

## Packaging

- `.claude-plugin/plugin.json` and `marketplace.json`: Claude Code plugin. Validated with `claude plugin validate`.
- `.codex-plugin/plugin.json` and `skills/*/agents/openai.yaml`: Codex. Not tested yet.
- `scripts/build-plugin.sh`: builds `dist/ai-evals.plugin` for the Claude desktop app.
- `scripts/install-skills.sh`: fallback that installs the skills as slash commands.

The plugin is named `ai-evals`, in the `calibre-labs` marketplace. Open before any public listing: a license file.

## Docs and examples

| Path | What it is |
|---|---|
| `rubric-templates/` | AI PRD template, and Corner, Ledger, Mapper and Support Triage as worked examples |
| `docs/uig-market-map.md` | Worked UIG for the Market Map agent |
| `prompts/`, `datasets/`, `evaluators/`, `mcp/` | The spring 2026 single-prompt Market Map example |

To add: Mapper's v2 rubric, and worked UIG examples for two or three other product types.

To do before the cohort uses them: review the Mapper pages and the Week 2 trace set, and change what we don't like.

## Design principles

1. Each skill works with zero setup beyond installing the plugin.
2. No assumption about an eval platform. Skills read and write files, and can read from a platform when the data lives there.
3. No product-specific tuning. Examples are labeled as examples.
4. Inputs are "inputs", not "queries": instructions, records, actions and text all count.
5. Methodology lives in the skill folder itself, in `SKILL.md` or its `references/`.
6. Annotating traces and labeling for calibration stay with a person. No skill does either on the user's behalf.
