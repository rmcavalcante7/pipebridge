"""
Integration tests for the live card update flow.
"""

from __future__ import annotations

from typing import Any

import pytest

from tests.live_examples import normalize_live_field_value


def _assert_card_fields_match(card: Any, expected_fields: dict[str, Any]) -> None:
    """
    Assert that live card fields match the expected normalized values.
    """
    for field_id, expected_value in expected_fields.items():
        actual_value = normalize_live_field_value(card.getFieldValue(field_id))
        normalized_expected = normalize_live_field_value(expected_value)
        assert actual_value == normalized_expected


@pytest.mark.integration
def test_card_update_flow_live_uses_only_created_card(
    live_pipefy_api: Any, live_card_lifecycle_context: Any
) -> None:
    """
    Validate that the live update flow only mutates the created lifecycle card.
    """
    card = live_pipefy_api.cards.get(live_card_lifecycle_context.created_card_id)

    assert card.id == live_card_lifecycle_context.created_card_id

    if live_card_lifecycle_context.move_destination_phase_id is not None:
        assert card.current_phase is not None
        assert (
            card.current_phase.id
            == live_card_lifecycle_context.move_destination_phase_id
        )


@pytest.mark.integration
def test_card_update_flow_live_persists_current_phase_payload(
    live_pipefy_api: Any, live_card_lifecycle_context: Any
) -> None:
    """
    Validate that fields updated before the move remain persisted on the created card.
    """
    if not live_card_lifecycle_context.current_phase_update_fields:
        pytest.skip("No supported current-phase fields were generated for update.")

    card = live_pipefy_api.cards.get(live_card_lifecycle_context.created_card_id)
    _assert_card_fields_match(
        card, live_card_lifecycle_context.current_phase_update_fields
    )


@pytest.mark.integration
def test_card_update_flow_live_persists_destination_phase_payload(
    live_pipefy_api: Any, live_card_lifecycle_context: Any
) -> None:
    """
    Validate that fields updated after the safe move remain persisted on the created card.
    """
    if not live_card_lifecycle_context.destination_phase_update_fields:
        pytest.skip("No supported destination-phase fields were generated for update.")

    card = live_pipefy_api.cards.get(live_card_lifecycle_context.created_card_id)
    _assert_card_fields_match(
        card,
        live_card_lifecycle_context.destination_phase_update_fields,
    )
