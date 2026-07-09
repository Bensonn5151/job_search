"""The standard job shape shared across every source.

Each source describes a job in its own format. Normalization rewrites a source's
job into this one shape, which mirrors the normalized columns of the jobs table.
From here on, nothing downstream needs to know which source a job came from.

Salary is deliberately left out for now. Jooble reports it as free text that is
often empty, and parsing it well is a later task. The untouched source record is
kept in the raw field, so no information is lost in the meantime.
"""

from datetime import date

from pydantic import BaseModel


class Job(BaseModel):
    # A job's identity: which source it came from, and that source's own id.
    source: str
    source_job_id: str

    title: str
    url: str
    company: str = ""
    location: str = ""
    description: str = ""
    posted_date: date | None = None

    # The original source record, kept for provenance and for later parsing.
    raw: dict = {}
