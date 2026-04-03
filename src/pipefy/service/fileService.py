# ============================================================
# Dependencies
# ============================================================
from pathlib import Path
from typing import List

from urllib.parse import urlparse, unquote

from pipefy.client.httpClient import PipefyHttpClient
from pipefy.service.cardService import CardService
from pipefy.exceptions import ValidationError, getExceptionContext

from pipefy.integrations.file.fileUploadResult import FileUploadResult
from pipefy.models.file.fileUploadRequest import FileUploadRequest
from pipefy.models.file.fileDownloadRequest import FileDownloadRequest

from pipefy.service.file.flows.fileUploadFlowV2 import FileUploadFlowV2
from pipefy.service.file.fileServiceContext import FileServiceContext
from pipefy.integrations.file.fileIntegration import FileIntegration


class FileService:
    """
    Application service responsible for file operations in Pipefy.

    This class acts as the orchestration layer between external interfaces
    (e.g., Facades) and internal domain flows.

    ARCHITECTURAL ROLE:
        - Receives structured request objects (DTO pattern)
        - Delegates execution to domain flows
        - Manages dependencies and execution context

    DESIGN PRINCIPLES:
        - No business logic
        - No parameter explosion
        - No data transformation logic
        - Strict delegation to flows

    API DESIGN:
        This service enforces a request-based API:
            - FileUploadRequest
            - FileDownloadRequest

        This ensures:
            - Consistency across operations
            - Extensibility without breaking signatures
            - Strong typing and validation

    :param client: PipefyHttpClient = HTTP client instance
    :param card_service: CardService = Card service instance

    :raises ValidationError:
        When dependencies are invalid

    :example:
        >>> from pipefy.client.httpClient import PipefyHttpClient
        >>> from pipefy.service.cardService import CardService
        >>> client = PipefyHttpClient("token", "https://api.pipefy.com/graphql")
        >>> service = FileService(client, CardService(client))
        >>> isinstance(service, FileService)
        True
    """

    # ============================================================
    # Constructor
    # ============================================================

    def __init__(
        self,
        client: PipefyHttpClient,
        card_service: CardService
    ) -> None:
        """
        Initializes FileService.

        :param client: PipefyHttpClient
        :param card_service: CardService

        :raises ValidationError:
            When dependencies are invalid

        :example:
            >>> callable(FileService)
            True
        """
        class_name, method_name = getExceptionContext(self)

        if client is None:
            raise ValidationError(
                "client must not be None",
                class_name,
                method_name
            )

        if card_service is None:
            raise ValidationError(
                "card_service must not be None",
                class_name,
                method_name
            )

        self._client = client
        self._card_service = card_service
        self._file_integration = FileIntegration()

        self._context = FileServiceContext(
            client=self._client,
            card_service=self._card_service,
            file_integration=self._file_integration
        )

        self._upload_flow_v2 = FileUploadFlowV2(self._context)

    # ============================================================
    # Upload
    # ============================================================

    def uploadFile(self, request: FileUploadRequest) -> FileUploadResult:
        """
        Uploads a file and attaches it to a Pipefy card field.

        This method delegates execution to FileUploadFlowV2, which
        implements a pipeline-based upload mechanism.

        :param request: FileUploadRequest = Upload request object

        :return: FileUploadResult = Upload result metadata

        :raises ValidationError:
            When request is invalid
        :raises RequestError:
            When upload fails
        :raises UnexpectedResponseError:
            When API response is invalid

        :example:
            >>> callable(FileService.uploadFile)
            True
        """
        class_name, method_name = getExceptionContext(self)

        if not isinstance(request, FileUploadRequest):
            raise ValidationError(
                "request must be a FileUploadRequest instance",
                class_name,
                method_name
            )

        return self._upload_flow_v2.execute(request)

    # ============================================================
    # Download
    # ============================================================

    def downloadAllAttachments(
        self,
        request: FileDownloadRequest
    ) -> List[Path]:
        """
        Downloads all attachments from a Pipefy card field.

        This method retrieves file URLs from the specified card field,
        downloads each file, and saves them locally.

        :param request: FileDownloadRequest = Download request object

        :return: list[Path] = List of saved file paths

        :raises ValidationError:
            When request is invalid
        :raises RequestError:
            When download fails

        :example:
            >>> callable(FileService.downloadAllAttachments)
            True
        """
        class_name, method_name = getExceptionContext(self)

        if not isinstance(request, FileDownloadRequest):
            raise ValidationError(
                "request must be a FileDownloadRequest instance",
                class_name,
                method_name
            )

        card = self._card_service.getCardModel(request.card_id)

        if request.field_id not in card.fields_map:
            return []

        raw_value = card.fields_map[request.field_id].value

        if not raw_value:
            return []

        import json
        attachments = json.loads(raw_value)

        output_path = Path(request.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        saved_files: List[Path] = []

        for url in attachments:
            parsed_url = urlparse(url)

            # remove query params e pega só o path
            file_name = Path(parsed_url.path).name

            # decodifica caracteres especiais
            file_name = unquote(file_name)

            content = self._file_integration.download(url)

            file_path = output_path / file_name
            file_path.write_bytes(content)

            saved_files.append(file_path)

        return saved_files


# ============================================================
# MAIN TEST
# ============================================================
if __name__ == "__main__":
    print("FileService (enterprise request-based API) ready")