"""Tests for turning a Jooble job into the standard Job shape.

Like the model tests, these run offline: normalization is a pure translation with
no network and no database, so it is fast and easy to check.
"""

from datetime import date

from dublin_jobs.sources.jooble import to_job
from dublin_jobs.sources.models import JoobleJob


def test_core_fields_map_across(raw_jooble_job):
    """Title, link, company and snippet land in the right standard fields."""
    job = to_job(JoobleJob.model_validate(raw_jooble_job))
    assert job.source == "jooble"
    assert job.source_job_id == "8068512861483800019"
    assert job.title == "Lead Data Engineer"
    assert job.url == raw_jooble_job["link"]
    assert job.company == "Mastercard"
    assert job.description == raw_jooble_job["snippet"]


def test_posted_date_is_a_date(raw_jooble_job):
    """Jooble's updated timestamp becomes a plain date on the standard job."""
    job = to_job(JoobleJob.model_validate(raw_jooble_job))
    assert job.posted_date == date(2026, 5, 15)


def test_raw_source_record_is_kept(raw_jooble_job):
    """The original Jooble record is preserved so nothing is lost."""
    job = to_job(JoobleJob.model_validate(raw_jooble_job))
    assert job.raw["company"] == "Mastercard"
