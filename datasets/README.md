# Example eval datasets

Eval datasets for the Market Map example agent, showing how to grow an eval set from 10 rows to a tagged, coverage-driven dataset with targeted edge-case sets and a regression set built from support tickets. All files are Braintrust-format CSVs and can be imported directly.

Every row is tagged in the `metadata` column with its [User Input Grid](../README.md#the-user-input-grid-uig) dimensions (`query_type`, `domain`, `style`, `temporal`, `edge_case`), so results can be sliced by dimension to find where the agent fails.

| File | Rows | What it tests |
|------|------|---------------|
| [`week1-dataset.csv`](week1-dataset.csv) | 10 | Starting dataset, with gold-standard `expected` answers for reference judges |
| [`week2-dataset-30.csv`](week2-dataset-30.csv) | 30 | Maximum diversity across all 4 UIG dimensions. Start here. |
| [`week3-dataset-60.csv`](week3-dataset-60.csv) | 54 | Full expanded set with every query type and edge case |
| [`week3-geography.csv`](week3-geography.csv) | 20 | Regional constraints |
| [`week3-historical.csv`](week3-historical.csv) | 20 | Period-accurate historical answers |
| [`week3-impossible.csv`](week3-impossible.csv) | 15 | Graceful refusal of self-contradicting queries |
| [`week3-jargon.csv`](week3-jargon.csv) | 20 | VC and tech jargon applied as real filters |
| [`week3-metric-ranking.csv`](week3-metric-ranking.csv) | 20 | Ranking by the requested metric, not revenue |
| [`week3-currency.csv`](week3-currency.csv) | 20 | Currency mismatches across 8 currencies |
| [`week3-gap-analysis.md`](week3-gap-analysis.md) | — | Remaining coverage gaps and queries to fill them |
| [`support-tickets.csv`](support-tickets.csv) | 10 | Synthetic support tickets (with PII) used as input to `/ticket-to-eval` |
| [`regression-dataset.csv`](regression-dataset.csv) | 10 | PII-stripped regression queries derived from those tickets |

To design a dataset like this for your own product, run `/uig` (see [`skills/uig-skill.md`](../skills/uig-skill.md)).
