"""
Unit tests for connector schema foundation.
"""

from __future__ import annotations

import pytest

from pipebridge.models.connectedRepoRef import ConnectedRepoRef
from pipebridge.models.phase import Phase
from pipebridge.models.phaseField import PhaseField
from pipebridge.models.pipe import Pipe
from pipebridge.service.pipe.pipeService import PipeService


class DummyClient:
    """
    Minimal fake client that captures generated pipe schema queries.
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
def test_connected_repo_ref_normalizes_public_union_typenames() -> None:
    """
    Normalize Pipefy public union typenames into stable SDK values.
    """
    pipe_repo = ConnectedRepoRef.fromDict(
        {"__typename": "PublicPipe", "id": "307073107", "name": "Automations"}
    )
    table_repo = ConnectedRepoRef.fromDict(
        {"__typename": "PublicTable", "id": "6CzIX6F_", "name": "Projects"}
    )

    assert pipe_repo.repo_type == "Pipe"
    assert pipe_repo.isPipe() is True
    assert table_repo.repo_type == "Table"
    assert table_repo.isTable() is True


@pytest.mark.unit
def test_phase_field_parses_connector_metadata() -> None:
    """
    Parse connector-specific field metadata from schema payloads.
    """
    field = PhaseField.fromDict(
        {
            "id": "nome_projetos",
            "label": "Projetos",
            "type": "connector",
            "required": True,
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
    )

    assert field.isConnector() is True
    assert field.help_text == "Select a project"
    assert field.can_connect_existing is True
    assert field.can_connect_multiples is False
    assert field.can_create_new_connected is False
    assert field.connected_repo is not None
    assert field.connected_repo.repo_type == "Table"
    assert field.connected_repo.id == "6CzIX6F_"


@pytest.mark.unit
def test_phase_and_pipe_expose_connector_helpers() -> None:
    """
    Expose semantic helpers for connector fields at phase and pipe level.
    """
    start_form_connector = PhaseField(
        id="nome_projetos",
        label="Projetos",
        type="connector",
        connected_repo=ConnectedRepoRef("Table", "6CzIX6F_", "TechMaster Projetos"),
        can_connect_existing=True,
    )
    phase_connector = PhaseField(
        id="automa_o",
        label="Pesquise o nome Automacao",
        type="connector",
        connected_repo=ConnectedRepoRef(
            "Pipe", "307073107", "Base historica Fila de Automacao"
        ),
        can_connect_existing=True,
    )
    phase = Phase(id="phase-1", name="Backlog", fields=[phase_connector])
    pipe = Pipe(
        id="pipe-1",
        name="Pipe 1",
        start_form_fields=[start_form_connector],
        phases=[phase],
    )

    assert [field.id for field in phase.getConnectorFields()] == ["automa_o"]
    assert [field.id for field in pipe.iterStartFormConnectorFields()] == [
        "nome_projetos"
    ]
    assert [field.id for field in pipe.getConnectorFields()] == [
        "nome_projetos",
        "automa_o",
    ]


@pytest.mark.unit
def test_pipe_service_field_catalog_requests_and_parses_connector_metadata() -> None:
    """
    Include connector metadata in the field catalog query and parse it into models.
    """
    client = DummyClient(
        {
            "data": {
                "pipe": {
                    "id": "pipe-1",
                    "name": "Pipe 1",
                    "cards_count": 1,
                    "organization": {"id": "org-1"},
                    "labels": [],
                    "users": [],
                    "start_form_fields": [
                        {
                            "id": "nome_projetos",
                            "uuid": "uuid-proj",
                            "internal_id": "start_form.nome_projetos",
                            "label": "Projetos",
                            "type": "connector",
                            "required": True,
                            "description": "",
                            "options": [],
                            "help_text": "",
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
                                    "uuid": "uuid-auto",
                                    "internal_id": "phase.automa_o",
                                    "label": "Pesquise o nome Automacao",
                                    "type": "connector",
                                    "required": False,
                                    "description": "",
                                    "options": [],
                                    "help_text": "",
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
    )

    service = PipeService(client)  # type: ignore[arg-type]
    pipe = service.getPipeFieldCatalog("pipe-1")

    assert client.last_query is not None
    assert "connectedRepo" in client.last_query
    assert "canConnectExisting" in client.last_query
    assert "canConnectMultiples" in client.last_query
    assert "canCreateNewConnected" in client.last_query

    start_form_field = pipe.requireStartFormField("nome_projetos")
    phase_field = pipe.requirePhase("phase-1").requireField("automa_o")

    assert start_form_field.connected_repo is not None
    assert start_form_field.connected_repo.repo_type == "Table"
    assert phase_field.connected_repo is not None
    assert phase_field.connected_repo.repo_type == "Pipe"
    assert phase_field.can_connect_multiples is True
