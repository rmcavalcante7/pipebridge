# ============================================================
# Dependencies
# ============================================================
from pipebridge.workflow.steps.baseStep import BaseStep
from pipebridge.service.file.flows.upload.context.uploadPipelineContext import (
    UploadPipelineContext,
)
from pipebridge.exceptions.file import FileTransferError
from pipebridge.exceptions.core.utils import getExceptionContext


class UploadStep(BaseStep):
    """
    Pipeline step responsible for uploading a file to external storage.

    This step performs the actual file upload using a presigned URL.

    EXECUTION POLICY:
        - retry and circuit breaker are applied externally
        - this step declares ``execution_profile = "network"``

    RESPONSIBILITIES:
        - Upload file bytes to storage
        - Delegate retry logic to StepEngine

    :example:
        >>> callable(UploadStep.execute)
        True
    """

    execution_profile: str = "network"

    # ============================================================
    # Execution
    # ============================================================

    def execute(self, context: UploadPipelineContext) -> None:
        """
        Execute file upload.

        :param context: UploadPipelineContext

        :return: None

        :raises FileTransferError:
            When upload fails

        :example:
            >>> callable(UploadStep.execute)
            True
        """
        class_name, method_name = getExceptionContext(self)
        upload_url = context.upload_url

        if upload_url is None:
            raise FileTransferError(
                message="upload_url must be available before upload execution",
                class_name=class_name,
                method_name=method_name,
            )

        try:
            context.integration.upload(upload_url, context.request.file_bytes)

        except Exception as exc:
            raise FileTransferError(
                message=str(exc),
                class_name=class_name,
                method_name=method_name,
                cause=exc,
                retryable=getattr(exc, "retryable", True),
            ) from exc
