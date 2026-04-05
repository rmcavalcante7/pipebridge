"""
Unit tests for semantic helper methods on core models.
"""

from __future__ import annotations

import pytest

from pipebridge.models.card import Card
from pipebridge.models.field import Field
from pipebridge.models.phase import Phase
from pipebridge.models.phaseField import PhaseField
from pipebridge.models.pipe import Pipe
from pipebridge.models.user import User
from pipebridge.models.label import Label


def build_card() -> Card:
    """
    Build a small card model for helper tests.

    :return: Card = Modeled card
    """
    phase = Phase(
        id="phase-1",
        name="Phase 1",
        fields=[
            PhaseField(id="name", label="Name", type="short_text", required=True),
            PhaseField(id="amount", label="Amount", type="number", required=False),
        ],
    )
    return Card(
        id="card-1",
        title="Example",
        pipe_id="pipe-1",
        current_phase=phase,
        phases_history=[],
        fields=[
            Field(
                id="name",
                label="Name",
                type="short_text",
                value="Rafael",
                report_value="Rafael",
            ),
            Field(
                id="amount",
                label="Amount",
                type="number",
                value="10",
                report_value="10",
            ),
        ],
        assignees=[User(id="user-1", name="Rafael")],
        labels=[Label(id="label-1", name="Important")],
    )


@pytest.mark.unit
def test_card_semantic_helpers() -> None:
    """
    Validate semantic helper methods on the card model.
    """
    card = build_card()

    assert card.hasField("name") is True
    assert card.getFieldValue("name") == "Rafael"
    assert card.requireFieldType("amount") == "number"
    assert card.getFieldLabel("name") == "Name"
    assert card.isFieldFilled("amount") is True
    assert [field.id for field in card.getFieldsByType("short_text")] == ["name"]


@pytest.mark.unit
def test_phase_semantic_helpers() -> None:
    """
    Validate semantic helper methods on the phase model.
    """
    phase = build_card().current_phase
    assert phase is not None

    assert phase.hasField("name") is True
    assert phase.getFieldType("name") == "short_text"
    assert phase.getFieldOptions("name") == []
    assert phase.isFieldRequired("name") is True
    assert [field.id for field in phase.getFieldsByType("number")] == ["amount"]


@pytest.mark.unit
def test_pipe_semantic_helpers() -> None:
    """
    Validate semantic helper methods on the pipe model.
    """
    card = build_card()
    phase = card.current_phase
    assert phase is not None

    pipe = Pipe(
        id="pipe-1",
        name="Pipe 1",
        phases=[phase],
        labels=card.labels,
        users=card.assignees,
    )

    assert pipe.hasPhase("phase-1") is True
    assert pipe.requirePhase("phase-1").name == "Phase 1"
    assert pipe.requireLabel("label-1").name == "Important"
    assert pipe.requireUser("user-1").name == "Rafael"
    assert len(list(pipe.iterAllFields())) == 2
    assert [field.id for field in pipe.getFieldsByType("short_text")] == ["name"]
