# ============================================================
# Dependencies
# ============================================================
import json
from typing import Dict, Any, Optional

from pipefy.client.httpClient import PipefyHttpClient
from pipefy.exceptions import RequestError, ValidationError, UnexpectedResponseError
from pipefy.exceptions.utils import getExceptionContext
from pipefy.service.cardService import CardService
from pipefy.integrations.file.fileUploadResult import FileUploadResult
from pipefy.integrations.file.fileIntegration import FileIntegration

from urllib.parse import urlparse


class FileService:
    """
    Service responsible for file upload and download operations.

    This service orchestrates the full lifecycle of file handling in Pipefy,
    including:

    - Generating presigned URLs via GraphQL
    - Uploading files to external storage (e.g., S3)
    - Attaching uploaded files to card fields
    - Downloading attachments from cards

    This class acts as an orchestration layer and delegates low-level
    HTTP operations to FileIntegration.

    :param client: PipefyHttpClient = HTTP client used for GraphQL operations
    :param card_service: CardService = Service responsible for card operations

    :raises ValidationError:
        When dependencies are not provided

    :example:
        >>> from pipefy.client.httpClient import PipefyHttpClient
        >>> from pipefy.service.cardService import CardService
        >>> client = PipefyHttpClient(auth_key="token", base_url="https://api.pipefy.com/graphql")
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
        Initializes the FileService.

        :param client: PipefyHttpClient = HTTP client instance
        :param card_service: CardService = Card service dependency

        :raises ValidationError:
            When client or card_service is None

        :example:
            >>> from pipefy.client.httpClient import PipefyHttpClient
            >>> from pipefy.service.cardService import CardService
            >>> client = PipefyHttpClient(auth_key="token", base_url="https://api.pipefy.com/graphql")
            >>> card_service = CardService(client)
            >>> service = FileService(client, card_service)
            >>> isinstance(service, FileService)
            True
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
        self._file_integration = FileIntegration()

    # ============================================================
    # PRIVATE METHODS
    # ============================================================

    def _createPresignedUrl(
            self,
            file_name: str,
            organization_id: str
    ) -> Dict[str, Any]:
        """
        Generates a presigned URL for uploading a file.

        This method performs a GraphQL mutation to retrieve a presigned URL
        and a corresponding download URL from Pipefy.

        :param file_name: str = Name of the file to upload
        :param organization_id: int = Organization identifier

        :return: dict = Raw GraphQL response containing upload and download URLs

        :raises ValidationError:
            When file_name is empty
        :raises ValidationError:
            When organization_id is not an integer
        :raises RequestError:
            When request execution fails

        :example:
            >>> from pipefy.client.httpClient import PipefyHttpClient
            >>> from pipefy.service.cardService import CardService
            >>> client = PipefyHttpClient(auth_key="token", base_url="https://api.pipefy.com/graphql")
            >>> service = FileService(client, CardService(client))
            >>> callable(service._createPresignedUrl)
            True
        """
        class_name, method_name = getExceptionContext(self)

        if not file_name:
            raise ValidationError(
                message="file_name cannot be empty",
                class_name=class_name,
                method_name=method_name
            )

        if not isinstance(organization_id, str):
            raise ValidationError(
                message="organization_id must be an integer",
                class_name=class_name,
                method_name=method_name
            )

        try:
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

            return self._client.sendRequest(query, timeout=60)

        except Exception as exc:
            raise RequestError(
                message=str(exc),
                class_name=class_name,
                method_name=method_name
            ) from exc

    def _uploadToStorage(
            self,
            url: str,
            file_bytes: bytes
    ) -> None:
        """
        Uploads a file to external storage using a presigned URL.

        This method delegates the upload operation to FileIntegration.

        :param url: str = Presigned upload URL
        :param file_bytes: bytes = File content

        :return: None

        :raises RequestError:
            When upload fails

        :example:
            >>> from pipefy.client.httpClient import PipefyHttpClient
            >>> from pipefy.service.cardService import CardService
            >>> client = PipefyHttpClient(auth_key="token", base_url="https://api.pipefy.com/graphql")
            >>> service = FileService(client, CardService(client))
            >>> callable(service._uploadToStorage)
            True
        """
        self._file_integration.upload(url, file_bytes)

    def _extractFilePath(self, upload_url: str) -> str:
        """
        Extracts the file path from a presigned upload URL.

        Removes query parameters and returns the clean URL.

        :param upload_url: str = Presigned upload URL

        :return: str = Clean file path

        :raises RequestError:
            When extraction fails

        :example:
            >>> from pipefy.client.httpClient import PipefyHttpClient
            >>> from pipefy.service.cardService import CardService
            >>> client = PipefyHttpClient(auth_key="token", base_url="https://api.pipefy.com/graphql")
            >>> service = FileService(client, CardService(client))
            >>> callable(service._extractFilePath)
            True
        """
        return self._file_integration.extractFilePath(upload_url)

    def _attachToCard(
            self,
            card_id: str,
            field_id: str,
            files_path: list[str],
    ) -> None:
        """
        Updates attachment field using Pipefy simplified mutation.

        This method sends the final state of attachments to Pipefy using
        `updateCardField`. The API expects a full list of file paths.

        IMPORTANT:
            - Pipefy replaces all attachments with the provided list
            - No incremental operations exist (add/remove)

        :param card_id: str = Card identifier
        :param field_id: str = Logical field identifier
        :param files_path: list[str] = Final list of file paths

        :return: None

        :raises ValidationError:
            When input parameters are invalid
        :raises RequestError:
            When API request fails

        :example:
            >>> from pipefy.client.httpClient import PipefyHttpClient
            >>> from pipefy.service.cardService import CardService
            >>> client = PipefyHttpClient(auth_key="token", base_url="https://api.pipefy.com/graphql")
            >>> service = FileService(client, CardService(client))
            >>> callable(service._attachToCard)
            True
        """

        class_name, method_name = getExceptionContext(self)

        # --------------------------------------------------------
        # Validation
        # --------------------------------------------------------
        if not card_id:
            raise ValidationError(
                message="card_id cannot be empty",
                class_name=class_name,
                method_name=method_name
            )

        if not field_id:
            raise ValidationError(
                message="field_id cannot be empty",
                class_name=class_name,
                method_name=method_name
            )

        if not files_path:
            raise ValidationError(
                message="file_path cannot be empty",
                class_name=class_name,
                method_name=method_name
            )

        try:
            mutation = f"""
            mutation {{
              updateCardField(input: {{
                card_id: "{card_id}",
                field_id: "{field_id}",
                new_value: {json.dumps(files_path)}
              }}) {{
                success
                card {{ id }}
              }}
            }}
            """

            self._client.sendRequest(mutation)

        except Exception as exc:
            raise RequestError(
                message=str(exc),
                class_name=class_name,
                method_name=method_name
            ) from exc

    def _getAttachedFiles(self, card_id: str, field_id: str) -> list[str]:
        """
        Retrieves current attachments from a card field.

        This method:
            - Uses CardService to retrieve field values
            - Parses JSON string into Python list
            - Normalizes file paths to relative format

        :param card_id: str = Card identifier
        :param field_id: str = Field identifier

        :return: list[str] = List of relative file paths

        :raises RequestError:
            When parsing fails

        :example:
            >>> callable(FileService._getAttachedFiles)
            True
        """
        card = self._card_service.getCardModel(card_id)

        if field_id not in card.fields_map:
            return []

        raw_value = card.fields_map[field_id].value

        if not raw_value:
            return []

        try:
            urls = json.loads(raw_value)
            if not isinstance(urls, list):
                return []
            return [self._extractFilePath(url) for url in urls]
        except Exception:
            return []

    # ============================================================
    # PUBLIC METHODS
    # ============================================================

    def uploadFile(
            self,
            file_name: str,
            file_bytes: bytes,
            card_id: str,
            field_id: str,
            organization_id: str,
            replace_files: bool = False
    ) -> FileUploadResult:
        """
        Uploads a file and attaches it to a Pipefy card.

        Execution flow:
            1. Generate presigned URL
            2. Upload file to storage
            3. Extract file path
            4. Attach file to card

        :param file_name: str = File name
        :param file_bytes: bytes = File content
        :param card_id: str = Card identifier
        :param field_id: str = Field identifier
        :param organization_id: str = Organization identifier
        :param replace_files: bool = If True, replaces all existing attachments.
                              If False, appends to existing attachments.

        :return: FileUploadResult = Upload result metadata

        :raises ValidationError:
            When input parameters are invalid
        :raises UnexpectedResponseError:
            When API response structure is invalid
        :raises RequestError:
            When upload or attachment fails

        :example:
            >>> from pipefy.client.httpClient import PipefyHttpClient
            >>> from pipefy.service.cardService import CardService
            >>> client = PipefyHttpClient(auth_key="token", base_url="https://api.pipefy.com/graphql")
            >>> card_service = CardService(client)
            >>> service = FileService(client, card_service)
            >>> callable(service.uploadFile)
            True
        """

        class_name, method_name = getExceptionContext(self)

        # --------------------------------------------------------
        # Input validation
        # --------------------------------------------------------
        if not file_name:
            raise ValidationError(
                message="file_name cannot be empty",
                class_name=class_name,
                method_name=method_name
            )

        if not isinstance(file_bytes, bytes):
            raise ValidationError(
                message="file_bytes must be bytes",
                class_name=class_name,
                method_name=method_name
            )

        if not card_id:
            raise ValidationError(
                message="card_id cannot be empty",
                class_name=class_name,
                method_name=method_name
            )

        if not field_id:
            raise ValidationError(
                message="field_id cannot be empty",
                class_name=class_name,
                method_name=method_name
            )

        if not isinstance(organization_id, str):
            raise ValidationError(
                message="organization_id must be an integer",
                class_name=class_name,
                method_name=method_name
            )

        try:
            presigned = self._createPresignedUrl(file_name, organization_id)

            if not isinstance(presigned, dict):
                raise UnexpectedResponseError(
                    message="Presigned response is not a dictionary",
                    class_name=class_name,
                    method_name=method_name
                )

            data = presigned.get("data")
            if not isinstance(data, dict):
                raise UnexpectedResponseError(
                    message="Missing 'data' in presigned response",
                    class_name=class_name,
                    method_name=method_name
                )

            presigned_data = data.get("createPresignedUrl")
            if not isinstance(presigned_data, dict):
                raise UnexpectedResponseError(
                    message="Missing 'createPresignedUrl'",
                    class_name=class_name,
                    method_name=method_name
                )

            upload_url = presigned_data.get("url")
            download_url = presigned_data.get("downloadUrl")

            if not upload_url or not isinstance(upload_url, str):
                raise UnexpectedResponseError(
                    message="Invalid upload URL",
                    class_name=class_name,
                    method_name=method_name
                )

            self._uploadToStorage(upload_url, file_bytes)

            file_path = self._extractFilePath(upload_url)
            attchaed_files = [file_path]
            if not replace_files:
                attchaed_files += self._getAttachedFiles(card_id=card_id, field_id=field_id)

            if not attchaed_files:
                raise UnexpectedResponseError(
                    message="Failed to extract file path",
                    class_name=class_name,
                    method_name=method_name
                )

            # final_files = []
            # for path in attchaed_files:
            #     final_files.append(self.normalizePaths(path))

            self._attachToCard(card_id=card_id, field_id=field_id, files_path=attchaed_files)

            return FileUploadResult(
                file_path=attchaed_files,
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

    def downloadAllAttachments(
            self,
            card_id: str,
            field_id: str,
            timeout: int = 60
    ) -> Dict[str, bytes]:
        """
        Downloads all attachments from a card field.

        This method retrieves attachment URLs from the card field,
        downloads each file, and returns a mapping of file name to content.

        :param card_id: str = Card identifier
        :param field_id: str = Field identifier
        :param timeout: int = Request timeout in seconds

        :return: dict[str, bytes] = Mapping of file name to file content

        :raises ValidationError:
            When parameters are invalid
        :raises UnexpectedResponseError:
            When field is missing or invalid
        :raises RequestError:
            When download fails

        :example:
            >>> callable(FileService.downloadAllAttachments)
            True
        """
        class_name, method_name = getExceptionContext(self)

        if not card_id:
            raise ValidationError(
                message="card_id cannot be empty",
                class_name=class_name,
                method_name=method_name
            )

        if not field_id:
            raise ValidationError(
                message="field_id cannot be empty",
                class_name=class_name,
                method_name=method_name
            )

        if not isinstance(timeout, int) or timeout <= 0:
            raise ValidationError(
                message="timeout must be a positive integer",
                class_name=class_name,
                method_name=method_name
            )

        try:
            card = self._card_service.getCardModel(card_id)

            if field_id not in card.fields_map:
                raise UnexpectedResponseError(
                    message=f"Field '{field_id}' not found in card",
                    class_name=class_name,
                    method_name=method_name
                )

            raw_value = card.fields_map[field_id].value

            if not raw_value:
                return {}

            attachments = json.loads(raw_value)

            if not isinstance(attachments, list):
                raise UnexpectedResponseError(
                    message="'attachments' must be a list",
                    class_name=class_name,
                    method_name=method_name
                )

            files: Dict[str, bytes] = {}

            for url in attachments:

                if not isinstance(url, str):
                    continue

                file_name = self.extractFileName(url)

                files[file_name] = self._file_integration.download(
                    url,
                    timeout=timeout
                )

            return files

        except (ValidationError, RequestError, UnexpectedResponseError):
            raise

        except Exception as exc:
            raise RequestError(
                message=str(exc),
                class_name=class_name,
                method_name=method_name
            ) from exc

    def downloadAllAttachmentsbk(
        self,
        card_id: str,
        field_id: str,
        timeout: int = 60
    ) -> Dict[str, bytes]:

        class_name, method_name = getExceptionContext(self)

        if not card_id:
            raise ValidationError(
                message="card_id cannot be empty",
                class_name=class_name,
                method_name=method_name
            )

        if not isinstance(timeout, int) or timeout <= 0:
            raise ValidationError(
                message="timeout must be a positive integer",
                class_name=class_name,
                method_name=method_name
            )

        try:

            card = self._card_service.getCardModel(card_id)
            if field_id not in card.fields_map:
                raise UnexpectedResponseError(
                    message=f"Field '{field_id}' not found in card",
                    class_name=class_name,
                    method_name=method_name
                )

            attachments = json.loads(card.fields_map[field_id].value)

            if attachments is None:
                raise UnexpectedResponseError(
                    message="Missing 'attachments'",
                    class_name=class_name,
                    method_name=method_name
                )

            if not isinstance(attachments, list):
                raise UnexpectedResponseError(
                    message="'attachments' must be a list",
                    class_name=class_name,
                    method_name=method_name
                )

            files: Dict[str, bytes] = {}

            for attachment in attachments:

                if not isinstance(attachment, str):
                    continue

                # url = attachment.get("url")
                url = attachment

                if not url or not isinstance(url, str):
                    continue

                files[self.extractFileName(url)] = self._file_integration.download(url, timeout=timeout)

            return files

        except (ValidationError, RequestError, UnexpectedResponseError):
            raise

        except Exception as exc:
            raise RequestError(
                message=str(exc),
                class_name=class_name,
                method_name=method_name
            ) from exc

    def extractFileName(self, url: str) -> str:
        """
        Extracts file name from a signed URL.

        :param url: str = Signed URL

        :return: str = File name

        :raises ValidationError:
            When URL is invalid

        :example:
            >>> callable(FileService.extractFileName)
            True
        """
        class_name, method_name = getExceptionContext(self)

        if not url or not isinstance(url, str):
            raise ValidationError(
                message="url must be a non-empty string",
                class_name=class_name,
                method_name=method_name
            )

        path = urlparse(url).path
        return path.split("/")[-1]

    def normalizePaths(self, paths: list, organization_id: str) -> list:
        """
        Normalizes file paths to ensure Pipefy compatibility.

        This method ensures all paths follow the format:

            orgs/{organization_id}/uploads/...

        :param paths: list[str] = List of file paths
        :param organization_id: str = Organization identifier

        :return: list[str] = Normalized file paths

        :example:
            >>> callable(FileService.normalizePaths)
            True
        """
        normalized = []
        prefix = f"orgs/{organization_id}/"

        for path in paths:
            # Se já começa com 'orgs/', mantém como está
            if path.startswith("orgs/"):
                normalized.append(path)
            # Se começa com 'uploads/', adiciona o prefixo da org
            elif path.startswith("uploads/"):
                normalized.append(f"{prefix}{path}")
            else:
                # Caso venha um path inesperado, tenta limpar e prefixar
                clean_path = path.split("signed/")[-1]
                normalized.append(f"{prefix}{clean_path}" if not clean_path.startswith("orgs/") else clean_path)

        return normalized