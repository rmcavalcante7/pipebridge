# ============================================================
# Dependencies
# ============================================================
import re

from typing import Optional
import requests  # type: ignore[import-untyped]

from pipebridge.exceptions import ValidationError
from pipebridge.exceptions.file import FileDownloadError, FileTransferError
from pipebridge.exceptions.transport import (
    ConnectionRequestError,
    TimeoutRequestError,
)
from pipebridge.exceptions.core.utils import getExceptionContext


# ============================================================
# FileIntegration
# ============================================================
class FileIntegration:
    """
    Handles low-level file operations and file path normalization.

    This class is responsible for:

    - Performing HTTP operations with external storage (e.g., S3)
    - Parsing and normalizing file URLs and paths
    - Handling inconsistencies in Pipefy file representations
    - Converting file references into Pipefy-compatible formats

    IMPORTANT:
        This class contains NO business logic related to Pipefy entities.
        It strictly handles infrastructure and data transformation concerns.

    DESIGN DECISION:
        Due to inconsistencies in Pipefy API responses, this class maintains
        an internal transient state (`_last_org_id`) used as a fallback when
        file paths are returned without organization context.

    STATE MANAGEMENT WARNING:
        This class is NOT thread-safe due to internal mutable state.

        It is REQUIRED that each execution flow (e.g., FileUploadFlow)
        uses its own instance of FileIntegration.

        Sharing the same instance across concurrent operations may result
        in incorrect file path normalization due to stale `_last_org_id`.

    SAFE USAGE PATTERN:
        - Instantiate once per flow execution
        - Avoid global/shared instances
        - Optionally call `resetContext()` between operations

    :example:
        >>> integration = FileIntegration()
        >>> callable(integration.upload)
        True
    """

    def __init__(self) -> None:
        """
        Initializes FileIntegration.

        This class maintains an internal fallback state for organization_id
        to handle inconsistent API responses.

        :example:
            >>> integration = FileIntegration()
            >>> integration is not None
            True
        """
        self._last_org_id: Optional[str] = None

    # ============================================================
    # Context Management
    # ============================================================

    def resetContext(self) -> None:
        """
        Resets internal state.

        This method clears the stored organization_id used as fallback.

        It should be used when:
            - Reusing the same instance across operations
            - Ensuring no state leakage between executions

        :return: None

        :example:
            >>> integration = FileIntegration()
            >>> integration.resetContext()
        """
        self._last_org_id = None

    # ============================================================
    # HTTP METHODS
    # ============================================================

    def upload(self, url: str, file_bytes: bytes, timeout: int = 60) -> None:
        """
        Uploads a file to external storage using a presigned URL.

        :param url: str = Presigned upload URL
        :param file_bytes: bytes = File content
        :param timeout: int = Timeout in seconds

        :return: None

        :raises ValidationError:
            When input parameters are invalid

        :raises FileTransferError:
            When HTTP request fails or returns invalid status

        :example:
            >>> integration = FileIntegration()
            >>> callable(integration.upload)
            True
        """
        class_name, method_name = getExceptionContext(self)

        if not url or not isinstance(url, str):
            raise ValidationError(
                message="url must be a non-empty string",
                class_name=class_name,
                method_name=method_name,
            )

        if not isinstance(file_bytes, bytes):
            raise ValidationError(
                message="file_bytes must be bytes",
                class_name=class_name,
                method_name=method_name,
            )

        if not isinstance(timeout, int) or timeout <= 0:
            raise ValidationError(
                message="timeout must be a positive integer",
                class_name=class_name,
                method_name=method_name,
            )

        try:
            response = requests.put(url, data=file_bytes, timeout=timeout)

            if response.status_code not in (200, 201):
                raise FileTransferError(
                    message=f"Upload failed with status {response.status_code}",
                    class_name=class_name,
                    method_name=method_name,
                    retryable=response.status_code >= 500,
                    context={"status_code": response.status_code},
                )

        except FileTransferError:
            raise

        except requests.Timeout as exc:
            raise FileTransferError(
                message=str(exc),
                class_name=class_name,
                method_name=method_name,
                cause=exc,
                retryable=True,
                context={"transport_error": TimeoutRequestError.__name__},
            ) from exc

        except requests.ConnectionError as exc:
            raise FileTransferError(
                message=str(exc),
                class_name=class_name,
                method_name=method_name,
                cause=exc,
                retryable=True,
                context={"transport_error": ConnectionRequestError.__name__},
            ) from exc

        except Exception as exc:
            raise FileTransferError(
                message=str(exc),
                class_name=class_name,
                method_name=method_name,
                cause=exc,
                retryable=getattr(exc, "retryable", False),
            ) from exc

    def download(self, url: str, timeout: int = 60) -> bytes:
        """
        Downloads a file from external storage.

        :param url: str = File URL
        :param timeout: int = Timeout in seconds

        :return: bytes = File content

        :raises ValidationError:
            When input parameters are invalid

        :raises FileDownloadError:
            When HTTP request fails or returns invalid status

        :example:
            >>> integration = FileIntegration()
            >>> callable(integration.download)
            True
        """
        class_name, method_name = getExceptionContext(self)

        if not url or not isinstance(url, str):
            raise ValidationError(
                message="url must be a non-empty string",
                class_name=class_name,
                method_name=method_name,
            )

        if not isinstance(timeout, int) or timeout <= 0:
            raise ValidationError(
                message="timeout must be a positive integer",
                class_name=class_name,
                method_name=method_name,
            )

        try:
            response = requests.get(url, timeout=timeout)

            if response.status_code != 200:
                raise FileDownloadError(
                    message=f"Download failed with status {response.status_code}",
                    class_name=class_name,
                    method_name=method_name,
                    retryable=response.status_code >= 500,
                    context={"status_code": response.status_code},
                )

            return bytes(response.content)

        except FileDownloadError:
            raise

        except requests.Timeout as exc:
            raise FileDownloadError(
                message=str(exc),
                class_name=class_name,
                method_name=method_name,
                cause=exc,
                retryable=True,
                context={"transport_error": TimeoutRequestError.__name__},
            ) from exc

        except requests.ConnectionError as exc:
            raise FileDownloadError(
                message=str(exc),
                class_name=class_name,
                method_name=method_name,
                cause=exc,
                retryable=True,
                context={"transport_error": ConnectionRequestError.__name__},
            ) from exc

        except Exception as exc:
            raise FileDownloadError(
                message=str(exc),
                class_name=class_name,
                method_name=method_name,
                cause=exc,
                retryable=getattr(exc, "retryable", False),
            ) from exc

    # ============================================================
    # Path Utilities
    # ============================================================

    def extractFilePath(self, upload_url: str, org_id: Optional[str] = None) -> str:
        """
        Normalizes file path to Pipefy required format.

        This method converts different URL formats into the canonical
        Pipefy path format:

            orgs/{organization_id}/uploads/{uuid}/{filename}

        BEHAVIOR:
            - Removes query parameters
            - Extracts path component
            - Captures organization_id when available
            - Uses explicit org_id if provided
            - Falls back to internal state when necessary

        PRIORITY ORDER:
            1. Explicit org_id parameter
            2. org_id extracted from URL
            3. Internal fallback (_last_org_id)

        IMPORTANT:
            Pipefy may return inconsistent formats:
                - With orgs/{id}/...
                - Without orgs/ (only uploads/...)

            This method guarantees consistent output.

        :param upload_url: str = Presigned upload or download URL
        :param org_id: Optional[str] = Explicit organization_id override

        :return: str = Normalized relative file path

        :raises ValidationError:
            When upload_url is invalid

        :raises FileTransferError:
            When normalization fails or organization_id cannot be resolved

        :example:
            >>> integration = FileIntegration()
            >>> integration.extractFilePath(
            ...     "https://host/orgs/x/uploads/file.txt"
            ... )
            'orgs/x/uploads/file.txt'
        """
        class_name, method_name = getExceptionContext(self)

        if not upload_url or not isinstance(upload_url, str):
            raise ValidationError(
                message="upload_url must be a non-empty string",
                class_name=class_name,
                method_name=method_name,
            )

        try:
            clean_path = upload_url.split("?")[0]

            # ----------------------------------------------------
            # CASE 1: explicit org_id provided
            # ----------------------------------------------------
            if org_id:
                if "uploads/" not in clean_path:
                    raise FileTransferError(
                        message="Cannot normalize path without uploads/ segment",
                        class_name=class_name,
                        method_name=method_name,
                    )

                relative = "uploads/" + clean_path.split("uploads/")[-1]
                return f"orgs/{org_id}/{relative}"

            # ----------------------------------------------------
            # CASE 2: contains orgs/
            # ----------------------------------------------------
            if "orgs/" in clean_path:
                match = re.search(r"orgs/([^/]+)/", clean_path)

                if not match:
                    raise FileTransferError(
                        message="Failed to extract organization_id from path",
                        class_name=class_name,
                        method_name=method_name,
                    )

                extracted_org_id = match.group(1)
                self._last_org_id = extracted_org_id

                return "orgs/" + clean_path.split("orgs/")[-1]

            # ----------------------------------------------------
            # CASE 3: only uploads/
            # ----------------------------------------------------
            if "uploads/" in clean_path:
                if not self._last_org_id:
                    raise FileTransferError(
                        message="organization_id not available for path normalization",
                        class_name=class_name,
                        method_name=method_name,
                    )

                relative = "uploads/" + clean_path.split("uploads/")[-1]
                return f"orgs/{self._last_org_id}/{relative}"

            # ----------------------------------------------------
            # CASE 4: fallback
            # ----------------------------------------------------
            if ".com/" in clean_path:
                return clean_path.split(".com/")[-1]

            raise FileTransferError(
                message="Unsupported file path format",
                class_name=class_name,
                method_name=method_name,
            )

        except ValidationError, FileTransferError:
            raise

        except Exception as exc:
            raise FileTransferError(
                message=str(exc),
                class_name=class_name,
                method_name=method_name,
                cause=exc,
                retryable=getattr(exc, "retryable", False),
            ) from exc


# ============================================================
# MAIN TEST
# ============================================================
if __name__ == "__main__":
    """
    Simple execution test demonstrating behavior.
    """
    integration = FileIntegration()

    url = (
        "https://pipefy-prd-us-east-1.s3.amazonaws.com/"
        "orgs/c74580a4-6f84-48c1-b432-836eaed711b2/"
        "uploads/uuid/file.txt?x=1"
    )

    print(integration.extractFilePath(url))

    # fallback test
    print(integration.extractFilePath("uploads/uuid/file.txt"))

    # explicit override test
    print(integration.extractFilePath("uploads/uuid/file.txt", org_id="custom-org"))
