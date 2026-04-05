# ============================================================
# Dependencies
# ============================================================

from pipebridge.client.httpClient import PipefyHttpClient
from pipebridge.exceptions import ValidationError
from pipebridge.exceptions.core.utils import getExceptionContext
from pipebridge.service.card.cardService import CardService
from pipebridge.integrations.file.fileIntegration import FileIntegration


class FileServiceContext:
    """
    Encapsulates all dependencies required by file operations.

    This object centralizes infrastructure dependencies and ensures
    consistent injection across flows and services.

    :param client: PipefyHttpClient = GraphQL HTTP client
    :param card_service: CardService = Card operations service
    :param file_integration: FileIntegration = Storage integration layer

    :raises ValidationError:
        When any dependency is None

    :example:
        >>> callable(FileServiceContext)
        True
    """

    def __init__(
        self,
        client: PipefyHttpClient,
        card_service: CardService,
        file_integration: FileIntegration,
    ) -> None:
        """
        Initialize the file service dependency container.

        :param client: PipefyHttpClient = HTTP client
        :param card_service: CardService = Card domain service
        :param file_integration: FileIntegration = Binary transfer integration

        :raises ValidationError:
            When any dependency is ``None``
        """
        class_name, method_name = getExceptionContext(self)

        if client is None:
            raise ValidationError("client must not be None", class_name, method_name)

        if card_service is None:
            raise ValidationError(
                "card_service must not be None", class_name, method_name
            )

        if file_integration is None:
            raise ValidationError(
                "file_integration must not be None", class_name, method_name
            )

        self.client = client
        self.card_service = card_service
        self.file_integration = file_integration
