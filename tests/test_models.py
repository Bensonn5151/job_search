"""Tests for the Jooble response models.

These are offline: they validate dictionaries directly and never call the API,
so they run instantly and never flake on the network.
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from dublin_jobs.sources.models import JoobleJob, JoobleResponse


def test_valid_job_parses(raw_jooble_job):
    """A full, well-formed job parses and its fields read back correctly."""
    job = JoobleJob.model_validate(raw_jooble_job)
    assert job.title == "Lead Data Engineer"
    assert job.company == "Mastercard"
    assert job.id == 8068512861483800019


def test_updated_becomes_datetime(raw_jooble_job):
    """Jooble sends 'updated' as a string; the model turns it into a datetime."""
    job = JoobleJob.model_validate(raw_jooble_job)
    assert isinstance(job.updated, datetime)
    assert job.updated == datetime(2026, 5, 15, 0, 0, 0)


def test_missing_required_field_is_rejected(raw_jooble_job):
    """A job without a title is bad data and must be refused at the edge."""
    del raw_jooble_job["title"]
    with pytest.raises(ValidationError):
        JoobleJob.model_validate(raw_jooble_job)


def test_optional_fields_default_to_empty(raw_jooble_job):
    """Jooble often omits salary and company; those default to empty strings."""
    del raw_jooble_job["salary"]
    del raw_jooble_job["company"]
    job = JoobleJob.model_validate(raw_jooble_job)
    assert job.salary == ""
    assert job.company == ""


def test_response_parses_page_of_jobs(raw_jooble_job):
    """A full page validates each job inside its jobs list."""
    page = {"totalCount": 2, "jobs": [raw_jooble_job, raw_jooble_job]}
    response = JoobleResponse.model_validate(page)
    assert response.totalCount == 2
    assert len(response.jobs) == 2
    assert all(isinstance(job, JoobleJob) for job in response.jobs)
