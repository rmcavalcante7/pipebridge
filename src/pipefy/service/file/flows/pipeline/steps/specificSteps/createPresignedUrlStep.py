# ============================================================
# Dependencies
# ============================================================
import inspect

from pipefy.exceptions.fileUpload import FileUploadError
from pipefy.service.file.flows.pipeline.steps.baseStep import BaseStep
from pipefy.service.file.flows.pipeline.uploadPipelineContext import UploadPipelineContext


class CreatePresignedUrlStep(BaseStep):
    """
    Pipeline step responsible for generating presigned upload and download URLs.

    This step interacts with the Pipefy GraphQL API to obtain a presigned URL
    used for uploading files to storage (S3-compatible service).

    RESPONSIBILITIES:
        - Execute GraphQL mutation to request presigned URL
        - Validate API response integrity
        - Populate execution context with:
            - upload_url
            - download_url
            - normalized file path

    RETRY STRATEGY:
        - max_retries = 3
        - exponential backoff (handled by StepEngine)
        - retries only for transient failures (network / timeout)

    FAILURE MODES:
        - Network failures
        - Invalid API response
        - Missing required fields in response

    SIDE EFFECTS:
        - Mutates context:
            context.upload_url
            context.download_url
            context.files

    :example:
        >>> callable(CreatePresignedUrlStep.execute)
        True
    """

    max_retries: int = 3
    retry_base_delay: float = 0.5

    # ============================================================
    # Retry Strategy
    # ============================================================

    def shouldRetry(self, exc: Exception) -> bool:
        """
        Determines whether retry should occur.

        Retry is only performed for transient errors such as:
            - network failures
            - timeouts
            - connection errors

        :param exc: Exception = Raised exception

        :return: bool

        :example:
            >>> step = CreatePresignedUrlStep()
            >>> isinstance(step.shouldRetry(Exception("timeout")), bool)
            True
        """
        message = str(exc).lower()

        return (
            "timeout" in message
            or "connection" in message
            or "temporarily unavailable" in message
        )

    # ============================================================
    # Execution
    # ============================================================

    def execute(self, context: UploadPipelineContext) -> None:
        """
        Executes presigned URL generation.

        :param context: UploadPipelineContext

        :return: None

        :raises FileUploadError:
            When API call fails or response is invalid
        """
        class_name = self.__class__.__name__
        method_name = inspect.currentframe().f_code.co_name

        request = context.request

        try:
            query = f"""
            mutation {{
                createPresignedUrl(
                    input: {{
                        organizationId: {request.organization_id},
                        fileName: "{request.file_name}"
                    }}
                ) {{
                    url
                    downloadUrl
                }}
            }}
            """

            response = context.client.sendRequest(query)

            # --------------------------------------------------------
            # Validate response structure
            # --------------------------------------------------------
            if not isinstance(response, dict):
                raise FileUploadError(
                    message="Invalid response format from API",
                    class_name=class_name,
                    method_name=method_name
                )

            data = response.get("data")
            if not data:
                raise FileUploadError(
                    message="Missing 'data' in API response",
                    class_name=class_name,
                    method_name=method_name
                )

            presigned = data.get("createPresignedUrl")
            if not presigned:
                raise FileUploadError(
                    message="Missing 'createPresignedUrl' in response",
                    class_name=class_name,
                    method_name=method_name
                )

            upload_url = presigned.get("url")
            download_url = presigned.get("downloadUrl")

            if not upload_url or not download_url:
                raise FileUploadError(
                    message=(
                        f"Invalid presigned URL response. "
                        f"upload_url={upload_url}, download_url={download_url}"
                    ),
                    class_name=class_name,
                    method_name=method_name
                )

            # --------------------------------------------------------
            # Update context
            # --------------------------------------------------------
            context.upload_url = upload_url
            context.download_url = download_url

            file_path = context.integration.extractFilePath(upload_url)
            context.files = [file_path]

        except FileUploadError:
            raise

        except Exception as exc:
            raise FileUploadError(
                message=str(exc),
                class_name=class_name,
                method_name=method_name
            ) from exc