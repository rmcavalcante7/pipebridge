"""
Integration tests for the live pipe service facade.
"""

from __future__ import annotations

from typing import Any

import pytest

PIPE_ID = "307064875"


@pytest.mark.integration
def test_pipe_raw_live(live_pipefy_api: Any) -> None:
    """
    Validate raw pipe retrieval through the public facade.
    """
    query_body = """
        id
        name
    """

    result = live_pipefy_api.pipes.raw.get(PIPE_ID, query_body)

    assert isinstance(result, dict)
    pipe_data = result.get("data", {}).get("pipe", {})
    assert isinstance(pipe_data, dict)
    assert pipe_data.get("id") == PIPE_ID
    assert pipe_data.get("name")


@pytest.mark.integration
def test_pipe_structured_live(live_pipefy_api: Any) -> None:
    """
    Validate structured pipe retrieval through the public facade.
    """
    result = live_pipefy_api.pipes.structured.get(PIPE_ID)

    assert isinstance(result, dict)
    assert result["id"] == PIPE_ID
    assert "name" in result
    assert isinstance(result.get("phases", []), list)
    assert isinstance(result.get("labels", []), list)
    assert isinstance(result.get("users", []), list)


@pytest.mark.integration
def test_pipe_model_live(live_pipefy_api: Any) -> None:
    """
    Validate pipe model parsing and semantic helpers.
    """
    pipe = live_pipefy_api.pipes.get(PIPE_ID)

    assert pipe is not None
    assert pipe.id == PIPE_ID
    assert pipe.name
    assert isinstance(pipe.phases, list)
    assert isinstance(pipe.labels, list)
    assert isinstance(pipe.users, list)

    phases = pipe.iterPhases()
    assert isinstance(phases, list)
    if phases:
        first_phase = phases[0]
        assert pipe.getPhase(first_phase.id).id == first_phase.id
        assert pipe.requirePhase(first_phase.id).id == first_phase.id

    labels = pipe.iterLabels()
    if labels:
        first_label = labels[0]
        assert pipe.requireLabel(first_label.id).id == first_label.id

    users = pipe.iterUsers()
    if users:
        first_user = users[0]
        assert pipe.requireUser(first_user.id).id == first_user.id

    if hasattr(pipe, "_parse_errors"):
        assert isinstance(pipe._parse_errors, list)


@pytest.mark.integration
def test_pipe_custom_query_live(live_pipefy_api: Any) -> None:
    """
    Validate pipe retrieval with a custom query body.
    """
    query_body = """
        id
        name

        phases {
            id
            name
            fields {
                id
                label
                type
            }
        }
    """

    pipe = live_pipefy_api.pipes.get(PIPE_ID, query_body=query_body)

    assert pipe is not None
    assert pipe.id == PIPE_ID
    assert isinstance(pipe.phases, list)

    phases = pipe.iterPhases()
    if phases:
        first_phase = phases[0]
        assert first_phase.id
        assert isinstance(first_phase.fields, list)


@pytest.mark.integration
def test_pipe_field_catalog_live(live_pipefy_api: Any) -> None:
    """
    Validate live pipe field catalog retrieval with populated phase fields.
    """
    pipe = live_pipefy_api.pipes.getFieldCatalog(PIPE_ID)

    assert pipe is not None
    assert pipe.id == PIPE_ID
    assert isinstance(pipe.phases, list)

    total_fields = 0
    for phase in pipe.iterPhases():
        assert isinstance(phase.fields, list)
        total_fields += len(phase.fields)

        for field in phase.fields:
            assert hasattr(field, "id")
            assert hasattr(field, "label")
            assert hasattr(field, "type")
            assert hasattr(field, "options")
            assert hasattr(field, "uuid")

    assert total_fields > 0
