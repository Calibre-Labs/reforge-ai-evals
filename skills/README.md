# Claude Code skills for AI evals

The skills in the `ai-evals` plugin. Together they cover the eval loop for any AI product or agent: writing the eval rubric, designing an eval dataset, turning trace notes into failure codes, writing code-based evaluators and LLM-as-a-judge prompts, checking judges against human labels, and turning production failures into regression tests.

Install the plugin in Claude Code:

```bash
claude plugin marketplace add Calibre-Labs/reforge-ai-evals
claude plugin install ai-evals@calibre-labs
```

Or copy them as plain slash commands with `bash install-skills.sh` from the repo root. See the [main README](../README.md#quick-start) for other options.

| Skill | Use it to |
|-------|-----------|
| [`eval-guide`](eval-guide/SKILL.md) | Find the right skill when you're not sure where to start |
| [`eval-rubric`](eval-rubric/SKILL.md) | Write the eval rubric for an agent: v1 from the PRD before traces, v2 from trace codes, or an audit of an existing rubric, plus release thresholds |
| [`uig`](uig/SKILL.md) | Build a User Input Grid (UIG) for your product, audit an eval dataset's coverage, and propose new queries to fill the gaps |
| [`trace-codes`](trace-codes/SKILL.md) | Cluster free-form trace notes into named yes/no failure codes with definitions, examples and counts, and write a label sheet for review |
| [`eval-code`](eval-code/SKILL.md) | Write deterministic evaluators for structure, counts, formats and citations |
| [`eval-llm-judge`](eval-llm-judge/SKILL.md) | Write an LLM-as-a-judge prompt: one criterion, binary PASS/FAIL, few-shot examples, JSON output, TPR/TNR validation plan |
| [`llm-align`](llm-align/SKILL.md) | Compute TPR/TNR between an LLM judge and human labels, investigate each disagreement, and suggest prompt fixes and few-shot examples |
| [`ticket-to-eval`](ticket-to-eval/SKILL.md) | Convert a support ticket or production trace into PII-stripped regression and coverage rows |

Each skill folder has a `SKILL.md` and an `agents/openai.yaml` for Codex. `eval-rubric` also ships reference files (PRD sections, an HTML rubric template and worked examples).

For example output, see [`docs/uig-market-map.md`](../docs/uig-market-map.md) (from `uig`) and the rubrics in [`rubric-templates/`](../rubric-templates/) (the kind `eval-rubric` writes).
