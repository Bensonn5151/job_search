# Project Dublin — Phase Tracker

Concise living checklist. Full rationale: [Project_dublin.md](Project_dublin.md).
Legend: ✅ done · 🔨 in progress · ⬜ not started

## Phase 0 — Foundations 🔨
Goal: a safe, reproducible project skeleton.
- ✅ **0.1** Repo layout, venv (py3.12), `.gitignore`, `.env.example`, first commit
- ⬜ **0.2** Postgres `dublin_jobs` DB + `jobs` table (dedup key + reserved enrichment columns)

Concepts: project structure, secrets hygiene, relational schema design.
Done when: `pip install -e .` works and the `jobs` table exists locally.

## Phase 1 — Tier 1 APIs (Adzuna) ⬜
Goal: real Dublin jobs flowing into Postgres.
- ⬜ **1.1** Adzuna API key + first authenticated fetch
- ⬜ **1.2** Pagination + rate-limit / backoff handling
- ⬜ **1.3** Pydantic models for the response
- ⬜ **1.4** Normalize → upsert into `jobs` (dedup key)

Concepts: REST, auth, query params, pagination, typed validation, **normalization (the core)**.
Done when: one command pulls N Dublin jobs and idempotently upserts them (re-run adds 0 dupes).

## Phase 2 — Tier 2 ATS feeds + dedup ⬜
Goal: Greenhouse/Lever JSON feeds for curated Dublin employers; unify + dedup across sources.
Concepts: ATS JSON endpoints, schema unification, dedup (key now, embedding similarity later).
Done when: the same job from two sources collapses to one row.

## Phase 3 — AI enrichment + visa cascade ⬜  ← the killer feature
Goal: tag jobs with sponsorship signal + CSOL eligibility (cascade: rules → Haiku → classifier-later; §5).
Concepts: structured outputs, deltas-only enrichment, cost control, embeddings, pgvector.
Done when: a "gold feed" query returns CSOL-eligible **and** positive-signal Dublin jobs.

## Phase 4 — Tier 3 Irish boards (HTML) ⬜
Goal: IrishJobs / Jobs.ie / JobsIreland via polite HTML parsing.
Concepts: BeautifulSoup, robots.txt, throttling/backoff.

## Phase 5 — Tier 4 dynamic sites ⬜
Goal: Playwright only where there's no API and it's legal. LinkedIn/Indeed stay off-limits.
Concepts: headless browsers, anti-bot, when *not* to scrape.

## Phase 6 — Automation + UI ⬜
Goal: GitHub Actions scheduling, breakage monitoring, expiry detection, Streamlit filter UI.
Concepts: CI/cron, observability, simple front end.

---

### Metrics
**System-health** metrics (source coverage, freshness, dedup rate, enrichment cost, gold-feed size)
are tracked from Phase 1 on — see Project_dublin.md §3 (Monitoring).
**Personal job-hunt funnel** KPIs (applications → interviews → offers) are **private** —
tracked in Notion / `private/` (git-ignored), never in this public repo.
