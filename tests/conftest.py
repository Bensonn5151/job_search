"""Shared test helpers.

pytest loads this file automatically. Anything defined here with @pytest.fixture
can be used by any test simply by naming it as a function argument.
"""

import pytest


@pytest.fixture
def raw_jooble_job() -> dict:
    """One job in exactly the shape the Jooble API returns.

    Use this as a starting point: copy it and change or remove a field to test
    how validation reacts.
    """
    return {
        "id": 8068512861483800019,
        "title": "Lead Data Engineer",
        "company": "Mastercard",
        "location": "Ireland",
        "salary": "",
        "snippet": "Work on a set of products and services...",
        "source": "decentrajobs.com",
        "type": "Full-time",
        "link": "https://jooble.org/jdp/8068512861483800019",
        "updated": "2026-05-15T00:00:00.0000000",
    }
