# Project Dublin — Multi-Source Job Scraper (Dublin, Ireland)

## Project profile
- **Purpose:** personal job-hunt tool for a non-EU MSc AI grad who will need visa sponsorship.
- **Mode:** code-along — we build together, I teach the concepts at each step, we discuss as we go.
- **Public:** lives on GitHub (public repo) → code is public, **data and secrets are not**.
- **Language:** Python.
- **Scope:** all four source tiers, built **incrementally** (APIs first, dynamic scraping last).

---

## 0. Contrarian framing: don't "scrape" most of it

The smart architecture is **API-first + AI enrichment + targeted scraping only where there's no API.**
Scraping LinkedIn/Indeed directly is legally hostile and a maintenance treadmill. Pull clean data from
APIs/aggregators; spend effort on the *enrichment* layer (where the AI value and differentiation live).

---

## 1. Legal & GDPR (you're in the EU — non-negotiable)

| Concern | What to do |
|---|---|
| **Terms of Service** | LinkedIn & Indeed ban scraping (LinkedIn litigates). Avoid direct scraping; use partner APIs or skip. |
| **robots.txt** | Respect it. Disallowed paths = don't crawl. |
| **GDPR (Irish DPC enforces hard)** | Job posts contain personal data (recruiter names/emails). Personal use → keep minimal & private; don't build a public service around the data. Strip recruiter PII unless truly needed. |
| **Public GitHub repo** | **Never commit:** the database, scraped data dumps, or API keys. Use `.gitignore` + a `.env` file (commit a `.env.example` instead). |
| **Copyright** | JDs are copyrighted. Store metadata + link out; don't republish full JDs. |
| **Rate / load** | Be polite (throttle, backoff, cache). Hammering a site can cross into "misuse." |

---

## 2. Source tiers (built incrementally, API-first)

Prioritise sources by **reliability × sponsorship-yield**, not raw coverage. For a non-EU
sponsorship seeker a small set of high-yield, low-rot sources beats exhaustive coverage.

- **Tier 1 — Official APIs (start here):** Adzuna (excellent Ireland coverage, free tier), Jooble, Careerjet, Reed (UK/IE), The Muse. Clean, documented, stable.
- **Tier 1.5 — Public / semi-state (Ireland-specific, large in Dublin):**
  - **Universities (TCD, UCD, DCU)** — *high value:* research/academic + professional roles are often Critical-Skills-eligible and universities actively sponsor non-EU staff. Usually **CoreHR (Access Group)** → tailored HTML/feed parsing.
  - **PublicJobs.ie** (civil service, HSE, Dublin City Council) — huge, but most roles require Irish/EU/EEA citizenship or residency, so **low visa-yield:** index it and let the visa classifier mark it, but don't prioritise the crawl.
- **Tier 2a — Stable ATS JSON (gold):** Greenhouse, Lever, Ashby, SmartRecruiters expose near-uniform JSON feeds (e.g. `boards-api.greenhouse.io/...`). Best ROI, least breakage. Curate Dublin tech employers (Stripe, Intercom, HubSpot, AWS, Google, Meta, Irish startups).
- **Tier 2b — Brittle per-tenant JSON (valuable, higher maintenance):** unlocks banking, aircraft leasing, pharma, big enterprise.
  - **Workday** — per-tenant `…/wday/cxs/…` JSON (POST), may need session headers; structure varies per company.
  - **SuccessFactors (SAP) / Taleo (Oracle)** — classic Dublin enterprise (AIB, Bank of Ireland, ESB, Ryanair). Career sites vary per customer; typically OData + API key or HTML parsing. Lower priority, per-employer upkeep.
- **Tier 3 — Irish boards (HTML):** IrishJobs.ie, Jobs.ie, Silicon Republic Careers (small but curated).
- **Tier 4 — Dynamic / anti-bot sites (last, only if no API):** Playwright where genuinely needed. **LinkedIn/Indeed stay off-limits** for direct scraping.

**Employer-discovery feeds (cross-cutting — not job listings):** Techireland.org, Scale Ireland, Enterprise Ireland / IDA company lists. These map *which* Dublin startups/scaleups exist → feed the **curated employer list** for Tier 2 and seed the **known-sponsor list** that powers the visa cascade's L1 rules (§5). Modelled as an `EmployerSource` sibling of the `Source` interface — no architecture change.

---

## 3. Core technical considerations

