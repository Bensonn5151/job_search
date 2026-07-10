# Project Dublin — Multi-Source Job Scraper

A personal job-hunt tool for Dublin, Ireland: pull jobs from official APIs (and later
ATS feeds + select boards), normalize them into one schema, enrich with AI (visa-sponsorship
& Critical Skills signals), and store in Postgres.

> Public repo: **code is public, data and secrets are not.** Never commit `.env` or job data.

See [Project_dublin.md](Project_dublin.md) for the full design and the reasoning behind the
visa feature.

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

- [x] **Phase 0** — Foundations: repository, environment, database
- [ ] **Phase 1** — Job APIs: fetch, normalize, store
  - [x] Jooble — paging, typed models, normalize, upsert
  - [ ] Careerjet — second source behind the same interface
- [ ] **Phase 2** — Company hiring systems and duplicate removal
- [ ] **Phase 3** — AI enrichment and the visa filter
- [ ] **Phase 4** — Irish job boards and public-sector roles
- [ ] **Phase 5** — Sites that need a real browser
- [ ] **Phase 6** — Automation and a simple interface
