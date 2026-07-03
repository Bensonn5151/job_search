"""Typed models for the Jooble API response.

These mirror Jooble's own shape one-to-one. Their only job is to validate: if
a job arrives with a missing title or an id that isn't a number, we find out
here, at the edge of the system, instead of much later at the database.

Turning these into our standard cross-source job format is a separate step.
"""

from datetime import datetime

from pydantic import BaseModel


class JoobleJob(BaseModel):
    """One job exactly as Jooble returns it."""

    id: int
    title: str
    link: str
    updated: datetime

    # These can be blank in Jooble's data, so they default to empty.
    company: str = ""
    location: str = ""
    salary: str = ""
    snippet: str = ""
    source: str = ""
    type: str = ""


class JoobleResponse(BaseModel):
    """A full page of results from Jooble."""

    totalCount: int = 0
    jobs: list[JoobleJob] = []
