"""
Integration tests for the live file service flows.
"""

from __future__ import annotations

import random
from pathlib import Path
from typing import Any

import pytest

from pipebridge import FileDownloadRequest, FileUploadRequest, UploadConfig
from pipebridge.exceptions import ValidationError
from pipebridge.service.file.flows.upload.config.uploadConfig import UploadConfig
from pipebridge.workflow.config.circuitBreakerConfig import CircuitBreakerConfig
from pipebridge.workflow.config.retryConfig import RetryConfig
from pipebridge.workflow.rules.baseRule import BaseRule
from pipebridge.workflow.steps.baseStep import BaseStep

CARD_ID = "1328390184"
PHASE_ID = "342616256"
ORG_ID = "133269"
FIELD_ID = "c_digo"


def _build_random_txt_file_name() -> str:
    """
    Build a randomized test filename.

    :return: str = Randomized ``.txt`` filename
    """
    return f"teste_{random.randint(1, 100)}.txt"


def _build_upload_request() -> FileUploadRequest:
    """
    Build a standard live upload request used by integration tests.

    :return: FileUploadRequest = Ready-to-use upload request
    """
    return FileUploadRequest(
        file_name=_build_random_txt_file_name(),
        file_bytes=b"hello from pytest pipebridge sdk",
        card_id=CARD_ID,
        field_id=FIELD_ID,
        organization_id=ORG_ID,
        replace_files=False,
        expected_phase_id=PHASE_ID,
    )


class _BlockTxtRule(BaseRule):
    """
    Block ``.txt`` uploads during validation.
    """

    priority = 25

    def execute(self, context) -> None:
        """
        Execute the blocking rule.

        :param context: UploadPipelineContext = Shared upload context

        :raises ValidationError:
            When the file extension is blocked
        """
        if context.request.file_name.endswith(".txt"):
            raise ValidationError(
                message="TXT files are not allowed",
                class_name=self.__class__.__name__,
                method_name="execute",
            )


class _AllowAllRule(BaseRule):
    """
    Allow every upload request.
    """

    def execute(self, context) -> None:
        """
        Execute a no-op validation rule.

        :param context: UploadPipelineContext = Shared upload context
        """
        return None


class _AlwaysFailRule(BaseRule):
    """
    Force validation failure.
    """

    priority = 1

    def execute(self, context) -> None:
        """
        Execute a forced validation failure.

        :param context: UploadPipelineContext = Shared upload context

        :raises ValidationError:
            Always raised to simulate failure
        """
        raise ValidationError(
            message="Forced failure for testing",
            class_name=self.__class__.__name__,
            method_name="execute",
        )


class _ForceNetworkFailureStep(BaseStep):
    """
    Step that always fails with a retryable network-like error.
    """

    execution_profile = "network"

    def execute(self, context) -> None:
        """
        Execute the forced failing step.

        :param context: UploadPipelineContext = Shared upload context

        :raises RuntimeError:
            Always raised to simulate a transient network failure
        """
        raise RuntimeError("connection reset by peer")


@pytest.mark.integration
def test_file_upload_live(live_pipefy_api: Any) -> None:
    """
    Validate basic live file upload through the public facade.
    """
    result = live_pipefy_api.files.uploadFile(_build_upload_request())

    assert result.success is True
    assert isinstance(result.file_path, list)
    assert result.file_path


@pytest.mark.integration
def test_file_upload_blocking_rule_live(live_pipefy_api: Any) -> None:
    """
    Validate that a custom blocking rule interrupts upload before steps.
    """
    with pytest.raises(Exception) as exc_info:
        live_pipefy_api.files.uploadFile(
            request=_build_upload_request(),
            extra_rules=[_BlockTxtRule()],
        )

    assert "TXT files are not allowed" in str(exc_info.value)


@pytest.mark.integration
def test_file_upload_allowing_rule_live(live_pipefy_api: Any) -> None:
    """
    Validate upload success when a permissive custom rule is added.
    """
    result = live_pipefy_api.files.uploadFile(
        request=_build_upload_request(),
        extra_rules=[_AllowAllRule()],
    )

    assert result.success is True


@pytest.mark.integration
def test_file_upload_advanced_config_live(live_pipefy_api: Any) -> None:
    """
    Validate upload success with custom retry and circuit breaker configuration.
    """
    config = UploadConfig(
        retry=RetryConfig(max_retries=5, base_delay=1.0),
        circuit=CircuitBreakerConfig(failure_threshold=5, recovery_timeout=5.0),
    )

    result = live_pipefy_api.files.uploadFile(
        request=_build_upload_request(),
        config=config,
    )

    assert result.success is True


@pytest.mark.integration
def test_file_upload_failure_simulation_live(live_pipefy_api: Any) -> None:
    """
    Validate error propagation from a forced custom validation failure.
    """
    config = UploadConfig(
        retry=RetryConfig(max_retries=2, base_delay=0.2),
        circuit=CircuitBreakerConfig(failure_threshold=2, recovery_timeout=2.0),
    )

    with pytest.raises(Exception) as exc_info:
        live_pipefy_api.files.uploadFile(
            request=_build_upload_request(),
            extra_rules=[_AlwaysFailRule()],
            config=config,
        )

    assert "Forced failure for testing" in str(exc_info.value)


@pytest.mark.integration
def test_file_circuit_breaker_opening_live(live_pipefy_api: Any) -> None:
    """
    Validate circuit breaker opening through a forced failing upload pipeline.
    """
    flow = live_pipefy_api.files._service._upload_flow
    original_pipeline = flow._pipeline

    try:
        flow._pipeline = [_ForceNetworkFailureStep()]
        config = UploadConfig(
            retry=RetryConfig(max_retries=1, base_delay=0.0),
            circuit=CircuitBreakerConfig(failure_threshold=2, recovery_timeout=5.0),
        )

        request = _build_upload_request()

        for _ in range(2):
            try:
                live_pipefy_api.files.uploadFile(request=request, config=config)
            except Exception:
                pass

        with pytest.raises(Exception) as exc_info:
            live_pipefy_api.files.uploadFile(request=request, config=config)

        assert "Circuit OPEN" in str(exc_info.value)
    finally:
        flow._pipeline = original_pipeline


@pytest.mark.integration
def test_file_download_live(live_pipefy_api: Any, project_root: Path) -> None:
    """
    Validate downloading all attachments from the target card field.
    """
    output_dir = project_root / "tests" / "downloads_pytest"
    output_dir.mkdir(parents=True, exist_ok=True)

    request = FileDownloadRequest(
        card_id=CARD_ID,
        field_id=FIELD_ID,
        output_dir=str(output_dir),
    )

    files = live_pipefy_api.files.downloadAllAttachments(request)

    assert isinstance(files, list)
    for file_path in files:
        assert isinstance(file_path, Path)
        assert file_path.exists()
