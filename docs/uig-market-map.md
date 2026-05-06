# User Input Grid: Market Map Agent

## Overview

The Market Map agent takes a single-turn natural language query and returns a ranked list of the top 3 players in the identified market category, with supporting metrics and citations. This UIG covers the four dimensions that drive meaningful diversity in what the agent must handle — and where it can fail.

**UIG Summary**

| Dimension | Values |
|-----------|--------|
| **Query Type** | Direct Category · Competitive Comps · Acquisition Targets · Historical Snapshot · Future/Speculative · Segment-Specific · Validation · Trend/Evolution |
| **Market Domain** | Tech/SaaS · Healthcare · Consumer/Brand · Financial · Industrial/Other |
| **Query Style** | Well-Specified · Under-Specified · Multi-Constraint · Jargon-Heavy · Edge/Out-of-Scope |
| **Temporal Frame** | Current · Historical · Future |

A 4-dimension grid with these values gives ~360 theoretical combinations. The practical eval set targets 50–80 queries that hit each dimension value at least 3 times, with deliberate coverage of edge cases.

---

## Dimension 1: Query Type

*What is the user actually asking the agent to do?*

| Value | Definition | Example Query |
|-------|-----------|---------------|
| **Direct Category** | User names a product/market category and wants the top players | `"team chat"` · `"healthcare EHR"` |
| **Competitive Comps** | User names a specific company and wants its market peers | `"databricks public comps"` · `"reforge competitors"` |
| **Acquisition Targets** | User frames the query as M&A scouting for a named acquirer | `"what AI security startups could Okta acquire in 2026?"` |
| **Historical Snapshot** | User specifies a past time period | `"search in 2003"` · `"social networking in 2008"` |
| **Future/Speculative** | User specifies a future year or "when X happens" | `"public AI companies in 2028"` |
| **Segment-Specific** | User scopes to a subsegment or persona within a market | `"AI coding assistants for enterprises"` · `"fintech for underbanked consumers"` |
| **Validation** | User names a company and asks where it ranks or whether it leads | `"is Stripe the top payments company?"` · `"where does HubSpot rank vs Salesforce?"` |
| **Trend/Evolution** | User asks how a market has changed across two time points | `"how has the cloud database market changed since 2020?"` · `"which AI companies have risen in the last 3 years?"` |

**Why this dimension matters:** The agent's failure modes differ by type. Acquisition targets require financial context the agent may hallucinate. Historical queries require period-accurate data. Speculative queries require hedging. Validation queries test whether the agent situates the named company correctly or just confirms the user's assumption. Trend/Evolution queries test whether the agent produces a meaningful delta rather than defaulting to a static current-state ranking.

---

## Dimension 2: Market Domain

*What industry or category does the query touch?*

| Value | Definition | Example Query |
|-------|-----------|---------------|
| **Tech/SaaS** | Software products, infrastructure, developer tools, AI | `"B2B payments infrastructure"` · `"cloud databases"` |
| **Healthcare** | Providers, software, devices, pharma | `"remote patient monitoring companies"` · `"healthcare billing software"` |
| **Consumer/Brand** | B2C brands, retail, media, consumer goods | `"streaming video services"` · `"running shoe brands"` |
| **Financial** | Banking, fintech, insurance, capital markets | `"neobanks for small businesses"` · `"crypto exchanges"` |
| **Industrial/Other** | Industrials, energy, aerospace, non-standard categories | `"spacecraft"` · `"carbon capture companies"` |

**Why this dimension matters:** The agent was likely trained and iterated on Tech/SaaS queries. Healthcare and Financial domains have compliance-sensitive data; Consumer domains have fewer "revenue" metrics and more brand/ratings data. The agent should still rank but may need to use different metric types.

---

## Dimension 3: Query Style

*How is the query phrased? How much can be inferred vs. must be assumed?*

