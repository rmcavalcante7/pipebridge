"""
Unit tests for pipe field catalog behavior.
"""

from __future__ import annotations

import pytest

from pipebridge.exceptions import (
    InvalidFieldOptionError,
    RequiredFieldError,
    ValidationError,
)
from pipebridge.models.phaseField import PhaseField
from pipebridge.models.pipe import Pipe
from pipebridge.service.card.cardService import CardService
from pipebridge.service.pipe.pipeService import PipeService


class DummyClient:
    """
    Minimal fake client that captures the generated query.
    """

    def __init__(self, response: dict) -> None:
        self.response = response
        self.last_query: str | None = None
        self.last_timeout: int | None = None

    def sendRequest(
        self, query: str, variables: dict | None = None, timeout: int = 30
    ) -> dict:
        self.last_query = query
        self.last_timeout = timeout
        return self.response


@pytest.mark.unit
def test_pipe_field_catalog_includes_start_form_fields_and_internal_id() -> None:
    """
    Validate field catalog coverage for start form and phase fields.
    """
    client = DummyClient(
        {
            "data": {
                "pipe": {
                    "id": "pipe-1",
                    "name": "Pipe 1",
                    "cards_count": 10,
                    "organization": {"id": "org-1"},
                    "labels": [
                        {"id": "label-1", "name": "Important", "color": "green"}
                    ],
                    "users": [
                        {"id": "user-1", "name": "Rafael", "email": "r@test.dev"}
                    ],
                    "start_form_fields": [
                        {
                            "id": "oc",
                            "uuid": "uuid-oc",
                            "internal_id": "start_form.oc",
                            "label": "Order Code",
                            "type": "short_text",
                            "required": True,
                            "description": "Order code",
                            "options": [],
                        }
                    ],
                    "phases": [
                        {
                            "id": "phase-1",
                            "name": "Phase 1",
                            "fields": [
                                {
                                    "id": "amount",
                                    "uuid": "uuid-amount",
                                    "internal_id": "phase.amount",
                                    "label": "Amount",
                                    "type": "number",
                                    "required": False,
                                    "description": "Total amount",
                                    "options": [],
                                }
                            ],
                        }
                    ],
                }
            }
        }
    )

    service = PipeService(client)  # type: ignore[arg-type]

    pipe = service.getPipeFieldCatalog("pipe-1")

    assert client.last_query is not None
    assert "start_form_fields" in client.last_query
    assert "internal_id" in client.last_query
    assert client.last_timeout == 60

    assert pipe.requireStartFormField("oc").internal_id == "start_form.oc"
    assert (
        pipe.requirePhase("phase-1").requireField("amount").internal_id
        == "phase.amount"
    )
    assert pipe.requireUser("user-1").email == "r@test.dev"
    assert pipe.requireLabel("label-1").name == "Important"
    assert [field.id for field in pipe.iterAllFields()] == ["oc", "amount"]


@pytest.mark.unit
def test_create_card_safely_validates_required_start_form_fields() -> None:
    """
    Validate required-field enforcement against start form schema.
    """
    service = CardService(DummyClient({"data": {"createCard": {"card": {"id": "1"}}}}))  # type: ignore[arg-type]
    service._pipe_schema_cache.set(
        "pipe-1",
        Pipe(
            id="pipe-1",
            start_form_fields=[
                PhaseField(id="oc", type="short_text", required=True),
            ],
        ),
    )

    with pytest.raises(RequiredFieldError):
        service.createCardSafely(pipe_id="pipe-1", title="Test", fields={})


@pytest.mark.unit
def test_create_card_safely_rejects_unknown_start_form_field() -> None:
    """
    Validate field existence enforcement against start form schema.
    """
    service = CardService(DummyClient({"data": {"createCard": {"card": {"id": "1"}}}}))  # type: ignore[arg-type]
    service._pipe_schema_cache.set(
        "pipe-1",
        Pipe(
            id="pipe-1",
            start_form_fields=[
                PhaseField(id="oc", type="short_text", required=False),
            ],
        ),
    )

    with pytest.raises(ValidationError):
        service.createCardSafely(
            pipe_id="pipe-1",
            title="Test",
            fields={"unknown": "x"},
        )


@pytest.mark.unit
def test_create_card_safely_delegates_to_create_card_when_valid() -> None:
    """
    Validate successful safe creation through the existing create path.
    """
    client = DummyClient(
        {"data": {"createCard": {"card": {"id": "1", "title": "Test"}}}}
    )
    service = CardService(client)  # type: ignore[arg-type]
    service._pipe_schema_cache.set(
        "pipe-1",
        Pipe(
            id="pipe-1",
            start_form_fields=[
                PhaseField(
                    id="oc",
                    type="short_text",
                    required=True,
                    options=["123"],
                ),
            ],
        ),
    )

    result = service.createCardSafely(
        pipe_id="pipe-1",
        title="Test",
        fields={"oc": "123"},
    )

    assert result == {"data": {"createCard": {"card": {"id": "1", "title": "Test"}}}}
    assert client.last_query is not None
    assert "createCard" in client.last_query


@pytest.mark.unit
def test_create_card_safely_raises_specific_error_for_invalid_option() -> None:
    """
    Validate option enforcement uses the documented field-option exception.
    """
    service = CardService(DummyClient({"data": {"createCard": {"card": {"id": "1"}}}}))  # type: ignore[arg-type]
    service._pipe_schema_cache.set(
        "pipe-1",
        Pipe(
            id="pipe-1",
            start_form_fields=[
                PhaseField(
                    id="oc",
                    type="select",
                    required=False,
                    options=["123"],
                ),
            ],
        ),
    )

    with pytest.raises(InvalidFieldOptionError):
        service.createCardSafely(
            pipe_id="pipe-1",
            title="Test",
            fields={"oc": "999"},
        )
