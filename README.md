# Project Dublin — Multi-Source Job Scraper

A personal job-hunt tool for Dublin, Ireland: pull jobs from official APIs (and later
ATS feeds + select boards), normalize them into one schema, enrich with AI (visa-sponsorship
& Critical Skills signals), and store in Postgres.

> Public repo: **code is public, data and secrets are not.** Never commit `.env` or job data.

See [Project_dublin.md](Project_dublin.md) for the full design and roadmap (incl. the
visa-sponsorship cascade in §5 — the killer feature).

## Setup

```bash
# 1. Create the virtual environment (Python 3.11+)
python3.12 -m venv .venv
source .venv/bin/activate

# 2. Install the package (editable) + dev tools
pip install -e ".[dev]"

# 3. Configure secrets
cp .env.example .env        # then fill in real values

# 4. Start Postgres and apply migrations
docker compose up -d
python -m dublin_jobs.db.migrate
```

## Status

- [x] **Phase 0** — Foundations: repo layout, venv, secrets hygiene
- [ ] **Phase 1** — Tier 1 APIs: Adzuna → normalize → Postgres
- [ ] **Phase 2** — Tier 2 ATS feeds + dedup
- [ ] **Phase 3** — AI enrichment (extraction, embeddings, visa cascade)
- [ ] **Phase 4** — Tier 3 Irish boards (HTML)
- [ ] **Phase 5** — Tier 4 dynamic sites (Playwright)
- [ ] **Phase 6** — Automation + UI
