"""
Integration tests for the live safe card move flow.
"""

from __future__ import annotations

from typing import Any

import pytest


@pytest.mark.integration
def test_move_safely_blocks_invalid_transition(
    live_card_lifecycle_context: Any,
) -> None:
    """
    Validate that live safe move blocks transitions not allowed from the created phase.
    """
    if live_card_lifecycle_context.invalid_destination_phase_id is None:
        pytest.skip("No invalid transition candidate was found for the created phase.")

    assert live_card_lifecycle_context.invalid_transition_context is not None
    assert live_card_lifecycle_context.invalid_transition_context.get(
        "allowed_transitions"
    )
    assert (
        live_card_lifecycle_context.invalid_transition_context.get(
            "destination_phase_id"
        )
        == live_card_lifecycle_context.invalid_destination_phase_id
    )


@pytest.mark.integration
def test_move_safely_blocks_pending_required_fields(
    live_card_lifecycle_context: Any,
) -> None:
    """
    Validate that live safe move blocks allowed transitions with pending required fields.
    """
    if live_card_lifecycle_context.pending_required_destination_phase_id is None:
        pytest.skip("No allowed destination with pending required fields was found.")

    assert live_card_lifecycle_context.pending_required_context is not None
    assert live_card_lifecycle_context.pending_required_context.get(
        "pending_required_fields"
    )
    assert (
        live_card_lifecycle_context.pending_required_context.get("destination_phase_id")
        == live_card_lifecycle_context.pending_required_destination_phase_id
    )


@pytest.mark.integration
def test_move_safely_live_from_created_start_form_card(
    live_pipefy_api: Any, live_card_lifecycle_context: Any
) -> None:
    """
    Validate the shared created live card reaches the recorded destination phase.
    """
    if live_card_lifecycle_context.move_destination_phase_id is None:
        pytest.skip("No movable destination without pending required fields was found.")

    moved_card = live_pipefy_api.cards.get(live_card_lifecycle_context.created_card_id)

    assert moved_card.current_phase is not None
    assert (
        moved_card.current_phase.id
        == live_card_lifecycle_context.move_destination_phase_id
    )
