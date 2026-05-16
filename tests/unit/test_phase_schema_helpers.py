"""
Unit tests for phase-schema helper methods exposed by service and facade.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from pipebridge.client.httpClient import PipefyHttpClient
from pipebridge.facade.pipefyFacade import PhasesFacade
from pipebridge.models.phase import Phase
from pipebridge.models.phaseField import PhaseField
from pipebridge.service.phase.phaseService import PhaseService


def build_phase() -> Phase:
    """
    Build a small phase model for schema helper tests.

    :return: Phase = Modeled phase
    """
    return Phase(
        id="phase-1",
        name="Phase 1",
        fields=[
            PhaseField(id="name", label="Name", type="short_text", required=True),
            PhaseField(id="amount", label="Amount", type="number", required=False),
        ],
    )


@pytest.mark.unit
def test_phase_service_schema_helpers(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Validate phase-schema helpers on the service layer.
    """
    client = PipefyHttpClient(
        auth_key="token",
        base_url="https://app.pipefy.com/queries",
    )
    service = PhaseService(client)
    phase = build_phase()

    monkeypatch.setattr(service, "getPhaseModel", lambda phase_id: phase)

    field = service.getPhaseField("phase-1", "name")

    assert field is not None
    assert field.label == "Name"
    assert service.hasPhaseField("phase-1", "name") is True
    assert service.getPhaseField("phase-1", "missing") is None
    assert service.hasPhaseField("phase-1", "missing") is False
    assert service.requirePhaseField("phase-1", "amount").type == "number"


@pytest.mark.unit
def test_phases_facade_schema_helpers_delegate() -> None:
    """
    Validate public facade helpers for phase-schema lookup.
    """

    class _FakePhaseService:
        def __init__(self) -> None:
            self.calls: list[tuple[str, str, str]] = []
            self.field = PhaseField(
                id="name",
                label="Name",
                type="short_text",
                required=True,
            )

        def getPhaseField(self, phase_id: str, field_id: str) -> PhaseField | None:
            self.calls.append(("get", phase_id, field_id))
            return self.field if field_id == "name" else None

        def hasPhaseField(self, phase_id: str, field_id: str) -> bool:
            self.calls.append(("has", phase_id, field_id))
            return field_id == "name"

        def requirePhaseField(self, phase_id: str, field_id: str) -> PhaseField:
            self.calls.append(("require", phase_id, field_id))
            if field_id != "name":
                raise AssertionError("unexpected test input")
            return self.field

    service = _FakePhaseService()
    facade = PhasesFacade(service=service, card_service=SimpleNamespace())

    field = facade.getField("phase-1", "name")

    assert field is not None
    assert field.label == "Name"
    assert facade.hasField("phase-1", "name") is True
    assert facade.requireField("phase-1", "name").id == "name"
    assert service.calls == [
        ("get", "phase-1", "name"),
        ("has", "phase-1", "name"),
        ("require", "phase-1", "name"),
    ]
