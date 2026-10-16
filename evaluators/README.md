# Code-based evaluators and LLM-as-a-judge examples

Eleven evaluators for the Market Map example agent: 4 deterministic code-based checks and 7 LLM-as-a-judge prompts. The criteria are specific to Market Map, but the patterns carry over to any AI product: one criterion per judge, binary PASS/FAIL definitions, 3 few-shot examples (PASS, FAIL, borderline) and a JSON critique before the score.

- [`evaluators.py`](evaluators.py) has every evaluator as a plain Python function, for local runs or as Braintrust scorer functions.
- Each other file holds a single evaluator written as a Braintrust custom scorer (`handler` function), ready to paste into Braintrust.

## Run locally

The LLM judges in `evaluators.py` need an [Anthropic API key](https://console.anthropic.com) and `pip install anthropic`.

```python
from evaluators import company_count, ranking_quality_judge

print(company_count("your model output here", "team chat"))          # 0.0, 0.5, or 1.0
print(ranking_quality_judge("your model output here", "team chat"))  # {"score": 1.0, "metadata": {...}}
```

## Code-based evaluators (no LLM call)

| Evaluator | File | Checks |
|-----------|------|--------|
| `company_count` | [`code-company-count.py`](code-company-count.py) | Exactly 3 ranked companies appear |
| `has_sources` | [`code-has-sources.py`](code-has-sources.py) | 3–4 source citations are present |
| `has_metrics` | [`code-has-metrics.py`](code-has-metrics.py) | Each company has at least 2 supporting data points |
| `has_category` | [`code-has-category.py`](code-has-category.py) | A market category is named before the ranking |

## LLM-as-a-judge evaluators

| Evaluator | File | Checks |
|-----------|------|--------|
| `ranking_quality_judge` | [`llm-judge-ranking-quality.py`](llm-judge-ranking-quality.py) | The right 3 companies, in the right order |
| `edge_case_handling_judge` | [`llm-judge-edge-case-handling.py`](llm-judge-edge-case-handling.py) | Vague or out-of-scope queries are handled gracefully, not hallucinated |
| `reference_judge` | [`llm-judge-reference.py`](llm-judge-reference.py) | Output matches a gold-standard reference answer |
| `company_match_judge` | [`llm-judge-company-match.py`](llm-judge-company-match.py) | Top 3 companies and their order match the reference |
| `metric_coverage_judge` | [`llm-judge-metric-coverage.py`](llm-judge-metric-coverage.py) | At least 2 of 3 companies have 2+ quantitative metrics |
| `metric_scope_judge` | [`llm-judge-metric-scope.py`](llm-judge-metric-scope.py) | Metrics are scoped to the relevant product, not the parent company |

To write evaluators like these for your own product, use the [`eval-code`](../skills/eval-code/SKILL.md) or [`eval-llm-judge`](../skills/eval-llm-judge/SKILL.md) skill. To check whether a judge agrees with human labels, use [`llm-align`](../skills/llm-align/SKILL.md).
