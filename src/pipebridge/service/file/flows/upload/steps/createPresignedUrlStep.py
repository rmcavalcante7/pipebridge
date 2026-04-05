# ============================================================
# Dependencies
# ============================================================
import inspect

from pipebridge.exceptions.file import PresignedUrlCreationError
from pipebridge.workflow.steps.baseStep import BaseStep
from pipebridge.service.file.flows.upload.context.uploadPipelineContext import (
    UploadPipelineContext,
)


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

    EXECUTION POLICY:
        - retry and circuit breaker are applied externally
        - this step declares ``execution_profile = "network"``
        - retryability is resolved by the workflow policy layer

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

    execution_profile: str = "network"

    # ============================================================
    # Execution
    # ============================================================

    def execute(self, context: UploadPipelineContext) -> None:
        """
        Execute presigned URL generation.

        :param context: UploadPipelineContext

        :return: None

        :raises PresignedUrlCreationError:
            When API call fails or response is invalid

        :example:
            >>> callable(CreatePresignedUrlStep.execute)
            True
        """
        class_name = self.__class__.__name__
        frame = inspect.currentframe()
        method_name = frame.f_code.co_name if frame is not None else "execute"

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
                raise PresignedUrlCreationError(
                    message="Invalid response format from API",
                    class_name=class_name,
                    method_name=method_name,
                )

            data = response.get("data")
            if not data:
                raise PresignedUrlCreationError(
                    message="Missing 'data' in API response",
                    class_name=class_name,
                    method_name=method_name,
                )

            presigned = data.get("createPresignedUrl")
            if not presigned:
                raise PresignedUrlCreationError(
                    message="Missing 'createPresignedUrl' in response",
                    class_name=class_name,
                    method_name=method_name,
                )

            upload_url = presigned.get("url")
            download_url = presigned.get("downloadUrl")

            if not upload_url or not download_url:
                raise PresignedUrlCreationError(
                    message=(
                        f"Invalid presigned URL response. "
                        f"upload_url={upload_url}, download_url={download_url}"
                    ),
                    class_name=class_name,
                    method_name=method_name,
                )

            # --------------------------------------------------------
            # Update context
            # --------------------------------------------------------
            context.upload_url = upload_url
            context.download_url = download_url

            file_path = context.integration.extractFilePath(upload_url)
            context.files = [file_path]

        except PresignedUrlCreationError:
            raise

        except Exception as exc:
            raise PresignedUrlCreationError(
                message=str(exc),
                class_name=class_name,
                method_name=method_name,
                cause=exc,
                retryable=getattr(exc, "retryable", False),
            ) from exc
