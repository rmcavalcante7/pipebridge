# ============================================================
# Dependencies
# ============================================================
import json

import requests

from pipefy.exceptions import RequestError, ValidationError
from pipefy.exceptions.utils import getExceptionContext


class FileIntegration:
    """
    Handles low-level file operations with external storage.

    This class is responsible for direct HTTP interactions with storage
    services (e.g., S3), including:

    - Uploading files using presigned URLs
    - Downloading files from URLs
    - Extracting file paths from URLs

    This class does NOT contain business logic related to Pipefy.

    :example:
        >>> integration = FileIntegration()
        >>> callable(integration.upload)
        True
    """

    # ============================================================
    # Public Methods
    # ============================================================

    def upload(
        self,
        url: str,
        file_bytes: bytes,
        timeout: int = 60
    ) -> None:
        """
        Uploads a file to external storage using a presigned URL.

        :param url: str = Presigned upload URL
        :param file_bytes: bytes = File content
        :param timeout: int = Timeout in seconds

        :return: None

        :raises ValidationError:
            When input parameters are invalid
        :raises RequestError:
            When HTTP request fails or returns invalid status

        :example:
            >>> integration = FileIntegration()
            >>> callable(integration.upload)
            True
        """
        class_name, method_name = getExceptionContext(self)

        # --------------------------------------------------------
        # Input validation
        # --------------------------------------------------------
        if not url or not isinstance(url, str):
            raise ValidationError(
                message="url must be a non-empty string",
                class_name=class_name,
                method_name=method_name
            )

        if not isinstance(file_bytes, bytes):
            raise ValidationError(
                message="file_bytes must be bytes",
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
            response = requests.put(url, data=file_bytes, timeout=timeout)

            if response.status_code not in (200, 201):
                raise RequestError(
                    message=f"Upload failed with status {response.status_code}",
                    class_name=class_name,
                    method_name=method_name
                )

        except RequestError:
            raise

        except Exception as exc:
            raise RequestError(
                message=str(exc),
                class_name=class_name,
                method_name=method_name
            ) from exc

    def download(
        self,
        url: str,
        timeout: int = 60
    ) -> bytes:
        """
        Downloads a file from external storage.

        :param url: str = File URL
        :param timeout: int = Timeout in seconds

        :return: bytes = File content

        :raises ValidationError:
            When input parameters are invalid
        :raises RequestError:
            When HTTP request fails or returns invalid status

        :example:
            >>> integration = FileIntegration()
            >>> callable(integration.download)
            True
        """
        class_name, method_name = getExceptionContext(self)

        # --------------------------------------------------------
        # Input validation
        # --------------------------------------------------------
        if not url or not isinstance(url, str):
            raise ValidationError(
                message="url must be a non-empty string",
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
            response = requests.get(url, timeout=timeout)

            if response.status_code != 200:
                raise RequestError(
                    message=f"Download failed with status {response.status_code}",
                    class_name=class_name,
                    method_name=method_name
                )

            return response.content

        except RequestError:
            raise

        except Exception as exc:
            raise RequestError(
                message=str(exc),
                class_name=class_name,
                method_name=method_name
            ) from exc

    def extractFilePath(self, upload_url: str) -> str:
        """
        Normalizes file path to Pipefy required format.

        This method converts different URL formats into the canonical
        Pipefy path format:

            orgs/{organization_id}/uploads/{uuid}/{filename}

        Supported inputs:
            - Full URLs (with domain and query params)
            - Signed URLs (with query parameters)
            - Relative paths (already normalized)

        :param upload_url: str = Presigned upload or download URL

        :return: str = Normalized relative file path

        :raises ValidationError:
            When upload_url is invalid
        :raises RequestError:
            When normalization fails

        :example:
            >>> integration = FileIntegration()
            >>> path = integration.extractFilePath("https://host/storage/v1/signed/orgs/x/uploads/file.txt?token=abc")
            >>> "uploads/" in path
            True
        """
        class_name, method_name = getExceptionContext(self)

        ORG_ID = "c74580a4-6f84-48c1-b432-836eaed711b2"

        if not upload_url or not isinstance(upload_url, str):
            raise ValidationError(
                message="upload_url must be a non-empty string",
                class_name=class_name,
                method_name=method_name
            )

        try:
            clean_path = upload_url.split("?")[0]

            if "orgs/" in clean_path:
                return "orgs/" + clean_path.split("orgs/")[-1]

            if "uploads/" in clean_path:
                uuid_path = "uploads/" + clean_path.split("uploads/")[-1]
                return f"orgs/{ORG_ID}/{uuid_path}"

            return clean_path.split(".com/")[-1]

        except Exception as exc:
            raise RequestError(
                message=str(exc),
                class_name=class_name,
                method_name=method_name
            ) from exc

    def extractFilePathbk(self, upload_url: str) -> str:
        """
        Extracts the relative file path from a presigned upload URL.

        This method performs the following transformations:
            1. Removes query parameters (?token, etc.)
            2. Removes domain portion if present
            3. Removes storage prefix (e.g., 'storage/v1/signed/')
            4. Returns a relative path compatible with Pipefy API

        Example transformation:
            https://host/storage/v1/signed/uploads/abc/file.txt?token=123
            → uploads/abc/file.txt

        :param upload_url: str = Presigned upload URL

        :return: str = Relative file path (e.g., uploads/...)

        :raises ValidationError:
            When upload_url is invalid
        :raises RequestError:
            When parsing fails

        :example:
            >>> integration = FileIntegration()
            >>> integration.extractFilePath("https://host/storage/v1/signed/uploads/file.txt?token=abc")
            'uploads/file.txt'
        """
        class_name, method_name = getExceptionContext(self)

        if not upload_url or not isinstance(upload_url, str):
            raise ValidationError(
                message="upload_url must be a non-empty string",
                class_name=class_name,
                method_name=method_name
            )

        try:
            clean_url = upload_url.split("?")[0]

            relative_path = clean_url.split(".com/")[-1]

            if "storage/v1/signed/" in relative_path:
                relative_path = relative_path.split("storage/v1/signed/")[-1]

            return relative_path

        except Exception as exc:
            raise RequestError(
                message=(
                    f"Class: {self.__class__.__name__}\n"
                    f"Method: {method_name}\n"
                    f"Failed to process upload URL: {str(exc)}"
                ),
                class_name=class_name,
                method_name=method_name
            ) from exc


# ============================================================
# MAIN TEST
# ============================================================

if __name__ == "__main__":
    """
    Simple execution test.
    """
    integration = FileIntegration()
    print("FileIntegration loaded successfully.")