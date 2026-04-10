"""
Functional tests for the public SDK API surface without real network calls.
"""

from __future__ import annotations

from typing import Any

import pytest

from pipebridge import (
    CardMoveConfig,
    CardUpdateConfig,
    FileDownloadRequest,
    FileUploadRequest,
    PipeBridge,
    TransportConfig,
    UploadConfig,
)


class _FakeCardsService:
    """
    Minimal fake card service for facade behavior tests.
    """

    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def updateFields(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(("updateFields", kwargs))
        return {"ok": True, "operation": "updateFields"}

    def createCard(
        self, pipe_id: str, title: str, fields: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        self.calls.append(
            (
                "createCard",
                {"pipe_id": pipe_id, "title": title, "fields": fields},
            )
        )
        return {"ok": True, "operation": "createCard"}

    def createCardSafely(
        self, pipe_id: str, title: str, fields: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        self.calls.append(
            (
                "createCardSafely",
                {"pipe_id": pipe_id, "title": title, "fields": fields},
            )
        )
        return {"ok": True, "operation": "createCardSafely"}

    def moveCardToPhaseSafely(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(("moveCardToPhaseSafely", kwargs))
        return {"ok": True, "operation": "moveCardToPhaseSafely"}

    def invalidatePipeSchemaCache(self, pipe_id: str | None = None) -> None:
        self.calls.append(("invalidatePipeSchemaCache", {"pipe_id": pipe_id}))

    def getPipeSchemaCacheStats(self) -> dict[str, Any]:
        self.calls.append(("getPipeSchemaCacheStats", {}))
        return {"entries": 0}

    def getPipeSchemaCacheEntryInfo(self, pipe_id: str) -> dict[str, Any]:
        self.calls.append(("getPipeSchemaCacheEntryInfo", {"pipe_id": pipe_id}))
        return {"pipe_id": pipe_id}


@pytest.mark.functional
def test_top_level_public_imports_are_usable() -> None:
    """
    Validate the main top-level objects exposed by ``pipebridge.__init__``.
    """
    upload_request = FileUploadRequest(
        file_name="file.txt",
        file_bytes=b"data",
        card_id="card-1",
        field_id="field-1",
        organization_id="org-1",
    )
    download_request = FileDownloadRequest(
        card_id="card-1",
        field_id="field-1",
        output_dir="tests",
    )

    assert isinstance(upload_request, FileUploadRequest)
    assert isinstance(download_request, FileDownloadRequest)
    assert isinstance(UploadConfig(), UploadConfig)
    assert isinstance(CardUpdateConfig(), CardUpdateConfig)
    assert isinstance(CardMoveConfig(), CardMoveConfig)
    assert isinstance(TransportConfig(), TransportConfig)


@pytest.mark.functional
def test_cards_facade_delegates_update_and_move_operations() -> None:
    """
    Validate the public cards facade behavior independently from the network.
    """
    fake_service = _FakeCardsService()
    cards_facade = PipeBridge.__new__(PipeBridge)
    from pipebridge.facade.pipefyFacade import CardsFacade

    cards_facade = CardsFacade(fake_service)

    create_result = cards_facade.create(
        pipe_id="pipe-1",
        title="Card",
        fields={"name": "Rafael"},
    )
    create_safely_result = cards_facade.createSafely(
        pipe_id="pipe-1",
        title="Card",
        fields={"name": "Rafael"},
    )
    update_result = cards_facade.updateFields(
        card_id="card-1",
        fields={"name": "Rafael"},
        config=CardUpdateConfig(),
    )
    move_result = cards_facade.moveSafely(
        card_id="card-1",
        destination_phase_id="phase-2",
        config=CardMoveConfig(),
    )
    cards_facade.invalidateSchemaCache("pipe-1")
    stats = cards_facade.getSchemaCacheStats()
    entry_info = cards_facade.getSchemaCacheEntryInfo("pipe-1")

    assert create_result["operation"] == "createCard"
    assert create_safely_result["operation"] == "createCardSafely"
    assert update_result["operation"] == "updateFields"
    assert move_result["operation"] == "moveCardToPhaseSafely"
    assert stats == {"entries": 0}
    assert entry_info == {"pipe_id": "pipe-1"}
    assert fake_service.calls[0][0] == "createCard"
    assert fake_service.calls[1][0] == "createCardSafely"
    assert fake_service.calls[2][0] == "updateFields"
    assert fake_service.calls[3][0] == "moveCardToPhaseSafely"
