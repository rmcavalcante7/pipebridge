"""
Integration tests for the live phase service facade.
"""

from __future__ import annotations

from typing import Any

import pytest

PHASE_ID = "342616256"


@pytest.mark.integration
def test_phase_raw_live(live_pipefy_api: Any) -> None:
    """
    Validate raw phase retrieval through the public facade.
    """
    query_body = """
        id
        name
    """

    result = live_pipefy_api.phases.raw.get(PHASE_ID, query_body)

    assert isinstance(result, dict)
    phase_data = result.get("data", {}).get("phase", {})
    assert isinstance(phase_data, dict)
    assert phase_data.get("id") == PHASE_ID
    assert phase_data.get("name")


@pytest.mark.integration
def test_phase_structured_live(live_pipefy_api: Any) -> None:
    """
    Validate structured phase retrieval through the public facade.
    """
    result = live_pipefy_api.phases.structured.get(PHASE_ID)

    assert isinstance(result, dict)
    assert result["id"] == PHASE_ID
    assert "name" in result
    assert isinstance(result.get("fields", []), list)


@pytest.mark.integration
def test_phase_model_live(live_pipefy_api: Any) -> None:
    """
    Validate phase model parsing and semantic field helpers.
    """
    phase = live_pipefy_api.phases.get(PHASE_ID)

    assert phase is not None
    assert phase.id == PHASE_ID
    assert phase.name
    assert isinstance(phase.fields, list)

    fields = phase.iterFields()
    assert isinstance(fields, list)
    if fields:
        first_field = fields[0]
        assert phase.getField(first_field.id).id == first_field.id
        assert phase.requireField(first_field.id).id == first_field.id

    if hasattr(phase, "_parse_errors"):
        assert isinstance(phase._parse_errors, list)


@pytest.mark.integration
def test_phase_custom_query_live(live_pipefy_api: Any) -> None:
    """
    Validate phase retrieval with a custom query body.
    """
    query_body = """
        id
        name

        cards(first: 5) {
            edges {
                node {
                    id
                    title
                }
            }
        }
    """

    phase = live_pipefy_api.phases.get(PHASE_ID, query_body=query_body)

    assert phase is not None
    assert phase.id == PHASE_ID
    assert isinstance(getattr(phase, "cards_preview", []), list)
