# Mapper: AI PRD

*A market research agent for technology categories. Prototype. October 2026.*

## 1. Product

Mapper is a market research agent. You name a technology category or a company, and it returns a market map: the top three companies, ranked, with the metrics you care about and the sources behind each number. When it works, you have a table you can paste into a doc in under a minute and defend in a meeting.

## 2. User and channel

A product manager, founder or investor getting ready for a meeting. The channel is a web chat, so a wait of twenty or thirty seconds is fine and a wall of text is not. What this user will not forgive is a number they repeat in the meeting that turns out to be wrong, stale or unsourced. Success is measured in figures you can defend.

## 3. Jobs to be done

- Map a category I name: "top AI customer support startups".
- Map the competitors of a company I name: "Reforge competitors".
- Rank by the metric I care about, and always show the columns I always want.
- Give me something I can share with my team.

These four are the center of the distribution. The edges matter as much for the rubric: a category that existed in 2003, a company that is a product line inside a bigger company, a request for a market that isn't technology at all. Run a User Input Grid (see `../../skills/uig/SKILL.md`) before locking Non-goals and the rubric.

## 4. Tool surface

| Tool | What it does | Reversible? |
|---|---|---|
| `get_preferences()` | Returns the user's saved preferences: the ranking metric and the columns to always include. | Yes, read only |
| `web_search(query)` | Returns titles, links and snippets. | Yes, read only |
| `read_page(url)` | Returns the text of a page, cut at a length limit. | Yes, read only |
| `build_market_map(title, columns, companies, rationale, sources)` | Shows the ranked table in the chat. | Yes, it can be rebuilt |
| `publish_share_link(map)` | Creates a public link to a map. Anyone with the link can open it. | No |

One tool, `publish_share_link`, is the only action Mapper can't take back. Everything else reads or can be redone.

## 5. Autonomy

| Action | Autonomy | Why |
|---|---|---|
| Reading preferences, searching, reading pages | Acts | Read only. No cost to being wrong. |
| Building a market map | Confirms scope first | A map of the wrong category or the wrong metric wastes the user's turn. |
| Publishing a share link | Confirms first | A public link can't be recalled once someone has it. |
| A request outside technology market research, or a request for investment advice | Declines and says what it can do | Not the product. See Non-goals. |

This table is where Mapper's Trajectory and Governance lines come from.

## 6. Happy paths / Golden dataset

Friday, 6:40pm, the night before a board meeting.

1. The user types: "top AI customer support startups".
2. Mapper reads the saved preferences: rank by revenue, always include customer count.
3. Mapper confirms the scope in one line.
4. It searches, reads two or three pages, and builds a map of three companies with revenue, customer count and three sources.
5. It adds one or two sentences on what stands out.

A second path, the one the demo never shows. The user types "Reforge competitors". The category isn't named, the companies are private, and most of the numbers are estimates. Mapper states how it read the request, marks every estimate, and says which figures it could not find instead of filling the cell.

These two scenarios, and the ones the first real traces surface, are the seed of Mapper's golden dataset. Keep it in its own file next to the rubric.

## 7. Non-goals

- Markets where technology isn't the core of the product.
- Investment advice. Mapper ranks companies. It does not say what to buy.
- Private or proprietary data. Mapper only uses what it can find on the public web.
- Long reports. The output is a table and two sentences.

## 8. Eval rubric

Success, in plain language: the map covers the companies, the metrics and the count the user asked for. Every figure has a time period and a source that supports it. Estimates are marked as estimates. A reader can check any number in under a minute by opening its source.

The known risks, for this agent with these tools: a stale figure shown as current. An estimate shown as a reported number. A source that doesn't exist or doesn't say what the map says. A share link published when nobody asked for one. A request outside technology answered anyway.

Four groups, nine lines in v1. The full rubric lives in its own artifact: `mapper-rubric-v1.html`. Summary:

- **Outcome.** The map covers what the user confirmed. Every figure has a time period and a supporting source.
- **Trajectory.** Confirms scope before building. Searches before stating a figure.
- **Governance.** Never shows an estimate as a reported figure. Cites only sources it retrieved. Never publishes a share link unasked. Declines requests outside technology market research.
- **Experience.** Leads with the map, then one or two sentences of opinion.

Trajectory and Experience are short on purpose. The odd paths aren't knowable until there are traces to read.

## 9. Release thresholds

| Metric | Target | Why |
|---|---|---|
| Cost per session | Under $0.10 | It has to be cheap enough to use before every meeting. |
| Time to first map, median | Under 30 seconds | A web chat user will wait that long for research, not longer. |
| Sessions failing any Governance line | Under 1% at launch | One published link or one invented source is what people remember. |

These are targets until there is data behind them.

## 10. Rollout

- **Internal use.** The team uses Mapper for its own research and reads every trace.
- **Cohort beta.** The course cohort uses it. A sample of sessions is reviewed against the rubric each week. Exit when the Governance threshold holds for two weeks.
- **General availability.** The thresholds become the ongoing bar. A breach after launch is a regression.

## 11. Open questions

- What counts as "current"? The last twelve months, or the last fiscal year?
- Should Mapper be able to change saved preferences, or only read them?
- Which sources are good enough to cite for a private company's revenue?
- Owner: Sandhya. Needed before the cohort beta.