| Value | Definition | Example Query |
|-------|-----------|---------------|
| **Well-Specified** | Clear market category, enough context to rank without assumptions | `"hospital EHR vendors 2025"` · `"streaming video services"` |
| **Under-Specified** | Ambiguous market scope — agent must interpret and state assumption | `"cloud"` · `"SaaS"` · `"brands people trust"` |
| **Multi-Constraint** | Query includes 2+ constraints the agent must satisfy simultaneously | `"AI security startups that Okta could acquire in 2026 with its cash"` |
| **Jargon-Heavy** | Query embeds industry/VC terms that must be correctly parsed before the market can be scoped | `"ai-native customer support startups"` · `"vc-backed PLG devtools"` · `"bootstrapped b2b SaaS"` |
| **Edge/Out-of-Scope** | Query is not a market map request (abstract concept, natural phenomenon, meta question) | `"happiness"` · `"is AI a market?"` · `"top 10 cloud companies"` |

**Why this dimension matters:** The Wk1 dataset is mostly well-specified. Under-specified and edge cases test whether the agent confidently hallucinates or gracefully handles uncertainty. Multi-constraint queries test whether the agent correctly applies all filters simultaneously. Jargon-heavy queries test a distinct failure mode: the agent may treat "ai-native" as decoration rather than a real filter, producing a list of traditional players instead of AI-first startups. This matters especially because power users of a market map tool speak in jargon.

**Common jargon terms and their correct interpretations:**

| Term | Correct filter |
|------|---------------|
| `ai-native` | Built on AI from the ground up; not legacy software with AI features bolted on |
| `vc-backed` | Has taken institutional venture capital; excludes bootstrapped and PE-backed |
| `PLG` | Product-led growth go-to-market; free tier or usage-based acquisition model |
| `bootstrapped` | Self-funded, no external VC — excludes vc-backed companies |
| `deep tech` | Hardware, biotech, frontier science; not software SaaS |
| `open source` | Core product is OSS-licensed; may have a commercial hosted wrapper |

---

## Dimension 4: Temporal Frame

*What time period does the query implicitly or explicitly reference?*

| Value | Definition | Example Query |
|-------|-----------|---------------|
| **Current** | Implicitly current (no year specified) or specifies 2024/2025 | `"team chat"` · `"hospital EHR vendors 2025"` |
| **Historical** | Specifies a past year or era | `"search in 2003"` · `"social networking in 2008"` |
| **Future** | Specifies a future year or event | `"public AI companies in 2028"` · `"humanoid robotics in 2028"` |

**Why this dimension matters:** The agent prompt specifies "prefer 2025 figures." Historical queries require the agent to override this default and use period-accurate data. Future queries require explicit uncertainty framing. Both are easy failure modes.

---

## Dataset Audit: Wk1 Dataset (10 rows)

### Coverage by Dimension

**Query Type**

| Value | Present in Wk1 | Examples | Coverage |
|-------|---------------|----------|----------|
| Direct Category | ✓ | "team chat", "healthcare EHR", "ai-native customer support startups" | STRONG |
| Competitive Comps | ✓ | "databricks public comps", "reforge competitors" | PARTIAL |
| Acquisition Targets | ✓ | "what AI security startups could Okta acquire..." | WEAK (1 example) |
| Historical Snapshot | ✓ | "search in 2003" | WEAK (1 example) |
| Future/Speculative | ✓ | "public ai companies in 2028" | WEAK (1 example) |
| Segment-Specific | ✗ | none | WEAK |

**Market Domain**

| Value | Present in Wk1 | Examples | Coverage |
|-------|---------------|----------|----------|
| Tech/SaaS | ✓ | databricks, team chat, AI security, reforge, AI customer support | STRONG |
| Healthcare | ✓ | "healthcare EHR" | PARTIAL (1 example) |
| Consumer/Brand | ✓ | "brands people trust" | WEAK (ambiguous, probably edge case) |
| Financial | ✗ | none | WEAK |
| Industrial/Other | ✓ | "spacecraft" | WEAK (likely out-of-scope) |

**Query Style**

| Value | Present in Wk1 | Examples | Coverage |
|-------|---------------|----------|----------|
| Well-Specified | ✓ | "databricks public comps", "healthcare EHR", "ai-native customer support startups" | STRONG |
| Under-Specified | ✓ | "brands people trust", "spacecraft" | PARTIAL (both are also edge cases) |
| Multi-Constraint | ✓ | "what AI security startups could Okta acquire in 2026 with its cash?" | WEAK (1 example) |
| Edge/Out-of-Scope | ✓ | "spacecraft", possibly "brands people trust" | PARTIAL |

**Temporal Frame**

