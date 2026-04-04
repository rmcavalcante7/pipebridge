# ============================================================
# Dependencies
# ============================================================
from pipefy.service.file.flows.pipeline.steps.baseStep import BaseStep
from pipefy.service.file.flows.pipeline.uploadPipelineContext import UploadPipelineContext
from pipefy.exceptions import RequestError
from pipefy.exceptions.utils import getExceptionContext


class UploadStep(BaseStep):
    """
    Pipeline step responsible for uploading a file to external storage.

    This step performs the actual file upload using a presigned URL.

    RETRY STRATEGY:
        - max_retries = 3
        - retry controlled by StepEngine
        - retries only for transient failures

    RESPONSIBILITIES:
        - Upload file bytes to storage
        - Delegate retry logic to StepEngine

    :example:
        >>> callable(UploadStep.execute)
        True
    """

    max_retries: int = 3

    # ============================================================
    # Execution
    # ============================================================

    def execute(self, context: UploadPipelineContext) -> None:
        """
        Executes file upload.

        :param context: UploadPipelineContext

        :return: None

        :raises RequestError:
            When upload fails
        """
        class_name, method_name = getExceptionContext(self)

        try:
            context.integration.upload(
                context.upload_url,
                context.request.file_bytes
            )

        except Exception as exc:
            raise RequestError(
                message=str(exc),
                class_name=class_name,
                method_name=method_name
            ) from exc