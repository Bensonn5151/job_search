# Project Dublin — Architecture

How the system fits together. The full design and reasoning are in [Project_dublin.md](Project_dublin.md);
the build order is in [PHASES.md](PHASES.md).

## 1. What kind of system this is

A **scheduled batch ETL pipeline with a pluggable source layer.** That framing drives every other choice:

- **Batch, not streaming** — listings change slowly; a daily/twice-daily run is enough. No queues, no streaming infra.
- **ELT-flavored** — store the **raw** payload, *then* transform. We can re-normalize without re-fetching when parsing improves.
- **Pluggable sources** — every source (API, ATS JSON, HTML, dynamic) hides behind one interface; the pipeline is source-agnostic.

## 2. System diagram

```
        ┌─────────── CONFIG ───────────┐        ┌──── SECRETS (.env) ────┐
        │ sources · location · CSOL    │        │ API keys · DB url      │
        │ list · salary thresholds     │        └───────────┬────────────┘
        └──────────────┬───────────────┘                    │
                       │                                     │
  SOURCES — pluggable connectors, one class per source (Tiers 1→4)
  ┌──────────┬────────────┬───────────┬──────────────┐      │
  │ Jooble   │ Greenhouse │ IrishJobs │ Playwright    │      │
  │ (API)    │ Lever(JSON)│ (HTML)    │ (dynamic)     │      │
  └────┬─────┴─────┬──────┴────┬──────┴──────┬────────┘      │
       │ fetch     │           │             │               ▼
       ▼           ▼           ▼             ▼     ┌───────────────────────┐
  ┌─────────────────────────────────────────────┐ │  ORCHESTRATION         │
  │ PIPELINE ORCHESTRATOR  (source-agnostic)     │◄┤  GitHub Actions cron   │
  │  fetch → parse+validate(Pydantic)            │ └───────────────────────┘
  │       → normalize(→canonical Job)            │
  │       → UPSERT (idempotent, ON CONFLICT)     │ ──► OBSERVABILITY
  └───────────────────────┬──────────────────────┘     (run metrics,
                          │ writes                       "source X = 0" alert)
                          ▼
  ┌──────────────── POSTGRES (system of record) ────────────────┐
  │  jobs (canonical)   employers (sponsors)   +pgvector embeds  │
  │  VIEW gold_feed = CSOL-eligible AND positive-signal AND fresh│
  └──────┬────────────────────────────────────────────┬─────────┘
         │ reads un-enriched / changed                 │ reads
         ▼                                             ▼
  ┌───────────────────────────┐              ┌──────────────────────┐
  │ ENRICHMENT (new/changed)  │              │ SERVE                 │
  │ rules, then a cheap AI    │              │ Streamlit + SQL       │
  │ +embeddings; writes back  │              │ filters / gold feed   │
  └───────────────────────────┘              └──────────────────────┘

  CROSS-CUTTING:  Dedup (key→embedding) · Freshness/expiry · Privacy/legal (strip PII, link-out)
```

## 3. Component responsibilities

| Component | Responsibility | Tools |
|---|---|---|
| **Source connectors** | Know one source; provide fetch, parse, and normalize | httpx, BeautifulSoup, Playwright |
| **Orchestrator** | Run each source through the pipeline; keep going if one source fails | Python command-line program |
| **Validator** | Reject or flag malformed data loudly | Pydantic |
| **Normalizer** | Convert each source's shape into the one standard job format | plain Python functions |
| **Store** | Save jobs without duplicates; the system of record | Postgres with psycopg |
| **Dedup** | Combine the same job found on different sources | SQL matching, then pgvector |
| **Enrichment** | Add the visa signal and embeddings, only for new or changed jobs | Claude Haiku and an embedding model |
| **Freshness** | Remove filled or expired jobs | SQL and link re-checks |
| **Serve** | Search and filter the results | Streamlit and SQL views |
| **Scheduling** | Run the whole pipeline unattended | GitHub Actions |
| **Monitoring** | Per-run counts and breakage alerts | logging and a run summary |

## 4. The core abstraction — the `Source` contract

Every connector implements the same shape, so the orchestrator never knows which tier a job came from:

```python
class Source(Protocol):
    name: str
    def fetch(self, query: SearchQuery) -> Iterable[RawRecord]: ...   # hit the source
    def parse(self, raw: RawRecord) -> SourceJob: ...                 # validate → typed (Pydantic)
    def normalize(self, sj: SourceJob) -> Job: ...                    # → the ONE canonical schema
```

Two payoffs. Adding a source means writing one class and adding a line of configuration; the
orchestrator does not change. And breakage stays contained: a broken `parse()` fails only its
own source, while the orchestrator records the failure and carries on with the rest.

## 5. A single run — the control loop

```python
for source in config.enabled_sources:                  # config-driven
    try:
        n = 0
        for raw in source.fetch(query):
            job = source.normalize(source.parse(raw))   # validate → canonical
            upsert(job)                                  # idempotent (ON CONFLICT)
            n += 1
        metrics.record(source.name, n)
        if n == 0: alert(f"{source.name} returned 0")    # breakage alarm
    except Exception as e:
        log.error(...); alert(...); continue             # fail-soft: one source down ≠ run down

mark_expired(not_seen_this_run)     # freshness
enrich_deltas()                     # only new/changed rows → cheap
```

## 6. Load-bearing decisions (accepted)

| Decision | Choice | Trade-off accepted | Why right here |
|---|---|---|---|
| Processing model | **Batch** | not real-time | jobs change slowly; saves streaming infra |
| Transform style | **Store raw, then normalize (ELT)** | extra storage | re-normalize w/o re-fetch; survives schema drift |
| Source coupling | **Uniform `Source` interface** | upfront abstraction | effortless extension + isolated breakage |
| Idempotency | **Upsert on `(source, source_job_id)`** | — | re-runnable; core effortlessness property |
| Enrichment placement | **Separate step, only new or changed jobs** | not "live" | keeps AI cost and run time flat |
| Storage | **One Postgres (+pgvector)** | not best-of-breed each | relational + vectors in one store; no extra infra |
| Failure policy | **Fail-soft per source, fail-loud per record** | — | resilience + observability together |

## 7. Phases fill in *one* diagram (we're not building six projects)

| Phase | What it adds |
|---|---|
| 0 | skeleton + Postgres box |
| 1 | orchestrator + first connector (Jooble) + `jobs` table + upsert |
| 2 | more connectors + Dedup block |
| 3 | Enrichment block + pgvector + `gold_feed` view |
| 4–5 | more connectors (HTML, Playwright) — *zero orchestrator change* |
| 6 | Orchestration (Actions) + Serve (Streamlit) + Observability hardening |
