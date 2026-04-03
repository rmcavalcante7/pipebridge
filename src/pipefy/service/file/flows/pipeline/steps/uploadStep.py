from pipefy.service.file.flows.pipeline.uploadPipelineContext import UploadPipelineContext
from pipefy.exceptions import RequestError
from pipefy.exceptions.utils import getExceptionContext


class UploadStep:
    """
    Pipeline step responsible for uploading a file to external storage.

    This step performs the actual file upload using a presigned URL.

    FEATURES:
        - Retry mechanism
        - Failure escalation

    :param retries: int = Number of retry attempts

    :example:
        >>> callable(UploadStep.execute)
        True
    """

    def __init__(self, retries: int = 3) -> None:
        """
        Initializes UploadStep.

        :param retries: int = Number of retry attempts

        :raises ValueError:
            When retries is invalid
        """
        if retries <= 0:
            raise ValueError("retries must be greater than zero")

        self._retries = retries

    def __str__(self) -> str:
        """
        Human-readable representation.

        :return: str
        """
        return f"<UploadStep retries={self._retries}>"

    def __repr__(self) -> str:
        """
        Developer-friendly representation.

        :return: str
        """
        return f"<UploadStep(retries={self._retries})>"

    def execute(self, context: UploadPipelineContext) -> None:
        """
        Executes upload logic with retry support.

        :param context: UploadPipelineContext

        :return: None

        :raises RequestError:
            When upload fails after all retries
        """
        class_name, method_name = getExceptionContext(self)

        last_error = None

        for attempt in range(self._retries):
            try:
                context.integration.upload(
                    context.upload_url,
                    context.request.file_bytes
                )
                return

            except Exception as exc:
                last_error = exc

        raise RequestError(
            f"Upload failed after {self._retries} attempts: {last_error}",
            class_name,
            method_name
        )