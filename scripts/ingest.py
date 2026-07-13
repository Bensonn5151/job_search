"""Fetch Dublin jobs from Jooble, normalize them, and save them to the database.

Run with no arguments to search the default keywords, or name your own:

    .venv/bin/python scripts/ingest.py
    .venv/bin/python scripts/ingest.py "machine learning" "data analyst"

Running it again does not create duplicates. Jobs already stored are updated in
place rather than inserted a second time. A job that matches two keywords is safe
for the same reason: its identity is the same both times, so the second sighting
becomes an update.
"""

import argparse

from dublin_jobs.sources.jooble import iter_jobs, to_job
from dublin_jobs.store import upsert_jobs

# The standard sweep: the searches worth running every time. Keywords given on
# the command line replace this list for one run without touching the code.
DEFAULT_KEYWORDS = [
    "data scientist",
    "data engineer",
    "machine learning",
    "AI engineer",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch Dublin jobs and save them.")
    parser.add_argument(
        "keywords",
        nargs="*",
        default=DEFAULT_KEYWORDS,
        help="search terms to fetch (defaults to the standard sweep)",
    )
    args = parser.parse_args()

    total_processed = 0
    total_new = 0

    for keyword in args.keywords:
        print(f"Fetching '{keyword}' from Jooble...")

        validated_jobs = iter_jobs(keyword)
        standard_jobs = (to_job(job) for job in validated_jobs)

        counts = upsert_jobs(standard_jobs)
        total_processed += counts["processed"]
        total_new += counts["inserted"]

        print(f"  new: {counts['inserted']}   already known: {counts['updated']}")

    print(f"\ntotal processed: {total_processed}   total new: {total_new}")


if __name__ == "__main__":
    main()
