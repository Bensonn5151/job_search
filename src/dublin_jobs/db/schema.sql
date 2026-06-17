-- Canonical jobs schema.
-- Apply:  psql "$DATABASE_URL" -f src/dublin_jobs/db/schema.sql
-- Safe to re-run.

CREATE TABLE IF NOT EXISTS jobs (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    -- Source identity (unique together; drives idempotent upserts)
    source          TEXT NOT NULL,
    source_job_id   TEXT NOT NULL,

    -- Normalized fields
    title           TEXT NOT NULL,
    company         TEXT,
    location        TEXT,
    remote_policy   TEXT,
    salary_min      NUMERIC,
    salary_max      NUMERIC,
    currency        TEXT,
    seniority       TEXT,
    posted_date     DATE,
    url             TEXT NOT NULL,
    description     TEXT,
    tech_stack      TEXT[],

    -- Cross-source dedup fingerprint: hash(title + company + location)
    dedup_key       TEXT,

    -- Provenance and freshness
    raw             JSONB,
    first_seen_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_expired      BOOLEAN NOT NULL DEFAULT false,

    -- AI enrichment (populated later)
    sponsorship_signal      TEXT,        -- 'positive' | 'neutral' | 'negative'
    sponsorship_confidence  REAL,
    sponsorship_evidence    TEXT,
    csol_eligible           BOOLEAN,
    enriched_at             TIMESTAMPTZ,

    UNIQUE (source, source_job_id)
);
