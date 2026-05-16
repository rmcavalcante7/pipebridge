"""
Unit tests for connector discovery service and public facade.
"""

from __future__ import annotations

import pytest

from pipebridge.exceptions import ValidationError
from pipebridge.facade.pipefyFacade import ConnectorsFacade
from pipebridge.models.connectorFieldSpec import ConnectorFieldSpec
from pipebridge.models.connectorOption import ConnectorOption
from pipebridge.service.connector.connectorService import ConnectorService


class DummyClient:
    """
    Fake client that returns queued responses and captures executed queries.
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


def build_pipe_schema_response() -> dict:
    return {
        "data": {
            "pipe": {
                "id": "pipe-1",
                "name": "Automation Factory",
                "cards_count": 1,
                "organization": {"id": "org-1"},
                "labels": [],
                "users": [],
                "start_form_fields": [
                    {
                        "id": "nome_projetos",
                        "label": "Projetos",
                        "type": "connector",
                        "required": True,
                        "description": "",
                        "options": [],
                        "uuid": "uuid-proj",
                        "internal_id": "start_form.nome_projetos",
                        "help_text": "Select a project",
                        "can_connect_existing": True,
                        "can_connect_multiples": False,
                        "can_create_new_connected": False,
                        "connected_repo": {
                            "__typename": "PublicTable",
                            "id": "6CzIX6F_",
                            "name": "TechMaster Projetos",
                        },
                    }
                ],
                "phases": [
                    {
                        "id": "phase-1",
                        "name": "Backlog",
                        "fields": [
                            {
                                "id": "automa_o",
                                "label": "Pesquise o nome Automacao",
                                "type": "connector",
                                "required": False,
                                "description": "",
                                "options": [],
                                "uuid": "uuid-auto",
                                "internal_id": "phase.automa_o",
                                "help_text": "Select an automation",
                                "can_connect_existing": True,
                                "can_connect_multiples": True,
                                "can_create_new_connected": False,
                                "connected_repo": {
                                    "__typename": "PublicPipe",
                                    "id": "307073107",
                                    "name": "Base historica Fila de Automacao",
                                },
                            }
                        ],
                    }
                ],
            }
        }
    }


@pytest.mark.unit
def test_connector_service_lists_fields_with_origin_metadata() -> None:
    """
    Expose connector fields with explicit start-form/phase origin metadata.
    """
    client = DummyClient([build_pipe_schema_response()])
    service = ConnectorService(client)  # type: ignore[arg-type]

    fields = service.listFields("pipe-1")

    assert [field.field_id for field in fields] == ["nome_projetos", "automa_o"]
    assert fields[0].origin_type == "start_form"
    assert fields[0].phase_id is None
    assert fields[1].origin_type == "phase"
    assert fields[1].phase_id == "phase-1"
    assert fields[1].phase_name == "Backlog"
    assert fields[1].connected_repo is not None
    assert fields[1].connected_repo.repo_type == "Pipe"
    assert "connectedRepo" in client.queries[0]


@pytest.mark.unit
def test_connector_service_lists_table_options_and_filters_by_search() -> None:
    """
    List table-backed connector options using dynamic repo queries.
    """
    client = DummyClient(
        [
            build_pipe_schema_response(),
            {
                "data": {
                    "table_records": {
                        "edges": [
                            {
                                "node": {
                                    "id": "1316654201",
                                    "title": "IA Time",
                                    "path": "/apollo_databases/307010661/records/1316654201",
                                    "url": "https://app.pipefy.com/apollo_databases/307010661/records/1316654201",
                                    "uuid": "uuid-1",
                                    "record_fields": [
                                        {
                                            "indexName": "field_1_assignee_select",
                                            "name": "Lider Responsável",
                                            "value": '["RAFAEL MOTA CAVALCANTE"]',
                                        },
                                        {
                                            "indexName": "field_5_string",
                                            "name": "E-mail Líder Squad",
                                            "value": "jhonata.v.andrade@accenture.com",
                                        },
                                    ],
                                }
                            },
                            {
                                "node": {
                                    "id": "1316654202",
                                    "title": "Financeiro",
                                    "path": "/apollo_databases/307010661/records/1316654202",
                                    "url": "https://app.pipefy.com/apollo_databases/307010661/records/1316654202",
                                    "uuid": "uuid-2",
                                }
                            },
                        ]
                    }
                }
            },
        ]
    )
    service = ConnectorService(client)  # type: ignore[arg-type]

    options = service.listOptions(
        pipe_id="pipe-1",
        field_id="nome_projetos",
        search="ia",
        limit=10,
    )

    assert [option.id for option in options] == ["1316654201"]
    assert options[0].repo_type == "Table"
    assert options[0].repo_name == "TechMaster Projetos"
    assert (
        options[0].getRecordField("Lider Responsável") == '["RAFAEL MOTA CAVALCANTE"]'
    )
    assert options[0].hasRecordField("E-mail Líder Squad") is True
    assert options[0].record_fields[0]["index_name"] == "field_1_assignee_select"
    assert "table_records" in client.queries[1]
    assert "record_fields" in client.queries[1]


@pytest.mark.unit
def test_connector_service_lists_pipe_options_with_current_phase() -> None:
    """
    List pipe-backed connector options and preserve current phase details.
    """
    client = DummyClient(
        [
            build_pipe_schema_response(),
            {
                "data": {
                    "allCards": {
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                        "edges": [
                            {
                                "node": {
                                    "id": "card-1",
                                    "title": "Bot de Cobrança",
                                    "current_phase": {
                                        "id": "phase-dev",
                                        "name": "Em Desenvolvimento",
                                    },
                                }
                            }
                        ],
                    }
                }
            },
        ]
    )
    service = ConnectorService(client)  # type: ignore[arg-type]

    options = service.listOptions(
        pipe_id="pipe-1",
        field_id="automa_o",
        phase_id="phase-1",
        limit=10,
    )

    assert len(options) == 1
    assert options[0].repo_type == "Pipe"
    assert options[0].current_phase_id == "phase-dev"
    assert options[0].current_phase_name == "Em Desenvolvimento"
    assert "allCards(" in client.queries[1]
    assert "current_phase" in client.queries[1]


@pytest.mark.unit
def test_connector_service_resolves_unique_exact_option_title() -> None:
    """
    Resolve a unique connector option by exact title.
    """
    client = DummyClient(
        [
            build_pipe_schema_response(),
            {
                "data": {
                    "table_records": {
                        "edges": [
                            {"node": {"id": "1", "title": "Projeto A"}},
                            {"node": {"id": "2", "title": "Projeto B"}},
                        ]
                    }
                }
            },
        ]
    )
    service = ConnectorService(client)  # type: ignore[arg-type]

    option = service.resolveOption(
        pipe_id="pipe-1",
        field_id="nome_projetos",
        title="projeto a",
    )

    assert option.id == "1"
    assert option.title == "Projeto A"


@pytest.mark.unit
def test_connector_service_raises_on_ambiguous_title_resolution() -> None:
    """
    Reject ambiguous connector title resolution.
    """
    client = DummyClient(
        [
            build_pipe_schema_response(),
            {
                "data": {
                    "table_records": {
                        "edges": [
                            {"node": {"id": "1", "title": "Projeto A"}},
                            {"node": {"id": "2", "title": "Projeto A"}},
                        ]
                    }
                }
            },
        ]
    )
    service = ConnectorService(client)  # type: ignore[arg-type]

    with pytest.raises(ValidationError, match="ambiguous"):
        service.resolveOption(
            pipe_id="pipe-1",
            field_id="nome_projetos",
            title="Projeto A",
        )


@pytest.mark.unit
def test_connectors_facade_delegates_to_service() -> None:
    """
    Keep the public facade thin and aligned with the connector service.
    """

    class FakeService:
        def listFields(self, pipe_id: str) -> list[ConnectorFieldSpec]:
            assert pipe_id == "pipe-1"
            return []

        def getField(
            self, pipe_id: str, field_id: str, phase_id: str | None = None
        ) -> ConnectorFieldSpec | None:
            assert (pipe_id, field_id, phase_id) == ("pipe-1", "nome_projetos", None)
            return None

        def requireField(
            self, pipe_id: str, field_id: str, phase_id: str | None = None
        ) -> ConnectorFieldSpec:
            assert (pipe_id, field_id, phase_id) == ("pipe-1", "nome_projetos", None)
            return ConnectorFieldSpec(field_id="nome_projetos")

        def listOptions(
            self,
            pipe_id: str,
            field_id: str,
            phase_id: str | None = None,
            search: str | None = None,
            limit: int = 20,
        ) -> list[ConnectorOption]:
            assert (pipe_id, field_id, phase_id, search, limit) == (
                "pipe-1",
                "nome_projetos",
                None,
                "IA",
                5,
            )
            return []

        def resolveOption(
            self,
            pipe_id: str,
            field_id: str,
            title: str,
            phase_id: str | None = None,
        ) -> ConnectorOption:
            assert (pipe_id, field_id, title, phase_id) == (
                "pipe-1",
                "nome_projetos",
                "IA Time",
                None,
            )
            return ConnectorOption(
                id="1316654201",
                title="IA Time",
                repo_type="Table",
                repo_id="6CzIX6F_",
            )

    facade = ConnectorsFacade(FakeService())  # type: ignore[arg-type]

    assert facade.listFields("pipe-1") == []
    assert facade.getField("pipe-1", "nome_projetos") is None
    assert facade.requireField("pipe-1", "nome_projetos").field_id == "nome_projetos"
    assert facade.listOptions("pipe-1", "nome_projetos", search="IA", limit=5) == []
    assert facade.resolveOption("pipe-1", "nome_projetos", "IA Time").id == "1316654201"
