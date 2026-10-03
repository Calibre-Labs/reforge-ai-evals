# Calibre evals: plan

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
| `eval-run` | Run an agent and its scorers over a dataset, save traces and a results report, compare two runs. | To do (Week 2) |
| `eval-trace` | Evaluate tool calls and multi-step traces: tool choice, arguments, order, task completion. | To do (Week 4) |
| `eval-monitor` | Sample production sessions on a schedule, score them, report drift, propose dataset rows. | To do (Week 4) |

Also to do: a local trace viewer the skills can generate. One HTML file served by a small Python server with no dependencies, for reading traces, writing notes and labeling. Notes save to disk so `trace-codes` and `llm-align` can read them.

## Packaging

- `.claude-plugin/plugin.json` and `marketplace.json`: Claude Code plugin. Validated with `claude plugin validate`.
- `.codex-plugin/plugin.json` and `skills/*/agents/openai.yaml`: Codex. Not tested yet.
- `scripts/build-plugin.sh`: builds `dist/calibre-evals.plugin` for the Claude desktop app.
- `install-skills.sh`: fallback that installs the skills as slash commands.

Open before any public listing: the plugin name (`calibre-evals` is the working name and is permanent once listed), and a license file.

## Docs and examples

| Path | What it is |
|---|---|
| `rubric-templates/` | AI PRD template, and Corner, Ledger, Mapper and Support Triage as worked examples |
| `docs/uig-market-map.md` | Worked UIG for the Market Map agent |
| `prompts/`, `datasets/`, `evaluators/`, `mcp/` | The spring 2026 single-prompt Market Map example |

To add: Mapper's Week 1 trace set and its v2 rubric, and worked UIG examples for two or three other product types.

## Design principles

1. Each skill works with zero setup beyond installing the plugin.
2. No assumption about an eval platform. Skills read and write files, and can read from a platform when the data lives there.
3. No product-specific tuning. Examples are labeled as examples.
4. Inputs are "inputs", not "queries": instructions, records, actions and text all count.
5. Methodology lives in the skill folder itself, in `SKILL.md` or its `references/`.
6. Annotating traces and labeling for calibration stay with a person. No skill does either on the user's behalf.
