# ============================================================
# Dependencies
# ============================================================
from pathlib import Path
from typing import List

from pipefy.client.httpClient import PipefyHttpClient
from pipefy.service.cardService import CardService
from pipefy.exceptions import ValidationError, getExceptionContext
from pipefy.integrations.file.fileService import FileService as IntegrationFileService
from pipefy.integrations.file.fileUploadResult import FileUploadResult


class FileService:
    """
    Service responsible for file operations in Pipefy.

    This class acts as an orchestration layer between the application
    services and the file integration layer.

    It delegates file upload and download operations to the integration
    FileService while preserving backward compatibility.

    :param client: PipefyHttpClient = HTTP client instance
    :param card_service: CardService = Card service instance

    :raises ValidationError:
        When dependencies are invalid

    :example:
        >>> from pipefy.client.httpClient import PipefyHttpClient
        >>> from pipefy.service.cardService import CardService
        >>> client = PipefyHttpClient("token", "https://api.pipefy.com/graphql")
        >>> card_service = CardService(client)
        >>> service = FileService(client, card_service)
        >>> isinstance(service, FileService)
        True
    """

    def __init__(
        self,
        client: PipefyHttpClient,
        card_service: CardService
    ) -> None:
        """
        Initializes FileService.

        :param client: PipefyHttpClient = HTTP client instance
        :param card_service: CardService = Card service instance

        :raises ValidationError:
            When dependencies are invalid
        """
        class_name, method_name = getExceptionContext(self)

        if client is None:
            raise ValidationError(
                message="client must not be None",
                class_name=class_name,
                method_name=method_name
            )

        if card_service is None:
            raise ValidationError(
                message="card_service must not be None",
                class_name=class_name,
                method_name=method_name
            )

        self._client = client
        self._card_service = card_service
        self._integration_service = IntegrationFileService(client, card_service)

    # ============================================================
    # Upload
    # ============================================================

    def uploadFile(
        self,
        file_name: str,
        file_bytes: bytes,
        card_id: str,
        field_id: str,
        organization_id: int,
        replace_files: bool = False
    ) -> FileUploadResult:
        """
        Upload a file and attach it to a card field.

        This method delegates the upload workflow to the integration layer
        and returns only the success status for backward compatibility.

        :param file_name: str = File name
        :param file_bytes: bytes = File content
        :param card_id: str = Card identifier
        :param field_id: str = Field identifier
        :param organization_id: int = Organization ID
        :param replace_files: bool = If True, replaces all existing attachments.
                              If False, appends to existing attachments.

        :return: FileUploadResult = Upload result with status and details

        :raises ValidationError:
            When input parameters are invalid
        :raises UnexpectedResponseError:
            When API response structure is invalid
        :raises RequestError:
            When upload fails

        :example:
            >>> from pipefy.client.httpClient import PipefyHttpClient
            >>> from pipefy.service.cardService import CardService
            >>> client = PipefyHttpClient("token", "https://api.pipefy.com/graphql")
            >>> service = FileService(client, CardService(client))
            >>> callable(service.uploadFile)
            True
        """
        result = self._integration_service.uploadFile(
            file_name=file_name,
            file_bytes=file_bytes,
            card_id=card_id,
            field_id=field_id,
            organization_id=organization_id,
            replace_files=replace_files
        )

        return result

    # ============================================================
    # Download
    # ============================================================

    def downloadAllAttachments(
        self,
        card_id: str,
        field_id: str,
        output_dir: str
    ) -> List[Path]:
        """
        Download all attachments from a card and save them locally.

        This method delegates the download operation to the integration
        layer and handles local file persistence.

        :param card_id: str = Card identifier
        :param output_dir: str = Output directory path

        :return: list[Path] = List of saved file paths

        :raises ValidationError:
            When input parameters are invalid
        :raises RequestError:
            When download fails

        :example:
            >>> from pipefy.client.httpClient import PipefyHttpClient
            >>> from pipefy.service.cardService import CardService
            >>> client = PipefyHttpClient("token", "https://api.pipefy.com/graphql")
            >>> service = FileService(client, CardService(client))
            >>> callable(service.downloadAllAttachments)
            True
        """
        class_name, method_name = getExceptionContext(self)

        if not output_dir or not isinstance(output_dir, str):
            raise ValidationError(
                message="output_dir must be a valid string",
                class_name=class_name,
                method_name=method_name
            )

        files = self._integration_service.downloadAllAttachments(card_id=card_id, field_id=field_id)

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        saved_files: List[Path] = []

        for file_name, content in files.items():
            file_path = output_path / file_name

            file_path.write_bytes(content)
            saved_files.append(file_path)

        return saved_files