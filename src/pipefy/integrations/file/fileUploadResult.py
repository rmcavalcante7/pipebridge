# ============================================================
# Dependencies
# ============================================================
from typing import Optional


class FileUploadResult:
    """
    Data transfer object representing the result of a file upload operation.

    This class encapsulates metadata returned after uploading a file,
    including the stored file path, optional download URL, and success status.

    This object is immutable after creation and contains no business logic.

    :param file_path: str = Path or URL of the uploaded file
    :param download_url: Optional[str] = Public download URL (if available)
    :param success: bool = Indicates if upload operation succeeded

    :raises ValueError:
        This class does NOT raise ValueError directly, but invalid usage
        should be prevented by upstream validation (e.g., FileService)

    :example:
        >>> result = FileUploadResult(
        ...     file_path="https://storage/file.txt",
        ...     download_url="https://download/file.txt",
        ...     success=True
        ... )
        >>> result.success
        True
    """

    def __init__(
        self,
        file_path: list[str],
        download_url: Optional[str],
        success: bool
    ) -> None:
        """
        Initializes FileUploadResult.

        :param file_path: list[str] = List of uploaded file paths
        :param download_url: Optional[str] = Public download URL
        :param success: bool = Upload success flag

        :example:
            >>> result = FileUploadResult(["path"], None, True)
            >>> "FileUploadResult" in str(result)
            True
        """
        self.file_path: list[str] = file_path
        self.download_url: Optional[str] = download_url
        self.success: bool = success

    # ============================================================
    # Representation Methods
    # ============================================================

    def __repr__(self) -> str:
        """
        Returns a developer-friendly string representation.

        :return: str = Debug representation

        :example:
            >>> result = FileUploadResult("path", None, True)
            >>> "FileUploadResult" in repr(result)
            True
        """
        return (
            f"{self.__class__.__name__}("
            f"file_path={self.file_path!r}, "
            f"download_url={self.download_url!r}, "
            f"success={self.success!r})"
        )

    def __str__(self) -> str:
        """
        Returns a human-readable representation.

        :return: str = Readable string

        :example:
            >>> result = FileUploadResult(["path"], None, True)
            >>> "FileUploadResult" in str(result)
            True
        """
        return (
            f"FileUploadResult(success={self.success}, "
            f"files={len(self.file_path)})"
        )
