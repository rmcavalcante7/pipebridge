from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from pipebridge.models.card import Card
from pipebridge.models.phase import Phase
from pipebridge.models.pipe import Pipe
from pipebridge.service.card.flows.update.dispatcher.resolvedFieldUpdate import (
    ResolvedFieldUpdate,
)
from pipebridge.service.card.flows.update.steps.resolveCardFieldUpdatesStep import (
    ResolveCardFieldUpdatesStep,
)


class _FakeDispatcher:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def dispatch(
        self,
        field_id: str,
        field_type: str,
        input_value: Any,
        current_field: Any = None,
        phase_field: Any = None,
    ) -> ResolvedFieldUpdate:
        self.calls.append(
            {
                "field_id": field_id,
                "field_type": field_type,
                "input_value": input_value,
                "current_field": current_field,
                "phase_field": phase_field,
            }
        )
        return ResolvedFieldUpdate(
            field_id=field_id,
            field_type=field_type,
            input_value=input_value,
            current_field=current_field,
            phase_field=phase_field,
            new_value=input_value,
        )


class _FakePipeSchemaCache:
    def __init__(self, pipe: Pipe) -> None:
        self.pipe = pipe
        self.calls: list[str] = []

    def getOrLoad(self, pipe_id: str, loader: Any) -> Pipe:
        self.calls.append(pipe_id)
        return self.pipe


class _FakePipeService:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def getPipeFieldCatalog(self, pipe_id: str) -> Pipe:
        self.calls.append(pipe_id)
        raise AssertionError(
            "Loader should not be called when cache already has the pipe."
        )


def test_resolve_step_falls_back_to_pipe_schema_for_start_form_field_type() -> None:
    dispatcher = _FakeDispatcher()
    step = ResolveCardFieldUpdatesStep(dispatcher=dispatcher)

    card = Card.fromDict(
        {
            "id": "card-1",
            "pipe": {"id": "pipe-1"},
            "current_phase": {"id": "phase-1", "name": "Backlog", "fields": []},
            "fields": [],
        }
    )
    phase = Phase.fromDict({"id": "phase-1", "name": "Backlog", "fields": []})
    pipe = Pipe.fromDict(
        {
            "id": "pipe-1",
            "start_form_fields": [
                {
                    "id": "oc",
                    "label": "OC",
                    "type": "short_text",
                    "required": False,
                }
            ],
            "phases": [],
        }
    )

    context = SimpleNamespace(
        card=card,
        phase=phase,
        pipe_id="pipe-1",
        pipe_schema_cache=_FakePipeSchemaCache(pipe=pipe),
        pipe_service=_FakePipeService(),
        request=SimpleNamespace(fields={"oc": "Doc-D invalido."}),
        resolved_operations=[],
    )

    step.execute(context)

    assert len(context.resolved_operations) == 1
    assert dispatcher.calls[0]["field_id"] == "oc"
    assert dispatcher.calls[0]["field_type"] == "short_text"
    assert dispatcher.calls[0]["phase_field"] is not None
    assert dispatcher.calls[0]["phase_field"].id == "oc"
    assert context.pipe_schema_cache.calls == ["pipe-1"]
