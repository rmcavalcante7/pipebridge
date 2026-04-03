# ============================================================
# Dependencies
# ============================================================
from typing import List, Optional

from pipefy import CardService
from pipefy.models.file.fileUploadRequest import FileUploadRequest
from pipefy.integrations.file.fileIntegration import FileIntegration
from pipefy.client.httpClient import PipefyHttpClient


# ============================================================
# UploadPipelineContext
# ============================================================
class UploadPipelineContext:
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
        upload_url: str,
        download_url: Optional[str] = None,
        files: Optional[List[str]] = None
    ) -> None:
        self.request = request
        self.client = client
        self.card_service = card_service
        self.integration = integration
        self.upload_url = upload_url
        self.download_url = download_url
        self.files: List[str] = files or []