- **Normalization schema (the real work):** unify into one shape — `title, company, location, remote_policy, salary_min/max, seniority, posted_date, source, url, description, tech_stack[], visa_signal`. ~50% of the project.
- **Deduplication:** same job on many sources. Dedup by `(normalized_title + company + location)`, then **embedding similarity** for near-dupes.
- **Freshness / expiry:** detect & drop filled/expired posts (recheck URLs; track first/last seen).
- **Anti-bot reality:** dynamic sites need **Playwright**; many sit behind Cloudflare. Brittle — prefer APIs.
- **Scheduling:** start with cron / **GitHub Actions**; graduate to **Prefect/Airflow** if it grows.
- **Storage:** **Postgres + pgvector** (relational + embeddings in one). Optional **Meilisearch/Typesense** for search UI.
- **Monitoring:** scrapers silently break. Alert on "source X returned 0 jobs today."
- **Politeness/robustness:** per-domain rate limits, exponential backoff, retries, caching, realistic headers.
- **Tooling:** **httpx + Pydantic** (APIs), **BeautifulSoup** (HTML), **Playwright** (dynamic), optionally **Scrapy** or **crawl4ai/Firecrawl** (LLM-ready markdown).

---

## 4. Where AI genuinely helps (and where it's a trap)

**High value:**
- **LLM extraction** of structured fields from messy JDs. Use **structured outputs / JSON schema**, run only on new/changed jobs, use a **cheap model (Claude Haiku)**.
- **Embeddings:** semantic dedup, "find similar jobs," and **CV matching** (embed profile → rank by cosine → LLM-rerank top 50).
- **Classification/tagging:** category, seniority, tech stack — and the visa feature below.

**Trap / overkill:**
- **Fully agentic browsing** (agent clicking each site) — slow, expensive, flaky. Use deterministic fetch + LLM *parse*, not LLM *navigation*.
- Running an LLM on **every job every run** — cache; enrich deltas only.

---

## 5. The killer feature (worth more than the scraper itself)

Non-EU path: Stamp 2 → **Graduate scheme (Stamp 1G, up to 24 months)** → **Critical Skills / General Employment Permit**.
Goal: a feed of *"Dublin AI/ML jobs that realistically lead to a Critical Skills Permit"* — it **solves the real problem** and is a **novel portfolio feature**. **Highest-leverage thing in the build.**

### 5.1 It's three signals, not one NLP problem

The question "will this job sponsor me / qualify for a Critical Skills Permit?" decomposes into three sub-problems with very different right tools. Don't collapse them into one text classifier.

| Signal | Where the truth lives | Right tool |
|---|---|---|
| **Critical Skills eligibility** | The official **CSOL** (occupation list) + a **salary threshold** (~€38k on-list / ~€64k off-list — *these change yearly*) | **Rules + lookup.** Map role title → occupation, compare salary to threshold. A rulebook, not something to learn. |
| **Does this employer sponsor?** | Mostly an **employer property**, not the JD. Ireland's DETE publishes employment-permit data; known sponsors are a list. | **Structured data / allow-list.** A company that sponsored before beats any sentence in the JD. |
| **Does the JD text signal sponsorship?** | The free text — **and its negation** | This is the only real **NLP** part. |

### 5.2 Why naive approaches fail

- **Keyword-only is dangerous for the decision.** Good for *recall* (flag candidates), bad for *precision* because of negation/paraphrase: *"unable to provide visa sponsorship"* (keyword present, means the opposite), *"must already be authorized to work in Ireland"* / *"EU/EEA applicants only"* (strong **negatives**, no keyword overlap). Track **negative** keywords as deliberately as positive ones.
- **Training a classifier first is a cold-start trap.** A "small" classifier needs hundreds of balanced, hand-labeled examples you don't have. Label them by your keywords and it just relearns the keywords. ML without labels = the trap §4 warns about.

### 5.3 Architecture — cheapest-first cascade (rules → LLM → distill)

```
JD + employer + salary
  └─ L1 RULES (free, instant)
       • CSOL lookup + salary threshold (config)      ← deterministic eligibility
       • known-sponsor employer list                  ← highest-precision signal
       • keyword recall pass (positive AND negative)  ← flags candidates, doesn't decide
  └─ L2 LLM (Claude Haiku, structured output)         ← only on NEW/CHANGED jobs, cached
       → {signal: pos|neutral|neg, confidence, evidence_span, csol_guess}
         handles negation & paraphrase the regex can't
  └─ L3 LEARNED classifier (LATER, optional)          ← only once labels are a free byproduct
       distill the LLM to cut cost at scale; a personal-scale tool may never need it
```

Labels accumulate for free: every LLM label you later confirm/correct (you applied, you found out) = one training example. Train L3 only when the data already exists and cost justifies it — not before.

### 5.4 Implications for earlier phases (cheap now, saves a migration later)

- **Phase 1 schema** reserves nullable enrichment columns: `sponsorship_signal`, `sponsorship_confidence`, `sponsorship_evidence`, `csol_eligible`, plus `enriched_at` (so we enrich **deltas only**).
- Plan an **`employers` table** with an `is_known_sponsor` flag (the employer signal is structured, not text).
- Keep the **CSOL list + salary thresholds as config/data**, never hardcoded — they change yearly.

