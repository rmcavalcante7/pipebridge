"""
Integration tests for the live safe card move flow.
"""

from __future__ import annotations

from typing import Any

import pytest

from pipebridge.exceptions import RequiredFieldError, ValidationError
from pipebridge.service.card.flows.move.cardMoveConfig import CardMoveConfig


@pytest.mark.integration
def test_move_safely_blocks_invalid_transition(live_pipefy_api: Any) -> None:
    """
    Validate that live safe move blocks transitions not allowed by current phase.
    """
    card_id = "1330664077"
    expected_current_phase_id = "342616258"
    invalid_destination_phase_id = "342616257"

    with pytest.raises(ValidationError) as exc_info:
        live_pipefy_api.cards.moveSafely(
            card_id=card_id,
            destination_phase_id=invalid_destination_phase_id,
            expected_current_phase_id=expected_current_phase_id,
            config=CardMoveConfig(validate_required_fields=True),
        )

    assert exc_info.value.context.get("allowed_transitions")


@pytest.mark.integration
def test_move_safely_blocks_pending_required_fields(live_pipefy_api: Any) -> None:
    """
    Validate that live safe move blocks allowed transitions with pending required fields.
    """
    card_id = "1330664077"
    expected_current_phase_id = "342616258"
    destination_phase_id = "342616253"

    with pytest.raises(RequiredFieldError) as exc_info:
        live_pipefy_api.cards.moveSafely(
            card_id=card_id,
            destination_phase_id=destination_phase_id,
            expected_current_phase_id=expected_current_phase_id,
            config=CardMoveConfig(validate_required_fields=True),
        )

    assert exc_info.value.context.get("pending_required_fields")
