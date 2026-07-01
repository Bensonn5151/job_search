"""Fetch raw job listings from the Jooble API.

Jooble is a single POST endpoint. The API key goes in the URL path, and the
search (keywords, location, page) goes in the JSON body. A response looks like:

    {"totalCount": 82, "jobs": [ {..30 jobs..} ]}

This module only fetches. It returns Jooble's raw job dictionaries untouched;
turning them into our standard format happens later, in a separate step.
"""

import time
from collections.abc import Iterator

import httpx

from dublin_jobs.config import settings

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
