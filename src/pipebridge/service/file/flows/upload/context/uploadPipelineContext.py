# ============================================================
# Dependencies
# ============================================================
from typing import List, Optional

from pipebridge.service.card.cardService import CardService
from pipebridge.models.file.fileUploadRequest import FileUploadRequest
from pipebridge.integrations.file.fileIntegration import FileIntegration
from pipebridge.client.httpClient import PipefyHttpClient
from pipebridge.service.file.flows.upload.config.uploadConfig import UploadConfig
from pipebridge.workflow.context.executionContext import ExecutionContext


# ============================================================
# UploadPipelineContext
# ============================================================
class UploadPipelineContext(ExecutionContext):
    """
    Strongly-typed context object for upload pipeline execution.

    This class replaces unstructured dictionaries used in pipeline steps,
    providing:

        - Type safety
        - Explicit contract
        - Better maintainability
        - Easier documentation
        - IDE support (autocomplete)

    This object is shared across all pipeline steps and is mutable
    by design, allowing each step to enrich or transform the state.

    :param request: FileUploadRequest = Upload request object
    :param client: PipefyHttpClient = GraphQL client
    :param integration: FileIntegration = Storage integration
    :param upload_url: str = Presigned upload URL
    :param download_url: Optional[str] = Download URL returned by API
    :param files: list[str] = List of normalized file paths

    :example:
        >>> callable(UploadPipelineContext)
        True
    """

    def __init__(
        self,
        request: FileUploadRequest,
        client: PipefyHttpClient,
        integration: FileIntegration,
        card_service: CardService,
        config: UploadConfig,
        upload_url: Optional[str] = None,
        download_url: Optional[str] = None,
        files: Optional[List[str]] = None,
    ) -> None:
        """
        Initialize UploadPipelineContext.

        :param request: FileUploadRequest = Upload request object
        :param client: PipefyHttpClient = GraphQL client
        :param integration: FileIntegration = Storage integration
        :param card_service: CardService = Card service used by upload steps
        :param config: UploadConfig = Upload execution policy configuration
        :param upload_url: Optional[str] = Presigned upload URL
        :param download_url: Optional[str] = Download URL returned by API
        :param files: Optional[List[str]] = Normalized file paths

        :return: None

        :example:
            >>> callable(UploadPipelineContext)
            True
        """
        super().__init__(metadata={"flow": "upload"})
        self.request = request
        self.client = client
        self.card_service = card_service
        self.config = config
        self.integration = integration
        self.upload_url = upload_url
        self.download_url = download_url
        self.files: List[str] = files or []