---

## 6. Incremental roadmap (each phase = working software + concepts learned)

| Phase | Build | Concepts you learn |
|---|---|---|
| **0 — Foundations** | Repo, venv, `.env`/secrets, `.gitignore`, project layout | Python project structure, git hygiene, secrets management |
| **1 — Tier 1 APIs** | Adzuna → normalize → store in Postgres | REST APIs, pagination, rate limits, Pydantic models, SQL basics |
| **2 — Tier 2 ATS + dedup** | Greenhouse/Lever JSON feeds; unify schema; dedup | JSON endpoints, schema unification, dedup strategies |
| **3 — AI enrichment** | LLM extraction (Haiku, structured output), embeddings, pgvector, CV matching, **visa classifier** | Structured outputs, embeddings, vector search, prompt design, cost control |
| **4 — Tier 3 Irish boards** | IrishJobs/Jobs.ie/JobsIreland via HTML parsing | BeautifulSoup, HTML parsing, politeness/throttling |
| **5 — Tier 4 dynamic sites** | Playwright for anti-bot pages, only where legal/needed | Headless browsers, anti-bot, when NOT to scrape |
| **6 — Automation + UI** | GitHub Actions scheduling, monitoring, expiry, Streamlit UI with filters | Cron/CI, observability, simple front end |

**Stack:** Python · httpx/Scrapy (+Playwright where needed) · Postgres+pgvector · Claude Haiku for extraction · embedding model · Streamlit front end · GitHub Actions scheduling.

---

## 7. Biggest pitfalls

- Underestimating **normalization + dedup** (the unglamorous 70%).
- Scraping LinkedIn/Indeed → blocked/banned. Start API-first.
- Burning LLM budget by enriching everything every run.
- Ignoring **scraper rot** — build breakage alerts from day one.
- Committing data/keys to the public repo — `.gitignore` from commit #1.

---

## 8. Next step
Start **Phase 0 + Phase 1**: scaffold the repo (layout, `.env.example`, `.gitignore`, Postgres schema)
and pull the first real Dublin jobs from the Adzuna API into the database.

---

## 9. Success metrics / KPIs (what makes this build run *effortlessly*)

These are the engineering success factors — the qualities/features that keep the project low-maintenance,
hard to silently break, and cheap to extend. "Effortless" = **idempotency + observability + API-first**.
Ranked by leverage.

| # | KPI / success factor | Measurable indicator | Why it = effortless | Phase |
|---|---|---|---|---|
| 1 | **Normalization quality** | % jobs with all core fields correctly populated; % needing manual fix (→0) | Clean unified data makes filtering, dedup, UI, and the visa feature trivial. ~50–70% of the value. | 1 |
| 2 | **Idempotent / re-runnable pipeline** | re-run adds **0** duplicate rows; never corrupts state | Run anytime, retry safely, schedule without fear. The core effortlessness property. | 1 |
| 3 | **Dedup accuracy** | false-merge rate ≈ 0; missed-dupe rate low | Same job on N sources → 1 row; feed stays clean as sources grow. | 2 |
| 4 | **Breakage detection / observability** | time-to-detect a zero/broken source ≤ 1 run; **0 silent failures** | It shouts when something breaks instead of quietly returning nothing. | 1→6 |
| 5 | **API-first resilience** | % of data from stable APIs/JSON vs brittle HTML (higher = better) | APIs break far less than HTML → maintenance near zero. | 1–2 |
| 6 | **Politeness & robustness** | 429/block rate ≈ 0; transient errors auto-recovered (retry/backoff) | Survives flaky networks + rate limits unattended. | 1→4 |
| 7 | **Deltas-only enrichment + caching** | $/run & runtime stay ~flat as DB grows; % re-enriched ≈ 0 | AI layer stays cheap and fast forever; cost doesn't creep. | 3 |
| 8 | **Config-driven sources/location** | add a source or change city with **0 code changes** | Effortless extensibility (location = config, not hardcoded). | 1→ |
| 9 | **Freshness / expiry** | % expired jobs still shown ≈ 0; median job age low | Self-cleaning feed — no dead listings. | 3→6 |
| 10 | **Visa-signal trustworthiness** | sponsorship/CSOL precision & recall vs spot-checks | The differentiator only matters if you can trust it. | 3 |
| 11 | **Automation** | runs on schedule with **0 manual steps** | Works while you sleep. | 6 |

**Earliest, highest-leverage three:** #1 normalization, #2 idempotency, #4 breakage detection — nail these in Phase 1.

> Note: *personal job-hunt funnel* metrics (applications → interviews → offers) are out of scope here and
> stay **private** (Notion / `private/`), never in this public repo.
