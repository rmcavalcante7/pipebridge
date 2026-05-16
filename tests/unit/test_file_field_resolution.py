"""
Unit tests for file flows that resolve field existence via schema helpers.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from pipebridge.exceptions import ValidationError
from pipebridge.models.file.fileDownloadRequest import FileDownloadRequest
from pipebridge.models.phaseField import PhaseField
from pipebridge.service.file.flows.download.fileDownloadContext import (
    FileDownloadContext,
)
from pipebridge.service.file.flows.download.fileDownloadFlow import FileDownloadFlow
from pipebridge.service.file.flows.upload.config.uploadConfig import UploadConfig
from pipebridge.service.file.flows.upload.rules.validateFieldRule import (
    ValidateFieldRule,
)
from pipebridge.service.file.flows.upload.steps.mergeAttachmentsStep import (
    MergeAttachmentsStep,
)


@pytest.mark.unit
def test_validate_field_rule_uses_current_phase_schema_by_default() -> None:
    """
    Validate upload field existence against the current phase schema by default.
    """
    rule = ValidateFieldRule()
    field = PhaseField(id="anexos", label="Anexos", type="attachment")
    card = SimpleNamespace(current_phase=SimpleNamespace(id="phase-1"))
    service = SimpleNamespace(
        getCardModel=lambda card_id: card,
        getCardCurrentPhaseField=lambda card_id, field_id: field,
        getCardPipeField=lambda card_id, field_id: None,
    )
    context = SimpleNamespace(
        request=SimpleNamespace(card_id="card-1", field_id="anexos"),
        card_service=service,
        config=UploadConfig(),
    )

    rule.execute(context)


@pytest.mark.unit
def test_validate_field_rule_can_fallback_to_pipe_schema() -> None:
    """
    Validate upload field existence against the whole pipe schema when enabled.
    """
    rule = ValidateFieldRule()
    field = PhaseField(id="anexar_assessement", label="Anexo", type="attachment")
    service = SimpleNamespace(
        getCardPipeField=lambda card_id, field_id: field,
    )
    context = SimpleNamespace(
        request=SimpleNamespace(card_id="card-1", field_id="anexar_assessement"),
        card_service=service,
        config=UploadConfig(validate_field_in_current_phase=False),
    )

    rule.execute(context)


@pytest.mark.unit
def test_validate_field_rule_rejects_non_attachment_schema_field() -> None:
    """
    Validate semantic rejection for non-attachment schema fields.
    """
    rule = ValidateFieldRule()
    field = PhaseField(id="priority", label="Priority", type="short_text")
    service = SimpleNamespace(
        getCardPipeField=lambda card_id, field_id: field,
    )
    context = SimpleNamespace(
        request=SimpleNamespace(card_id="card-1", field_id="priority"),
        card_service=service,
        config=UploadConfig(validate_field_in_current_phase=False),
    )

    with pytest.raises(ValidationError) as exc_info:
        rule.execute(context)

    assert "not an attachment field" in str(exc_info.value)


@pytest.mark.unit
def test_merge_attachments_step_uses_card_attachments_surface() -> None:
    """
    Validate merge behavior using attachment payloads instead of card.fields.
    """
    step = MergeAttachmentsStep()
    service = SimpleNamespace(
        listCardAttachmentsByField=lambda card_id, field_id: [
            {
                "path": "uploads/existing-a.txt",
                "url": "https://example.com/existing-a.txt",
            },
            {
                "url": "https://example.com/existing-b.txt",
            },
        ]
    )
    integration = SimpleNamespace(
        extractFilePath=lambda url: f"normalized/{Path(url).name}"
    )
    context = SimpleNamespace(
        request=SimpleNamespace(
            card_id="card-1",
            field_id="anexos",
            replace_files=False,
        ),
        card_service=service,
        integration=integration,
        files=["uploads/new.txt"],
    )

    step.execute(context)

    assert context.files == [
        "uploads/existing-a.txt",
        "normalized/existing-b.txt",
        "uploads/new.txt",
    ]


@pytest.mark.unit
def test_file_download_flow_uses_attachment_surface_by_field(
    tmp_path: Path,
) -> None:
    """
    Validate download flow using schema lookup plus card attachments by field.
    """
    service = SimpleNamespace(
        getCardPipeField=lambda card_id, field_id: PhaseField(
            id=field_id,
            label="Anexos",
            type="attachment",
        ),
        listCardAttachmentsByField=lambda card_id, field_id: [
            {
                "path": "uploads/teste.txt",
                "url": "https://example.com/teste.txt",
            }
        ],
    )
    integration = SimpleNamespace(download=lambda url: b"hello")
    context = FileDownloadContext(
        card_service=service,
        file_integration=integration,
    )
    flow = FileDownloadFlow(context)

    files = flow.execute(
        FileDownloadRequest(
            card_id="card-1",
            field_id="anexos",
            output_dir=str(tmp_path),
        )
    )

    assert len(files) == 1
    assert files[0].name == "teste.txt"
    assert files[0].read_bytes() == b"hello"
