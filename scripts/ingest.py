"""Fetch Dublin jobs from Jooble, normalize them, and save them to the database.

Change KEYWORD, then run:  .venv/bin/python scripts/ingest.py

Running it again does not create duplicates. Jobs already stored are updated in
place rather than inserted a second time, so the second run reports zero new jobs.
"""

from dublin_jobs.sources.jooble import iter_jobs, to_job
from dublin_jobs.store import upsert_jobs

KEYWORD = "data scientist"


def main() -> None:
    print(f"Fetching '{KEYWORD}' from Jooble...")

    validated_jobs = iter_jobs(KEYWORD)
    standard_jobs = (to_job(job) for job in validated_jobs)

    counts = upsert_jobs(standard_jobs)

    print(f"processed {counts['processed']} jobs")
    print(f"  new:           {counts['inserted']}")
    print(f"  already known: {counts['updated']}")


if __name__ == "__main__":
    main()
