"""Save standard Job records into the jobs table without creating duplicates.

A job's identity is its source together with that source's own id for the job.
When a job with that identity is already stored, we update it in place instead of
inserting a second copy. On such an update we refresh the content fields and the
last_seen_at time, but we leave first_seen_at and the enrichment columns alone, so
re-running the fetch never discards a judgement we have already paid for.
"""

from collections.abc import Iterable

import psycopg
from psycopg.types.json import Json

from dublin_jobs.config import settings
from dublin_jobs.job import Job

UPSERT = """
    INSERT INTO jobs
        (source, source_job_id, title, url, company, location, description, posted_date, raw)
    VALUES
        (%(source)s, %(source_job_id)s, %(title)s, %(url)s, %(company)s,
         %(location)s, %(description)s, %(posted_date)s, %(raw)s)
    ON CONFLICT (source, source_job_id) DO UPDATE SET
        title = EXCLUDED.title,
        url = EXCLUDED.url,
        company = EXCLUDED.company,
        location = EXCLUDED.location,
        description = EXCLUDED.description,
        posted_date = EXCLUDED.posted_date,
        raw = EXCLUDED.raw,
        last_seen_at = now()
"""


def upsert_jobs(jobs: Iterable[Job]) -> dict:
    """Save each job, reporting how many were new and how many already existed.

    We count the rows before and after the run. The difference is how many jobs
    were new; the rest were jobs we had already stored and simply updated.
    """
    with psycopg.connect(settings.database_url) as conn:
        before = conn.execute("SELECT count(*) FROM jobs").fetchone()[0]

        processed = 0
        for job in jobs:
            params = job.model_dump()
            params["raw"] = Json(job.raw)
            conn.execute(UPSERT, params)
            processed += 1

        after = conn.execute("SELECT count(*) FROM jobs").fetchone()[0]

    inserted = after - before
    return {"processed": processed, "inserted": inserted, "updated": processed - inserted}