| Value | Present in Wk1 | Examples | Coverage |
|-------|---------------|----------|----------|
| Current | ✓ | most queries | STRONG |
| Historical | ✓ | "search in 2003" | WEAK (1 example) |
| Future | ✓ | "public ai companies in 2028" | WEAK (1 example) |

---

### Gap Analysis

**High-priority gaps (entirely absent or 1 example — nothing would catch failures here):**

1. **Financial domain** — no financial services queries at all. The agent may rank fintech companies using tech metrics (ARR, valuation) when the correct metrics are AUM, net revenue, or TPV. Nothing in Wk1 would catch this.

2. **Segment-Specific queries** — no examples of scoped subsegment queries. The agent may over-expand or under-scope the market category without being tested on this.

3. **Multi-Constraint queries** — only 1 example. These are high-value for M&A/strategy use cases and test whether the agent correctly applies all constraints simultaneously.

4. **Under-Specified + Non-Edge queries** — both under-specified queries in Wk1 are also edge cases ("brands" and "spacecraft"). We need under-specified queries that *are* answerable (e.g., "cloud") to test whether the agent correctly states an assumption and proceeds.

5. **Historical × Healthcare/Financial** — no historical queries outside of Tech. The agent may use 2025 figures even when asked about 2009 healthcare or 2005 financial markets.

**Medium-priority gaps:**

6. Consumer/Brand domain needs well-scoped examples (not just the ambiguous "brands people trust").

7. Count-only / format-edge queries ("how many X", "top 10 X") test output format compliance.

8. Very short / malformed inputs test graceful handling of low-quality queries.

---

## Recommended Queries to Add (Wk2 Dataset)

Organized by gap filled. See `Wk2 Dataset.csv` for the full 50-row set with metadata tags.

### Financial Domain (not represented)
- `"personal finance apps"` — well-specified, current
- `"B2B payments infrastructure"` — well-specified, tech/financial overlap
- `"neobanks for small businesses"` — segment-specific, financial
- `"crypto exchanges by trading volume"` — well-specified, financial
- `"what fintechs could JPMorgan acquire with its 2025 cash reserves?"` — acquisition target, financial

### Segment-Specific (not represented)
- `"AI coding assistants for enterprises"` — well-specified, tech, segment
- `"low-code platforms for non-technical users"` — well-specified, tech, segment
- `"fintech for underbanked consumers"` — well-specified, financial, segment
- `"cybersecurity for healthcare organizations"` — well-specified, cross-domain, segment
- `"vertical SaaS for construction companies"` — well-specified, tech, segment

### Multi-Constraint (underrepresented)
- `"open source database companies with over $100M ARR that are still private"`
- `"cybersecurity identity companies that Microsoft hasn't acquired yet"`
- `"AI infrastructure companies Nvidia could acquire to strengthen its software stack in 2026"`
- `"what B2B SaaS companies in HR tech could Workday acquire given its $3B cash?"`
- `"LegalTech startups Thomson Reuters could acquire to compete with Harvey AI"`

### Historical × Non-Tech
- `"hospital systems by revenue in 2010"`
- `"retail banks by assets in 2005"`
- `"smartphone manufacturers in 2010"` (tech, but useful baseline)
- `"social networking sites in 2008"`
- `"database companies in 1995"`

### Future/Speculative
- `"humanoid robotics companies in 2028"`
- `"quantum computing hardware companies in 2030"`
- `"self-driving trucking companies in 2027"`
- `"brain-computer interface companies in 2029"`
- `"fusion energy companies when commercial fusion becomes viable"`

### Edge Cases (various types)
- `"best companies"` — too vague
- `"good tech companies"` — vague, no market category
- `"is AI a market?"` — meta question
- `"weather"` — natural phenomenon
- `"happiness"` — abstract concept
- `"biggest companies ever"` — too broad
- `"what will happen to AI in 2040?"` — predictive, no market data
- `"x"` — malformed/too short
- `"universities that teach AI"` — not a market
- `"friends"` — not a market

### Count-Only / Format-Edge
- `"how many CRM companies are there?"` — count, not ranking
- `"top 10 cloud companies"` — asks for 10, not 3
- `"cloud"` — single word, very broad
- `"SaaS"` — single word, extremely broad
- `"list all database vendors"` — exhaustive list request, not top 3
