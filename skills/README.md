# Agent skills for AI evals

Eight skills that guide an AI coding agent through the eval loop for any AI product. See the [main README](../README.md) for how they fit together.

| Skill | What it does |
|-------|--------------|
| [eval-guide](eval-guide/SKILL.md) | Entry point. Routes to the skill that matches where you are |
| [eval-rubric](eval-rubric/SKILL.md) | Writes the eval rubric and release thresholds: v1 from the PRD, v2 from trace codes, or an audit |
| [uig](uig/SKILL.md) | Builds a User Input Grid, audits dataset coverage and proposes inputs to fill the gaps |
| [trace-review-app](trace-review-app/SKILL.md) | Builds a one-file trace review app for your product, with notes, pass/fail labels, trace-code tags and exports (draft) |
| [trace-codes](trace-codes/SKILL.md) | Clusters trace notes into named yes/no failure codes with counts and a label sheet |
| [eval-code](eval-code/SKILL.md) | Writes deterministic, code-based evaluators |
| [eval-llm-judge](eval-llm-judge/SKILL.md) | Writes LLM-as-a-judge prompts with one criterion each |
| [llm-align](llm-align/SKILL.md) | Measures judges against human labels (TPR/TNR) and suggests prompt fixes |
| [ticket-to-eval](ticket-to-eval/SKILL.md) | Turns support tickets and bad traces into PII-stripped regression rows |

## Install

```bash
npx skills add https://github.com/Calibre-Labs/reforge-ai-evals            # any coding agent
claude plugin marketplace add Calibre-Labs/reforge-ai-evals               # Claude Code plugin
claude plugin install ai-evals@calibre-labs
```

Other options:
- **Claude desktop app:** `bash scripts/build-plugin.sh`, then install `dist/ai-evals.plugin`.
- **Codex:** the repo includes `.codex-plugin/` and a per-skill `agents/openai.yaml` (not yet tested).
- **Claude Code slash commands without the plugin:** `bash scripts/install-skills.sh`, or run Claude Code from the repo root, where `.claude/commands/` links to these skills.

Each skill is a folder with a `SKILL.md`. `eval-rubric` also ships reference files, so copy the whole folder when installing by hand.
