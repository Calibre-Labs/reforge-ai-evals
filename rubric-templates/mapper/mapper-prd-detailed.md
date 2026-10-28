# Mapper: AI PRD

*A market research agent for technology categories. Live at mapper.calibrelabs.ai. October 2026.*

## 1. Product

Mapper is a market research agent. You name a technology category or a company, and it returns a market map: three to five companies, ranked, with the metrics you care about and the sources behind each number. It can also return a feature matrix, a funding timeline, a SWOT, a news digest or a written analysis. When it works, you have something you can paste into a doc in under a minute and defend in a meeting.

## 2. User and channel

A product manager, founder or investor getting ready for a meeting. The channel is a web chat, so this user will wait 20 or 30 seconds and wants a short answer. They will not forgive a number they repeat in the meeting that turns out to be wrong, stale or unsourced. Success is measured in figures you can defend.

## 3. Jobs to be done

- Map a category I name: "ai-native customer support startups".
- Map the competitors or comparables of a company I name: "databricks public comps".
- Rank by the metric I care about, and show the columns I ask for.
- Give me something I can share with my team.

These four are the common requests. The unusual ones matter as much for the rubric: a market in a past or future year ("search in 2003", "public ai companies in 2028"), a company that is a product line inside a bigger company, a request for a market that isn't technology at all, and a request for investment advice ("should i buy anthropic stock"). Run a User Input Grid (see `../../skills/uig/SKILL.md`) before locking Non-goals and the rubric.

## 4. Tool surface

Each session has two turns before the output. On the first turn the harness sends the scoping instructions, today's date and the user's message, with no tools, and Mapper replies with a scoping question. On the second turn it researches and builds the output.

| Tool | What it does | Reversible? |
|---|---|---|
| Research | One Gemini call with Google Search grounding. It searches the web, reads the results, and returns notes and the sources it used. Source links come back as Google redirect links. The course trace pages show this step as `web_search` and `read_page`. | Yes, read only |
| `build_market_map(title, description, columns, companies, rationale, sources)` | Shows the ranked table in the chat, with a short rationale and the sources. | Yes, it can be rebuilt |
| Five more output tools | A feature matrix, a funding timeline, a SWOT, a news digest and a written analysis. Today the harness picks the output tool from the wording of the request. | Yes, they can be rebuilt |

Every tool reads or can be redone. Sharing is part of the app, not the agent: the user can publish a link to any output from the Share button.

Mapper has no saved preferences yet. The user says which metric to rank by and which columns to include, usually in reply to the scoping question. The course trace pages show a `get_preferences` step that returns "No saved preferences" for this reason.

## 5. Autonomy

| Action | Autonomy | Why |
|---|---|---|
| Searching and reading pages | Acts | Read only. No cost to being wrong. |
| Building an output | Confirms scope first, then delivers what was confirmed | A map of the wrong category, metric or count wastes the user's turn. Today the harness asks a scoping question on every first turn. |
| A request outside technology market research, or a request for investment advice | Declines and says what it can do | Not the product. See Non-goals. |

This table is where Mapper's Trajectory and Governance lines come from.

## 6. Happy paths / Golden dataset

Thursday, 6:40pm, the evening before a board meeting.

1. The user types: "ai-native customer support startups".
2. Mapper replies with one scoping question. It proposes how many companies, the ranking metric and the columns.
3. The user corrects it: "Top 3 only, ranked by revenue. Include customer count."
4. Mapper researches and builds a map of three companies with revenue, customer count and the sources behind each figure.
5. It adds one or two sentences on what stands out.

A second path, which is harder. The user types "databricks public comps". Databricks is private, so the map is of public companies to compare it with, and some figures are for a business unit inside a bigger company. Mapper states how it read the request, marks every estimate, and says which figures it could not find instead of filling the cell.

These two scenarios, plus the ones the first real traces turn up, are the start of Mapper's golden dataset. Keep it in its own file next to the rubric.

## 7. Non-goals

- Markets where technology isn't the core of the product.
- Investment advice. Mapper ranks companies. It does not say what to buy.
- Private or proprietary data. Mapper only uses what it can find on the public web.
- Long reports. The output comes first, with at most two sentences around it.

## 8. Eval rubric

Success, in plain language: the map covers the companies, the metrics and the count the user asked for. Every figure has a time period and a source that supports it. Estimates are marked as estimates. A reader can check any number in under a minute by opening its source.

The known risks for this agent with these tools: a stale figure shown as current, an estimate shown as a reported number, a source that doesn't exist or doesn't say what the map says, and investment advice or a request outside technology answered anyway.

v1 has nine lines in four groups, two or three per group. Mapper makes six kinds of output (a market map, a feature matrix, a funding timeline, a SWOT, a news digest and a written analysis), so the lines talk about the output, not just the map. The full rubric is its own page, `mapper-rubric-v1.html`. In summary:

- **Outcome.** Every figure in the output names its period and has a source that supports it.
- **Trajectory.** Confirms scope, then delivers what was confirmed. Searches before stating a figure.
- **Governance.** Never shows an estimate as a reported figure. Cites only sources it retrieved. Declines investment advice and requests outside technology market research.
- **Experience.** Leads with the result, with at most two sentences around it. Says how it read the request and names any figure it couldn't find.

Trajectory and Experience are short on purpose. The odd paths aren't knowable until there are traces to read. A stale figure shown as current is a known risk with no line yet; it waits for a more detailed rubric.

## 9. Release thresholds

| Metric | Target | Why |
|---|---|---|
| Cost per session | Under $0.10 | It has to be cheap enough to use before every meeting. |
| Time to first map, median | Under 30 seconds | A web chat user will wait that long for research. |
| Sessions failing any Governance line | Under 1% at launch | One invented source or one piece of investment advice is what people remember. |

These are targets until there is data behind them.

## 10. Rollout

- **Internal use.** The team uses Mapper for its own research and reads every trace.
- **Cohort beta.** The course cohort uses it. A sample of sessions is reviewed against the rubric each week. Exit when the Governance threshold holds for two weeks.
- **General availability.** The thresholds become the ongoing bar. A breach after launch is a regression.

## 11. Open questions

- Should Mapper ask a scoping question on every first turn, or only when the request is unclear?
- Should the model pick the output type, instead of the harness matching words in the request?
- What counts as "current"? The last twelve months, or the last fiscal year?
- Should Mapper remember a user's ranking metric and columns across sessions?
- Which sources are good enough to cite for a private company's revenue?
- Owner: Sandhya. Needed before the cohort beta.
