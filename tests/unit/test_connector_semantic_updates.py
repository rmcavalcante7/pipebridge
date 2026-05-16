"""
Unit tests for semantic connector card operations.
"""

from __future__ import annotations

import pytest

from pipebridge.models.card import Card
from pipebridge.models.field import Field
from pipebridge.models.phaseField import PhaseField
from pipebridge.models.connectedRepoRef import ConnectedRepoRef
from pipebridge.service.card.flows.update.cardUpdateConfig import CardUpdateConfig
from pipebridge.service.card.flows.update.dispatcher.handlers.connectorUpdateHandler import (
    ConnectorUpdateHandler,
)
from pipebridge.service.card.flows.update.rules.validateCardFieldSchemaRule import (
    ValidateCardFieldSchemaRule,
)
from pipebridge.service.connector.connectorService import ConnectorService


class DummyClient:
    """
    Fake client that returns queued responses and captures queries.
    """

    def __init__(self, responses: list[dict]) -> None:
        self.responses = list(responses)
        self.queries: list[str] = []

    def sendRequest(
        self, query: str, variables: dict | None = None, timeout: int = 30
    ) -> dict:
        self.queries.append(query)
        if not self.responses:
            raise AssertionError("No queued response available for sendRequest")
        return self.responses.pop(0)


class FakeCardService:
    """
    Minimal fake card service used by ConnectorService semantic helpers.
    """

    def __init__(self, card: Card, field: PhaseField) -> None:
        self.card = card
        self.field = field
        self.last_update_call: dict | None = None

    def getCardPipeField(self, card_id: str, field_id: str) -> PhaseField | None:
        assert card_id == self.card.id
        assert field_id == self.field.id
        return self.field

    def getCardModel(self, card_id: str) -> Card:
        assert card_id == self.card.id
        return self.card

    def updateFields(
        self,
        card_id: str,
        fields: dict,
        expected_phase_id: str | None = None,
        config: CardUpdateConfig | None = None,
        extra_rules: list | None = None,
        extra_handlers: dict | None = None,
    ) -> dict:
        self.last_update_call = {
            "card_id": card_id,
            "fields": fields,
            "expected_phase_id": expected_phase_id,
            "config": config,
            "extra_rules": extra_rules,
            "extra_handlers": extra_handlers,
        }
        return {"nome_projetos": {"success": True}}


def build_connector_field(can_connect_multiples: bool = True) -> PhaseField:
    return PhaseField(
        id="nome_projetos",
        label="Projetos",
        type="connector",
        connected_repo=ConnectedRepoRef(
            repo_type="Table",
            id="6CzIX6F_",
            name="TechMaster Projetos",
        ),
        can_connect_existing=True,
        can_connect_multiples=can_connect_multiples,
    )


def build_table_records_response(ids_and_titles: list[tuple[str, str]]) -> dict:
    return {
        "data": {
            "table_records": {
                "edges": [
                    {"node": {"id": item_id, "title": title}}
                    for item_id, title in ids_and_titles
                ]
            }
        }
    }


@pytest.mark.unit
def test_connector_service_get_card_value_returns_empty_when_connector_is_not_materialized() -> (
    None
):
    """
    Return an empty structured connector value when the connector exists in schema
    but is absent from card.fields.
    """
    card = Card(
        id="card-1",
        title="Example",
        pipe_id="pipe-1",
        current_phase=None,
        phases_history=[],
        fields=[],
        assignees=[],
        labels=[],
    )
    fake_card_service = FakeCardService(card=card, field=build_connector_field())
    service = ConnectorService(
        DummyClient([]),  # type: ignore[arg-type]
        card_service=fake_card_service,  # type: ignore[arg-type]
    )

    value = service.getCardValue(card_id="card-1", field_id="nome_projetos")

    assert value.field_id == "nome_projetos"
    assert value.item_ids == []
    assert value.items == []
    assert value.raw_value is None


