# Claude Code skills for AI evals

Five Claude Code skills that automate the core steps of building AI evals: designing an eval dataset, writing code-based evaluators, writing LLM-as-a-judge prompts, validating judges against human labels, and turning production failures into regression tests. They are not tied to the Market Map example and work for any AI product or agent.

Install them all from the repo root:

```bash
bash install-skills.sh
```

This copies each skill to `~/.claude/commands/` so it is available as a slash command in any Claude Code session.

| Skill | Command | Use it to |
|-------|---------|-----------|
| [`uig-skill.md`](uig-skill.md) | `/uig` | Build a User Input Grid (UIG) for your product, audit an eval dataset's coverage, and propose new queries to fill the gaps |
| [`eval-code-skill.md`](eval-code-skill.md) | `/eval-code` | Write deterministic evaluators for structure, counts, formats and citations |
| [`eval-llm-judge-skill.md`](eval-llm-judge-skill.md) | `/eval-llm-judge` | Write an LLM-as-a-judge prompt: one criterion, binary PASS/FAIL, 3 few-shot examples, JSON output, TPR/TNR validation plan |
| [`llm-align-skill.md`](llm-align-skill.md) | `/llm-align` | Compute TPR/TNR between an LLM judge and human labels, investigate each disagreement, and suggest prompt fixes and few-shot examples |
| [`ticket-to-eval-skill.md`](ticket-to-eval-skill.md) | `/ticket-to-eval` | Convert a support ticket or production trace into PII-stripped regression and coverage rows in Braintrust or a local CSV |

See the [main README](../README.md) for the full toolkit, and [`docs/uig-market-map.md`](../docs/uig-market-map.md) for an example of `/uig` output.
