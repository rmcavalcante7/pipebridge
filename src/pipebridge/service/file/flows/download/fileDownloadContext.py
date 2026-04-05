# ============================================================
# Dependencies
# ============================================================
from pipebridge.integrations.file.fileIntegration import FileIntegration
from pipebridge.service.card.cardService import CardService


class FileDownloadContext:
    """
    Dependency container for file download flows.

    :param card_service: CardService = Card service used to read card state
    :param file_integration: FileIntegration = Binary download integration

    :example:
        >>> callable(FileDownloadContext)
        True
    """

    def __init__(
        self, card_service: CardService, file_integration: FileIntegration
    ) -> None:
        """
        Initialize FileDownloadContext.

        :param card_service: CardService = Card service used to read card state
        :param file_integration: FileIntegration = Binary download integration

        :return: None

        :example:
            >>> callable(FileDownloadContext)
            True
        """
        self.card_service = card_service
        self.file_integration = file_integration
