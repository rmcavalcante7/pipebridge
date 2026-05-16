"""
Unit tests for connector read modeling in card fields.
"""

from __future__ import annotations

import pytest

from pipebridge.models.card import Card
from pipebridge.models.field import Field
from pipebridge.models.phase import Phase
from pipebridge.service.card.cardService import CardService


class DummyClient:
    """
    Minimal fake client that captures the generated card query.
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
def test_field_from_dict_preserves_connector_read_metadata() -> None:
    """
    Preserve array, native, and connected item data for connector fields.
    """
    field = Field.fromDict(
        {
            "field": {"id": "nome_projetos", "label": "Projetos", "type": "connector"},
            "value": '["IA Time"]',
            "report_value": "IA Time",
            "array_value": ["1316654201"],
            "native_value": "IA Time",
            "connectedRepoItems": [
                {
                    "__typename": "PublicTableRecord",
                    "id": "1316654201",
                    "title": "IA Time",
                    "path": "/apollo_databases/307010661/records/1316654201",
                    "url": "https://app.pipefy.com/apollo_databases/307010661/records/1316654201",
                    "uuid": "98cff791-d85c-4c67-a17b-973bcdfff377",
                }
            ],
        }
    )

    assert field.array_value == ["1316654201"]
    assert field.native_value == "IA Time"
    assert len(field.connected_items) == 1
    assert field.connected_items[0].item_type == "PublicTableRecord"
    assert field.connected_items[0].id == "1316654201"


@pytest.mark.unit
def test_card_connector_helpers_return_structured_values() -> None:
    """
    Expose connector ids and connected items through semantic card helpers.
    """
    card = Card(
        id="card-1",
        title="Example",
        pipe_id="pipe-1",
        current_phase=Phase(id="phase-1", name="Backlog", fields=[]),
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
            ),
            Field(
                id="automa_o",
                label="Pesquise o nome Automacao",
                type="connector",
                value='["pipe item"]',
                report_value="pipe item",
                array_value=["133"],
                native_value="pipe item",
                connected_items=[],
            ),
        ],
        assignees=[],
        labels=[],
    )

    assert card.getConnectorIds("nome_projetos") == ["1316654201"]
    assert card.hasConnectedItems("nome_projetos") is False

    connector_value = card.getConnectorValue("automa_o")
    assert connector_value is not None
    assert connector_value.field_id == "automa_o"
    assert connector_value.item_ids == ["133"]
    assert connector_value.native_value == "pipe item"


@pytest.mark.unit
def test_card_service_default_query_requests_connector_read_metadata() -> None:
    """
    Include connector read metadata in the default structured card query.
    """
    client = DummyClient(
        {
            "data": {
                "card": {
                    "id": "card-1",
                    "title": "Example",
                    "pipe": {"id": "pipe-1"},
                    "current_phase": {"id": "phase-1", "name": "Backlog"},
                    "phases_history": [],
                    "fields": [],
                    "assignees": [],
                    "labels": [],
                    "attachments": [],
                }
            }
        }
    )

    service = CardService(client)  # type: ignore[arg-type]
    card = service.getCardModel("card-1")

    assert card.id == "card-1"
    assert client.last_query is not None
    assert "array_value" in client.last_query
    assert "native_value" in client.last_query
    assert "connectedRepoItems" in client.last_query
    assert "... on PublicRepoItemInterface" in client.last_query
