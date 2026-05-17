"""
Unit tests for safe connector validation during card creation.
"""

from __future__ import annotations

import pytest

from pipebridge.exceptions import ValidationError
from pipebridge.models.connectedRepoRef import ConnectedRepoRef
from pipebridge.models.phaseField import PhaseField
from pipebridge.models.pipe import Pipe
from pipebridge.service.card.cardService import CardService


class QueuedClient:
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


def build_table_connector_field(
    required: bool = True,
    can_connect_multiples: bool = False,
    can_connect_existing: bool = True,
) -> PhaseField:
    return PhaseField(
        id="nome_projetos",
        label="Projetos",
        type="connector",
        required=required,
        uuid="uuid-proj",
        connected_repo=ConnectedRepoRef(
            repo_type="Table",
            id="6CzIX6F_",
            name="TechMaster Projetos",
        ),
        can_connect_existing=can_connect_existing,
        can_connect_multiples=can_connect_multiples,
    )


def build_pipe_connector_field(
    required: bool = False,
    can_connect_multiples: bool = True,
    can_connect_existing: bool = True,
) -> PhaseField:
    return PhaseField(
        id="automa_o",
        label="Pesquise o nome Automacao",
        type="connector",
        required=required,
        uuid="uuid-auto",
        connected_repo=ConnectedRepoRef(
            repo_type="Pipe",
            id="307073107",
            name="Base historica Fila de Automacao",
        ),
        can_connect_existing=can_connect_existing,
        can_connect_multiples=can_connect_multiples,
    )


@pytest.mark.unit
def test_create_card_safely_validates_table_connector_ids_before_create() -> None:
    """
    Validate start-form table connector ids before delegating to createCard.
    """
    client = QueuedClient(
        [
            {
                "data": {
                    "table_records": {
                        "edges": [
                            {"node": {"id": "1316654201", "title": "IA Time"}},
                            {"node": {"id": "1316654202", "title": "Financeiro"}},
                        ]
                    }
                }
            },
            {"data": {"createCard": {"card": {"id": "1", "title": "Test"}}}},
        ]
    )
    service = CardService(client)  # type: ignore[arg-type]
    service._pipe_schema_cache.set(
        "pipe-1",
        Pipe(id="pipe-1", start_form_fields=[build_table_connector_field()]),
    )

    result = service.createCardSafely(
        pipe_id="pipe-1",
        title="Test",
        fields={"nome_projetos": ["1316654201"]},
    )

    assert result == {"data": {"createCard": {"card": {"id": "1", "title": "Test"}}}}
    assert len(client.queries) == 2
    assert "table_records" in client.queries[0]
    assert "createCard" in client.queries[1]


@pytest.mark.unit
def test_create_card_safely_validates_pipe_connector_ids_before_create() -> None:
    """
    Validate pipe-backed connector ids before delegating to createCard.
    """
    client = QueuedClient(
        [
            {
                "data": {
                    "cards": {
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                        "edges": [
                            {
                                "node": {
                                    "uuid": "gid://pipefy/Card/uuid-133",
                                    "internalId": "133",
                                    "title": "Bot de Cobranca",
                                    "currentPhase": {
                                        "id": "phase-1",
                                        "name": "Backlog",
                                    },
                                }
                            }
                        ],
                    }
                }
            },
            {"data": {"createCard": {"card": {"id": "2", "title": "Connector"}}}},
        ]
    )
    service = CardService(client)  # type: ignore[arg-type]
    service._pipe_schema_cache.set(
        "pipe-1",
        Pipe(id="pipe-1", start_form_fields=[build_pipe_connector_field()]),
    )

    result = service.createCardSafely(
        pipe_id="pipe-1",
        title="Connector",
        fields={"automa_o": ["133"]},
    )

    assert result == {
        "data": {"createCard": {"card": {"id": "2", "title": "Connector"}}}
    }
    assert len(client.queries) == 2
    assert "cards(" in client.queries[0]
    assert "createCard" in client.queries[1]


@pytest.mark.unit
def test_create_card_safely_rejects_non_list_connector_payload() -> None:
    """
    Require connector creation payloads to be a list of connected ids.
    """
    service = CardService(QueuedClient([]))  # type: ignore[arg-type]
    service._pipe_schema_cache.set(
        "pipe-1",
        Pipe(id="pipe-1", start_form_fields=[build_table_connector_field()]),
    )

    with pytest.raises(ValidationError, match="expects a list"):
        service.createCardSafely(
            pipe_id="pipe-1",
            title="Test",
            fields={"nome_projetos": "1316654201"},
        )


@pytest.mark.unit
def test_create_card_safely_rejects_multiple_ids_when_connector_is_single() -> None:
    """
    Reject multi-id payloads when the connector does not allow multiples.
    """
    service = CardService(QueuedClient([]))  # type: ignore[arg-type]
    service._pipe_schema_cache.set(
        "pipe-1",
        Pipe(
            id="pipe-1",
            start_form_fields=[
                build_table_connector_field(can_connect_multiples=False)
            ],
        ),
    )

    with pytest.raises(ValidationError, match="does not allow multiple"):
        service.createCardSafely(
            pipe_id="pipe-1",
            title="Test",
            fields={"nome_projetos": ["1316654201", "1316654202"]},
        )


@pytest.mark.unit
def test_create_card_safely_rejects_connector_id_not_found_in_connected_repo() -> None:
    """
    Reject ids that do not belong to the connected repo backing the connector.
    """
    client = QueuedClient(
        [
            {
                "data": {
                    "table_records": {
                        "edges": [
                            {"node": {"id": "1316654201", "title": "IA Time"}},
                        ]
                    }
                }
            }
        ]
    )
    service = CardService(client)  # type: ignore[arg-type]
    service._pipe_schema_cache.set(
        "pipe-1",
        Pipe(id="pipe-1", start_form_fields=[build_table_connector_field()]),
    )

    with pytest.raises(ValidationError, match="not found in connected repo"):
        service.createCardSafely(
            pipe_id="pipe-1",
            title="Test",
            fields={"nome_projetos": ["999999"]},
        )


@pytest.mark.unit
def test_create_card_safely_rejects_existing_id_when_connector_disallows_existing() -> (
    None
):
    """
    Reject existing-item payloads when the connector forbids connecting existing items.
    """
    service = CardService(QueuedClient([]))  # type: ignore[arg-type]
    service._pipe_schema_cache.set(
        "pipe-1",
        Pipe(
            id="pipe-1",
            start_form_fields=[
                build_table_connector_field(can_connect_existing=False),
            ],
        ),
    )

    with pytest.raises(ValidationError, match="does not allow connecting existing"):
        service.createCardSafely(
            pipe_id="pipe-1",
            title="Test",
            fields={"nome_projetos": ["1316654201"]},
        )
