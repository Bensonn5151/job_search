"""Fetch raw job listings from the Jooble API.

Jooble is a single POST endpoint. The API key goes in the URL path, and the
search (keywords, location, page) goes in the JSON body. A response looks like:

    {"totalCount": 82, "jobs": [ {..30 jobs..} ]}

This module only fetches. It returns Jooble's raw job dictionaries untouched;
turning them into our standard format happens later, in a separate step.
"""

import logging
import time
from collections.abc import Iterator

import httpx
from pydantic import ValidationError

from dublin_jobs.config import settings
from dublin_jobs.job import Job
from dublin_jobs.sources.models import JoobleJob

log = logging.getLogger(__name__)

# Jooble returns at most 30 jobs per page.
PAGE_SIZE = 30

# Wait this long between page requests, so we don't hammer the API.
DELAY_BETWEEN_PAGES = 1.0

# Give up on a single request after this many seconds.
REQUEST_TIMEOUT = 30.0


def fetch_jobs(
    keywords: str,
    location: str | None = None,
    max_pages: int = 20,
) -> Iterator[dict]:
    """Yield raw Jooble job dicts for a search, paging until the results run out.

    keywords:  what to search for, e.g. "data scientist".
    location:  where to search; defaults to the configured JOB_LOCATION.
    max_pages: a safety cap so a bug can never loop forever.
    """
    location = location or settings.job_location
    url = f"https://jooble.org/api/{settings.jooble_api_key}"

    with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
        for page in range(1, max_pages + 1):
            body = {"keywords": keywords, "location": location, "page": page}
            response = client.post(url, json=body)
            response.raise_for_status()

            jobs = response.json().get("jobs", [])
            yield from jobs

            # A short page (fewer than a full 30) means there are no more
            # results. Jooble's totalCount drifts between requests, so the page
            # length is the signal we trust.
            if len(jobs) < PAGE_SIZE:
                break

            # Be polite: pause before asking for the next page.
            time.sleep(DELAY_BETWEEN_PAGES)


def iter_jobs(
    keywords: str,
    location: str | None = None,
    max_pages: int = 20,
) -> Iterator[JoobleJob]:
    """Yield validated JoobleJob objects for a search.

    Wraps fetch_jobs and validates each raw record. A job that fails validation
    is logged and skipped, so one bad record never stops the whole run.
    """
    for raw in fetch_jobs(keywords, location, max_pages):
        try:
            yield JoobleJob.model_validate(raw)
        except ValidationError as error:
            log.warning("skipping malformed Jooble job %s: %s", raw.get("id"), error)


def to_job(job: JoobleJob) -> Job:
    """Rewrite a Jooble job into the project's standard Job shape.

    Jooble's own 'source' field names the site the advert came from, so it is not
    used here; our source is simply 'jooble'. Jooble's numeric id becomes the
    source_job_id, and the whole Jooble record is kept in raw.
    """
    return Job(
        source="jooble",
        source_job_id=str(job.id),
        title=job.title,
        url=job.link,
        company=job.company,
        location=job.location,
        description=job.snippet,
        posted_date=job.updated.date(),
        raw=job.model_dump(mode="json"),
    )
