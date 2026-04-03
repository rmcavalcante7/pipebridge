# ============================================================
# Dependencies
# ============================================================
import json
from typing import Dict, Any

from pipefy.exceptions import RequestError, ValidationError, UnexpectedResponseError
from pipefy.exceptions.utils import getExceptionContext

from pipefy.service.file.flows.baseFileUploadFlow import BaseFileUploadFlow
from pipefy.models.file.fileUploadRequest import FileUploadRequest
from pipefy.integrations.file.fileUploadResult import FileUploadResult


# ============================================================
# FileUploadFlowV1
# ============================================================
class FileUploadFlowV1(BaseFileUploadFlow):
    """
    Default implementation of file upload flow (Version 1).

    This class represents the original and stable upload behavior.

    RESPONSIBILITIES:
        - Generate presigned URL via Pipefy GraphQL
        - Upload file to external storage (S3)
        - Normalize file path
        - Retrieve existing attachments
        - Merge attachments (append or replace)
        - Attach files to card

    CHARACTERISTICS:
        - Sequential execution (no pipeline)
        - No retry mechanism
        - Simple and predictable behavior

    USE CASE:
        This flow should be used when:
            - Simplicity is preferred
            - No advanced processing is required
            - Backward compatibility is critical

    :param context: FileServiceContext = Dependency container

    :example:
        >>> callable(FileUploadFlowV1.execute)
        True
    """

    def __init__(self, context) -> None:
        """
        Initializes FileUploadFlowV1.

        :param context: FileServiceContext = Shared dependencies

        :example:
            >>> callable(FileUploadFlowV1)
            True
        """
        self._ctx = context

    # ============================================================
    # Public API
    # ============================================================

    def execute(self, request: FileUploadRequest) -> FileUploadResult:
        """
        Executes upload flow V1.

        This method performs the full upload process in a sequential manner.

        :param request: FileUploadRequest = Upload request object

        :return: FileUploadResult = Upload result metadata

        :raises ValidationError:
            When request is invalid
        :raises RequestError:
            When HTTP or processing fails
        :raises UnexpectedResponseError:
            When API response is invalid

        :example:
            >>> callable(FileUploadFlowV1.execute)
            True
        """
        class_name, method_name = getExceptionContext(self)

        try:
            presigned = self._createPresignedUrl(
                request.file_name,
                request.organization_id
            )

            data = presigned.get("data", {})
            presigned_data = data.get("createPresignedUrl", {})

            upload_url = presigned_data.get("url")
            download_url = presigned_data.get("downloadUrl")

            if not upload_url:
                raise UnexpectedResponseError(
                    message="Invalid upload URL",
                    class_name=class_name,
                    method_name=method_name
                )

            # Upload file
            self._ctx.file_integration.upload(upload_url, request.file_bytes)

            # Normalize path
            file_path = self._ctx.file_integration.extractFilePath(upload_url)

            files = [file_path]

            # Merge with existing files
            if not request.replace_files:
                files += self._getAttachedFiles(request)

            # Attach to card
            self._attachToCard(request, files)

            return FileUploadResult(
                file_path=files,
                download_url=download_url,
                success=True
            )

        except (ValidationError, RequestError, UnexpectedResponseError):
            raise

        except Exception as exc:
            raise RequestError(
                message=str(exc),
                class_name=class_name,
                method_name=method_name
            ) from exc

    # ============================================================
    # Internal Methods
    # ============================================================

    def _createPresignedUrl(
        self,
        file_name: str,
        organization_id: str
    ) -> Dict[str, Any]:
        """
        Creates a presigned URL using Pipefy GraphQL.

        :param file_name: str = File name
        :param organization_id: str = Organization identifier

        :return: dict = GraphQL response

        :raises RequestError:
            When request fails

        :example:
            >>> callable(FileUploadFlowV1._createPresignedUrl)
            True
        """
        query = f"""
        mutation {{
            createPresignedUrl(
                input: {{
                    organizationId: {organization_id},
                    fileName: "{file_name}"
                }}
            ) {{
                url
                downloadUrl
            }}
        }}
        """

        return self._ctx.client.sendRequest(query, timeout=60)

    def _getAttachedFiles(self, request: FileUploadRequest) -> list[str]:
        """
        Retrieves existing attachments and normalizes them.

        :param request: FileUploadRequest

        :return: list[str]

        :example:
            >>> callable(FileUploadFlowV1._getAttachedFiles)
            True
        """
        card = self._ctx.card_service.getCardModel(request.card_id)

        if request.field_id not in card.fields_map:
            return []

        raw_value = card.fields_map[request.field_id].value

        if not raw_value:
            return []

        try:
            urls = json.loads(raw_value)
            return [
                self._ctx.file_integration.extractFilePath(url)
                for url in urls
            ]
        except Exception:
            return []

    def _attachToCard(self, request: FileUploadRequest, files: list[str]) -> None:
        """
        Attaches files to Pipefy card field.

        :param request: FileUploadRequest
        :param files: list[str]

        :raises RequestError:

        :example:
            >>> callable(FileUploadFlowV1._attachToCard)
            True
        """
        mutation = f"""
        mutation {{
          updateCardField(input: {{
            card_id: "{request.card_id}",
            field_id: "{request.field_id}",
            new_value: {json.dumps(files)}
          }}) {{
            success
          }}
        }}
        """

        self._ctx.client.sendRequest(mutation)


# ============================================================
# MAIN TEST
# ============================================================
if __name__ == "__main__":
    print("FileUploadFlowV1 loaded successfully")