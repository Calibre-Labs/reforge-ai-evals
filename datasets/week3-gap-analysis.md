# Dataset Gap Analysis — Week 3

This document captures the edge case and coverage gaps identified after auditing the Week 1–3 datasets against the User Input Grid (UIG). Use it to guide new dataset creation.

---

## What Week 3 Datasets Already Cover

| File | Dimension Targeted | Notes |
|---|---|---|
| `week3-geography.csv` | Domain × regional constraint | SE Asia, India, Europe, Africa, China |
| `week3-historical.csv` | Temporal: Historical | Past time periods, various domains |
| `week3-impossible.csv` | Style: Edge/Out-of-Scope | Logically self-contradicting queries |
| `week3-jargon.csv` | Style: Jargon-Heavy | VC/tech terms that must be correctly parsed |
| `week3-metric-ranking.csv` | Style: Multi-Constraint | Non-standard ranking criteria (NPS, uptime, GitHub stars) |

---

## Missing Query Types (No Dedicated Dataset Yet)

These are UIG query types with no dedicated week 3 coverage. Each has a distinct failure mode the current evaluators won't catch.

| Query Type | Example Queries | Why It Matters |
|---|---|---|
| **Validation** | "Is Stripe the top payments company?", "Where does HubSpot rank vs Salesforce?" | Tests whether the agent confirms user assumptions vs. corrects them. High hallucination risk: agent may validate a false premise confidently. |
| **Trend/Evolution** | "How has the cloud DB market changed since 2020?", "Which AI companies have risen in the last 3 years?" | Tests if the agent produces a meaningful delta or just re-ranks current state. Hard to evaluate without a specific reference judge. |
| **Competitive Comps** | "Databricks public comps", "Reforge competitors" | Tests whether the agent scopes to true peer companies vs. the whole category. Also tests whether it uses the right comparison metric (revenue multiples vs. headcount). |
| **Future/Speculative** | "Humanoid robotics in 2028", "Quantum computing hardware in 2030" | Tests uncertainty framing and hedging. Agent should label projections as projections — not present them as current fact. |
| **Acquisition Targets** | "What could Salesforce acquire to compete with ServiceNow?", "AI infrastructure companies Nvidia could acquire in 2026" | Tests multi-constraint financial reasoning. Agent may hallucinate acquisition prices or apply the wrong financial criteria. |
| **Under-Specified but Answerable** | "Cloud", "SaaS", "Enterprise software", "Productivity apps" | Distinct from impossible queries: these are vague but valid. Agent should state its interpretation and proceed — not refuse or hallucinate confidently. |

---

## Other Gaps Worth Filling

### 1. Wrong-Assumption Validation
Queries where the user's premise is factually incorrect.

**Examples:**
- "Is Bing the top search engine?" (No — Google is)
- "Is Zoom the leader in video conferencing in 2025?" (Debatable — Microsoft Teams has surpassed it by many metrics)
- "Is WeWork the top coworking space company?" (Bankrupt in 2023)

**Why it matters:** Tests whether the agent politely corrects a false premise or blindly confirms the user's assumption. A well-calibrated agent should rank accurately even when the user implies a wrong answer.

---

### 2. Defunct / Dead Markets
Queries about markets or companies that no longer exist as stated.

**Examples:**
- "MySpace competitors in 2008"
- "Blockbuster's video rental competitors"
- "Palm smartphone competitors"
- "What was the search market before Google?"

**Why it matters:** Tests period-accurate data retrieval. The agent may hallucinate companies that existed later, or apply 2025 knowledge to a 2005 market. Also good for stress-testing the `has_metrics` evaluator — metrics for defunct companies are often harder to format consistently.

---

### 3. Markets Too Small for Top-3
Niche markets where fewer than 3 credible, rankable players exist.

**Examples:**
- "Commercial fusion energy companies" (fewer than 3 with public revenue)
- "LiDAR manufacturers for autonomous vehicles" (very few dedicated players)
- "Space tourism companies" (handful of players, none with meaningful public revenue yet)
- "Quantum networking hardware companies"

**Why it matters:** The prompt requires exactly 3 ranked companies. When fewer than 3 credible players exist, the agent faces a dilemma: hallucinate a third, refuse, or surface the limitation. The current evaluator (`company_count`) will mechanically penalize any response that doesn't list 3 — even a correct one that explains only 2 exist.

---

### 4. Format-Breaking Queries
Queries that ask for something other than top 3, testing output format compliance.

**Examples:**
- "Top 10 cloud companies" (asks for 10, not 3)
- "Give me a list of all CRM vendors" (exhaustive, not top 3)
- "How many BI tools are there?" (count, not ranking)
- "Compare Salesforce and HubSpot" (binary comparison, not top 3)
- "Which is better: Slack or Teams?" (preference query)

**Why it matters:** These test whether the agent correctly interprets its task constraints vs. the user's literal request. A good response produces top 3 and notes the constraint; a bad response either gives 10 or refuses to answer.

---

### 5. Non-Market Queries Disguised as Market Queries
Plausible-sounding queries that aren't actually asking for company rankings.

**Examples:**
- "Universities that teach AI" (institutions, not products)
- "Which countries invest most in AI" (geopolitical, not market)
- "Biggest VC funds by AUM" (investors, not product companies)
- "Top AI researchers by citation count" (people, not companies)
- "Best open source projects for ML" (OSS projects, not companies)

**Why it matters:** These test the agent's ability to recognize when a query isn't a market map request vs. when it's a market that just uses different entities (universities, funds, researchers). The boundary is genuinely fuzzy — a good agent navigates it rather than silently picking one interpretation.

---

## Recommended Priority Order

1. **Validation (wrong-assumption variant)** — high real-world frequency; distinct failure mode current evaluators miss
2. **Trend/Evolution** — common strategic use case; needs a new evaluator (delta judge)
3. **Competitive Comps** — already in the UIG but no dedicated dataset
4. **Markets too small for top-3** — exposes a gap in `company_count` evaluator logic
5. **Future/Speculative** — good for demonstrating uncertainty calibration failures
6. **Format-breaking queries** — straightforward to build; good for evaluator stress-tests