@pytest.mark.unit
def test_connector_service_set_card_value_updates_with_relaxed_phase_existence_validation() -> (
    None
):
    """
    Replace connector ids using the public semantic helper.
    """
    card = Card(
        id="card-1",
        title="Example",
        pipe_id="pipe-1",
        current_phase=None,
        phases_history=[],
        fields=[],
        assignees=[],
        labels=[],
    )
    fake_card_service = FakeCardService(card=card, field=build_connector_field())
    service = ConnectorService(
        DummyClient([build_table_records_response([("1316654201", "IA Time")])]),  # type: ignore[arg-type]
        card_service=fake_card_service,  # type: ignore[arg-type]
    )

    result = service.setCardValue(
        card_id="card-1",
        field_id="nome_projetos",
        item_ids=["1316654201"],
    )

    assert result == {"nome_projetos": {"success": True}}
    assert fake_card_service.last_update_call is not None
    assert fake_card_service.last_update_call["fields"] == {
        "nome_projetos": ["1316654201"]
    }
    assert isinstance(fake_card_service.last_update_call["config"], CardUpdateConfig)
    assert (
        fake_card_service.last_update_call["config"].validate_field_existence is False
    )


@pytest.mark.unit
def test_connector_service_add_card_value_merges_without_duplicates() -> None:
    """
    Add connector ids with read-modify-write semantics.
    """
    card = Card(
        id="card-1",
        title="Example",
        pipe_id="pipe-1",
        current_phase=None,
        phases_history=[],
        fields=[
            Field(
                id="nome_projetos",
                label="Projetos",
                type="connector",
                value='["IA Time"]',
                report_value="IA Time",
                array_value=["1316654201"],
                native_value="IA Time",
                connected_items=[],
            )
        ],
        assignees=[],
        labels=[],
    )
    fake_card_service = FakeCardService(card=card, field=build_connector_field())
    service = ConnectorService(
        DummyClient(
            [
                build_table_records_response(
                    [("1316654201", "IA Time"), ("1316654202", "Financeiro")]
                )
            ]
        ),  # type: ignore[arg-type]
        card_service=fake_card_service,  # type: ignore[arg-type]
    )

    service.addCardValue(
        card_id="card-1",
        field_id="nome_projetos",
        item_ids=["1316654201", "1316654202"],
    )

    assert fake_card_service.last_update_call is not None
    assert fake_card_service.last_update_call["fields"] == {
        "nome_projetos": ["1316654201", "1316654202"]
    }


@pytest.mark.unit
def test_connector_service_remove_card_value_uses_read_modify_write() -> None:
    """
    Remove connector ids with read-modify-write semantics.
    """
    card = Card(
        id="card-1",
        title="Example",
        pipe_id="pipe-1",
        current_phase=None,
        phases_history=[],
        fields=[
            Field(
                id="nome_projetos",
                label="Projetos",
                type="connector",
                value='["IA Time","Financeiro"]',
                report_value="IA Time, Financeiro",
                array_value=["1316654201", "1316654202"],
                native_value="IA Time, Financeiro",
                connected_items=[],
            )
        ],
        assignees=[],
        labels=[],
    )
    fake_card_service = FakeCardService(card=card, field=build_connector_field())
    service = ConnectorService(
        DummyClient(
            [build_table_records_response([("1316654202", "Financeiro")])]
        ),  # type: ignore[arg-type]
        card_service=fake_card_service,  # type: ignore[arg-type]
    )

    service.removeCardValue(
        card_id="card-1",
        field_id="nome_projetos",
        item_ids=["1316654202"],
    )

    assert fake_card_service.last_update_call is not None
    assert fake_card_service.last_update_call["fields"] == {
        "nome_projetos": ["1316654201"]
    }


@pytest.mark.unit
def test_connector_update_handler_accepts_list_of_string_ids() -> None:
    """
    Allow connector updates to operate with list[str] payloads.
    """
    handler = ConnectorUpdateHandler()

    resolved = handler.resolve(
        field_id="nome_projetos",
        field_type="connector",
        input_value=["1316654201", "1316654202"],
    )

    assert resolved.new_value == ["1316654201", "1316654202"]


@pytest.mark.unit
def test_connector_type_validation_accepts_list_of_strings() -> None:
    """
    Allow connector type validation to accept list[str] for semantic helpers.
    """
    ValidateCardFieldSchemaRule._validateTypeCompatibility(
        field_id="nome_projetos",
        field_type="connector",
        value=["1316654201", "1316654202"],
        class_name="Test",
        method_name="test",
    )
