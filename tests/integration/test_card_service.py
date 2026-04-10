"""
Integration tests for the live card service facade.
"""

from __future__ import annotations

from typing import Any

import pytest

from tests.live_examples import (
    DEFAULT_CREATE_DESCRIPTION_VALUE,
    DEFAULT_LIVE_PIPE_ID,
    normalize_live_field_value,
)

CARD_ID = "1328390184"
PIPE_ID = DEFAULT_LIVE_PIPE_ID
PHASE_ID = "342616255"


@pytest.mark.integration
def test_card_raw_live(live_pipefy_api: Any) -> None:
    """
    Validate raw card retrieval through the public facade.
    """
    query = """
    fields {
      field {
        id
      }
      value
    }
    """

    result = live_pipefy_api.cards.raw.get(CARD_ID, query)

    assert isinstance(result, dict)
    card_data = result.get("data", {}).get("card", {})
    assert isinstance(card_data, dict)
    assert isinstance(card_data.get("fields", []), list)


@pytest.mark.integration
def test_card_structured_live(live_pipefy_api: Any) -> None:
    """
    Validate structured card retrieval through the public facade.
    """
    result = live_pipefy_api.cards.structured.get(CARD_ID)

    assert isinstance(result, dict)
    assert result.get("id") == CARD_ID
    assert "title" in result
    assert isinstance(result.get("fields", []), list)


@pytest.mark.integration
def test_card_structured_custom_query_live(live_pipefy_api: Any) -> None:
    """
    Validate structured card retrieval with a custom query body.
    """
    query = """
        fields {
            field {
                id
            }
            value
        }
    """

    result = live_pipefy_api.cards.structured.get(CARD_ID, query)

    assert isinstance(result, dict)
    assert isinstance(result.get("fields", []), list)


@pytest.mark.integration
def test_card_model_live(live_pipefy_api: Any) -> None:
    """
    Validate card model parsing and semantic helpers.
    """
    card = live_pipefy_api.cards.get(CARD_ID)

    assert card is not None
    assert card.id == CARD_ID
    assert hasattr(card, "title")
    assert isinstance(card.iterFields(), list)

    fields = card.iterFields()
    if fields:
        first_field = fields[0]
        assert card.hasField(first_field.id) is True
        assert card.requireField(first_field.id).id == first_field.id


@pytest.mark.integration
def test_card_list_by_pipe_live(live_pipefy_api: Any) -> None:
    """
    Validate listing cards from a pipe.
    """
    cards = live_pipefy_api.cards.list(PIPE_ID)

    assert isinstance(cards, list)
    if cards:
        assert hasattr(cards[0], "id")


@pytest.mark.integration
def test_card_list_by_phase_live(live_pipefy_api: Any) -> None:
    """
    Validate listing cards from a phase through the phases facade.
    """
    cards = live_pipefy_api.phases.listCards(PHASE_ID)

    assert isinstance(cards, list)
    if cards:
        assert hasattr(cards[0], "id")


@pytest.mark.integration
def test_card_create_safely_live_example(
    live_pipefy_api: Any, live_card_lifecycle_context: Any
) -> None:
    """
    Validate the shared destructive start-form-created card.
    """
    created_card = live_pipefy_api.cards.get(
        live_card_lifecycle_context.created_card_id
    )

    assert created_card.id == live_card_lifecycle_context.created_card_id
    assert (
        normalize_live_field_value(created_card.getFieldValue("copy_of_descri_o"))
        == DEFAULT_CREATE_DESCRIPTION_VALUE
    )
    assert (
        live_card_lifecycle_context.create_fields["copy_of_descri_o"]
        == DEFAULT_CREATE_DESCRIPTION_VALUE
    )
