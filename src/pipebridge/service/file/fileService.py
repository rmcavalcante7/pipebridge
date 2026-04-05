# ============================================================
# Dependencies
# ============================================================
from pathlib import Path
from typing import List, Optional, Sequence

from pipebridge.client.httpClient import PipefyHttpClient
from pipebridge.service.card.cardService import CardService
from pipebridge.exceptions import ValidationError, getExceptionContext

from pipebridge.integrations.file.fileUploadResult import FileUploadResult
from pipebridge.models.file.fileUploadRequest import FileUploadRequest
from pipebridge.models.file.fileDownloadRequest import FileDownloadRequest
from pipebridge.service.file.flows.download.fileDownloadContext import (
    FileDownloadContext,
)
from pipebridge.service.file.flows.download.fileDownloadFlow import FileDownloadFlow
from pipebridge.service.file.flows.upload.config.uploadConfig import UploadConfig
from pipebridge.service.file.flows.upload.fileUploadFlow import FileUploadFlow
from pipebridge.service.file.fileServiceContext import FileServiceContext
from pipebridge.integrations.file.fileIntegration import FileIntegration
from pipebridge.workflow.rules.baseRule import BaseRule
from pipebridge.workflow.steps.baseStep import BaseStep


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
        >>> from pipebridge.client.httpClient import PipefyHttpClient
        >>> from pipebridge.service.card.cardService import CardService
        >>> client = PipefyHttpClient("token", "https://api.pipefy.com/graphql")
        >>> service = FileService(client, CardService(client))
        >>> isinstance(service, FileService)
        True
    """

    # ============================================================
    # Constructor
    # ============================================================

    def __init__(self, client: PipefyHttpClient, card_service: CardService) -> None:
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
            raise ValidationError("client must not be None", class_name, method_name)

        if card_service is None:
            raise ValidationError(
                "card_service must not be None", class_name, method_name
            )

        self._client = client
        self._card_service = card_service
        self._file_integration = FileIntegration()

        self._context = FileServiceContext(
            client=self._client,
            card_service=self._card_service,
            file_integration=self._file_integration,
        )
        self._download_context = FileDownloadContext(
            card_service=self._card_service, file_integration=self._file_integration
        )

        self._upload_flow = FileUploadFlow(self._context)
        self._download_flow = FileDownloadFlow(self._download_context)

    # ============================================================
    # Upload
    # ============================================================

    def uploadFile(
        self,
        request: FileUploadRequest,
        extra_rules: Optional[list[BaseRule]] = None,
        config: Optional[UploadConfig] = None,
        extra_steps_before: Optional[Sequence[BaseStep]] = None,
        extra_steps_after: Optional[Sequence[BaseStep]] = None,
    ) -> FileUploadResult:
        """
        Uploads a file and attaches it to a Pipefy card field.

        This method delegates execution to FileUploadFlow, which
        implements a pipeline-based upload mechanism.

        :param request: FileUploadRequest = Upload request object
        :param extra_rules: Optional[list[BaseRule]] = Set of custom rules
            constructed by the user. The rules will be applied before the
            upload flow.
        :param config: Optional[UploadConfig] = Configuration for upload process
        :param extra_steps_before: Optional[Sequence[BaseStep]] = Additional
            custom steps executed before the built-in upload pipeline
        :param extra_steps_after: Optional[Sequence[BaseStep]] = Additional
            custom steps executed after the built-in upload pipeline

        :return: FileUploadResult = Upload result metadata

        :raises ValidationError:
            When request is invalid
        :raises FileFlowError:
            When the upload flow fails in a domain-specific way
        :raises WorkflowError:
            When rule execution or step execution fails at workflow level
        :raises RequestError:
            When a lower-level transport or API failure bubbles up

        :example:
            >>> callable(FileService.uploadFile)
            True
        """
        class_name, method_name = getExceptionContext(self)

        if not isinstance(request, FileUploadRequest):
            raise ValidationError(
                "request must be a FileUploadRequest instance", class_name, method_name
            )

        return self._upload_flow.execute(
            request=request,
            extra_rules=extra_rules,
            config=config,
            extra_steps_before=extra_steps_before,
            extra_steps_after=extra_steps_after,
        )

    # ============================================================
    # Download
    # ============================================================

    def downloadAllAttachments(self, request: FileDownloadRequest) -> List[Path]:
        """
        Downloads all attachments from a Pipefy card field.

        This method retrieves file URLs from the specified card field,
        downloads each file, and saves them locally.

        :param request: FileDownloadRequest = Download request object

        :return: list[Path] = List of saved file paths

        :raises ValidationError:
            When request is invalid
        :raises FileDownloadError:
            When attachment parsing or binary download fails
        :raises RequestError:
            When a lower-level transport or API failure bubbles up

        :example:
            >>> callable(FileService.downloadAllAttachments)
            True
        """
        class_name, method_name = getExceptionContext(self)

        if not isinstance(request, FileDownloadRequest):
            raise ValidationError(
                "request must be a FileDownloadRequest instance",
                class_name,
                method_name,
            )

        return self._download_flow.execute(request)


# ============================================================
# MAIN TEST
# ============================================================
if __name__ == "__main__":
    print("FileService (enterprise request-based API) ready")
