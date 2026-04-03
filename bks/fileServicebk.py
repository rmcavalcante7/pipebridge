# ============================================================
# Dependencies
# ============================================================
import re
import inspect
from typing import Any, Dict

import requests

from pipefy.client.httpClient import PipefyHttpClient
from pipefy.service.cardService import CardService
from pipefy.exceptions import RequestError
from pathlib import Path
from typing import List


class FileService:
    """
    Service responsible for file upload operations in Pipefy.

    This service handles file-related workflows including:
    - Generating presigned upload URLs
    - Uploading binary content to Pipefy storage
    - Linking uploaded files to cards via fields

    It orchestrates:
    - HTTP client (GraphQL communication)
    - CardService (field updates)

    :example:
        >>> client = PipefyHttpClient("token")
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
        Initialize FileService.

        :param client: PipefyHttpClient = HTTP client instance
        :param card_service: CardService = Card service instance

        :example:
            >>> client = PipefyHttpClient("token")
            >>> card_service = CardService(client)
            >>> service = FileService(client, card_service)
        """
        self._client: PipefyHttpClient = client
        self._card_service: CardService = card_service

    # ============================================================
    # File Upload
    # ============================================================

    def uploadFile(
        self,
        file_name: str,
        file_bytes: bytes,
        card_id: str,
        field_id: str,
        organization_id: int
    ) -> bool:
        """
        Upload a file and attach it to a card field.

        This method performs a multi-step workflow:
        1. Requests a presigned upload URL from Pipefy
        2. Uploads the file using HTTP PUT
        3. Extracts the stored file path
        4. Updates the card field with the uploaded file reference

        :param file_name: str = Name of the file (including extension)
        :param file_bytes: bytes = Binary content of the file
        :param card_id: str = Target card ID
        :param field_id: str = Field ID to attach the file
        :param organization_id: int = Pipefy organization ID

        :return: bool = True if upload and attachment succeed

        :raises RequestError:
            When any step of the upload process fails
        :raises RequestError:
            When API response structure is invalid

        :example:
            >>> client = PipefyHttpClient("token")
            >>> card_service = CardService(client)
            >>> service = FileService(client, card_service)
            >>> isinstance(service, FileService)
            True
        """
        try:
            # ====================================================
            # Step 1: Generate presigned URL
            # ====================================================
            query = f"""
            mutation {{
                createPresignedUrl(input: {{
                    fileName: "{file_name}",
                    organizationId: {organization_id}
                }}) {{
                    url
                    downloadUrl
                }}
            }}
            """

            response: Dict[str, Any] = self._client.sendRequest(query, timeout=60)

            try:
                url_put: str = response["data"]["createPresignedUrl"]["url"]
                download_url: str = response["data"]["createPresignedUrl"]["downloadUrl"]
            except KeyError as exc:
                raise RequestError(
                    f"Class: {self.__class__.__name__}\n"
                    f"Method: uploadFile\n"
                    f"Error: Invalid API response structure"
                ) from exc

            # ====================================================
            # Step 2: Upload file to storage
            # ====================================================
            headers = {
                "Content-Type": f"application/{file_name.split('.')[-1]}"
            }

            upload_response = requests.put(
                url_put,
                data=file_bytes,
                headers=headers,
                timeout=60
            )

            if upload_response.status_code not in (200, 201):
                raise RequestError(
                    f"Class: {self.__class__.__name__}\n"
                    f"Method: uploadFile\n"
                    f"Error: Upload failed with status {upload_response.status_code}"
                )

            # ====================================================
            # Step 3: Extract file path
            # ====================================================
            match = re.findall(r'(orgs.+)\?', download_url)

            if not match:
                raise RequestError(
                    f"Class: {self.__class__.__name__}\n"
                    f"Method: uploadFile\n"
                    f"Error: Could not extract file path from download URL"
                )

            file_path: str = match[0]

            # ====================================================
            # Step 4: Attach file to card
            # ====================================================
            result: Dict[str, Any] = self._card_service.updateFields(
                card_id,
                [[field_id, file_path]]
            )

            try:
                return result["data"]["updateFieldsValues"]["success"]
            except KeyError as exc:
                raise RequestError(
                    f"Class: {self.__class__.__name__}\n"
                    f"Method: uploadFile\n"
                    f"Error: Invalid response when attaching file to card"
                ) from exc

        except Exception as exc:
            raise RequestError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: uploadFile\n"
                f"Error: {str(exc)}"
            ) from exc

    # ============================================================
    # File Download
    # ============================================================



    def downloadAllAttachments(
            self,
            card_id: str,
            output_dir: str
    ) -> List[Path]:
        """
        Download all attachments from a card.

        This method:
        - Retrieves card attachments via CardService
        - Downloads each file using its URL
        - Saves files locally into the specified directory

        :param card_id: str = Card ID
        :param output_dir: str = Directory path to save files

        :return: list[Path] = List of saved file paths

        :raises RequestError:
            When card retrieval fails
        :raises RequestError:
            When download fails
        :raises RequestError:
            When response structure is invalid

        :example:
            >>> client = PipefyHttpClient("token")
            >>> card_service = CardService(client)
            >>> service = FileService(client, card_service)
            >>> service = FileService(client, card_service)
            >>> isinstance(service, FileService)
            True
        """
        try:
            # ====================================================
            # Step 1: Retrieve card with attachments
            # ====================================================
            response: Dict[str, Any] = self._card_service.getCardStructured(card_id, attributes=["attachments"])

            try:
                attachments = response["data"]["card"]["attachments"]
            except KeyError as exc:
                raise RequestError(
                    f"Class: {self.__class__.__name__}\n"
                    f"Method: downloadAllAttachments\n"
                    f"Error: Invalid response structure when retrieving attachments"
                ) from exc

            # ====================================================
            # Step 2: Prepare output directory
            # ====================================================
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            downloaded_files: List[Path] = []

            # ====================================================
            # Step 3: Download each file
            # ====================================================
            for attachment in attachments:
                file_url = attachment.get("url")

                if not file_url:
                    continue

                file_name = file_url.split("/")[-1].split("?")[0]
                file_path = output_path / file_name

                response = requests.get(file_url, timeout=60)

                if response.status_code != 200:
                    raise RequestError(
                        f"Class: {self.__class__.__name__}\n"
                        f"Method: downloadAllAttachments\n"
                        f"Error: Failed to download file ({response.status_code})"
                    )

                file_path.write_bytes(response.content)
                downloaded_files.append(file_path)

            return downloaded_files

        except Exception as exc:
            raise RequestError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: downloadAllAttachments\n"
                f"Error: {str(exc)}"
            ) from exc

# ============================================================
# Main (Usage Example)
# ============================================================

if __name__ == "__main__":
    """
    Simple execution example.
    """

    try:
        TOKEN = ""
        client = PipefyHttpClient(TOKEN)
        card_service = CardService(client)
        file_service = FileService(client, card_service)

        result = file_service.downloadAllAttachments(
            card_id="35850877",
            output_dir="./tmp"
        )

        print("Upload success:", result)

    except Exception as error:
        print("Error occurred:")
        print(error)