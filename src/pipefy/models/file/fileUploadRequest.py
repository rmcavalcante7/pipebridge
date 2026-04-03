# ============================================================
# Dependencies
# ============================================================
from typing import Optional

from pipefy.exceptions import ValidationError
from pipefy.exceptions.utils import getExceptionContext


# ============================================================
# FileUploadRequest
# ============================================================
class FileUploadRequest:
    """
    Represents a file upload request.

    This class encapsulates all input data required to execute
    a file upload operation in Pipefy.

    It is designed to:

    - Eliminate parameter explosion
    - Improve API readability
    - Provide validation at construction time
    - Enable extensibility without breaking method signatures

    This object is immutable by design convention and should be
    treated as a command object.

    :param file_name: str = Name of the file to upload
    :param file_bytes: bytes = Binary content of the file
    :param card_id: str = Pipefy card identifier
    :param field_id: str = Target field identifier
    :param organization_id: str = Pipefy organization identifier
    :param replace_files: bool = Whether to replace or append existing files

    :raises ValidationError:
        When any parameter is invalid

    :example:
        >>> request = FileUploadRequest(
        ...     file_name="file.txt",
        ...     file_bytes=b"data",
        ...     card_id="123",
        ...     field_id="field_1",
        ...     organization_id="org_1"
        ... )
        >>> isinstance(request, FileUploadRequest)
        True
    """

    def __init__(
        self,
        file_name: str,
        file_bytes: bytes,
        card_id: str,
        field_id: str,
        organization_id: str,
        replace_files: bool = False,
        expected_phase_id: Optional[str] = None

    ) -> None:
        class_name, method_name = getExceptionContext(self)

        if not file_name or not isinstance(file_name, str):
            raise ValidationError(
                "file_name must be a non-empty string",
                class_name,
                method_name
            )

        if not isinstance(file_bytes, bytes):
            raise ValidationError(
                "file_bytes must be of type bytes",
                class_name,
                method_name
            )

        if not card_id or not isinstance(card_id, str):
            raise ValidationError(
                "card_id must be a non-empty string",
                class_name,
                method_name
            )

        if not field_id or not isinstance(field_id, str):
            raise ValidationError(
                "field_id must be a non-empty string",
                class_name,
                method_name
            )

        if not organization_id or not isinstance(organization_id, str):
            raise ValidationError(
                "organization_id must be a non-empty string",
                class_name,
                method_name
            )

        if not isinstance(replace_files, bool):
            raise ValidationError(
                "replace_files must be a boolean",
                class_name,
                method_name
            )

        if expected_phase_id is not None and not isinstance(expected_phase_id, str):
            raise ValidationError(
                "expected_phase_id must be a non-empty string",
                class_name,
                method_name
            )

        self.file_name: str = file_name
        self.file_bytes: bytes = file_bytes
        self.card_id: str = card_id
        self.field_id: str = field_id
        self.organization_id: str = organization_id
        self.replace_files: bool = replace_files
        self.expected_phase_id: Optional[str] = expected_phase_id

    # ============================================================
    # Factory Methods
    # ============================================================

    @classmethod
    def fromFile(
        cls,
        file_path: str,
        card_id: str,
        field_id: str,
        organization_id: str,
        replace_files: bool = False
    ) -> "FileUploadRequest":
        """
        Creates a FileUploadRequest from a file path.

        :param file_path: str = Local file path
        :param card_id: str
        :param field_id: str
        :param organization_id: str
        :param replace_files: bool

        :return: FileUploadRequest

        :raises ValidationError:
            When file_path is invalid
        :raises IOError:
            When file cannot be read

        :example:
            >>> import os, tempfile
            >>> tmp = tempfile.NamedTemporaryFile(delete=False)
            >>> _ = tmp.write(b"data")
            >>> tmp.close()
            >>> req = FileUploadRequest.fromFile(tmp.name, "1", "f", "org")
            >>> isinstance(req, FileUploadRequest)
            True
        """
        class_name, method_name = getExceptionContext(cls)

        if not file_path or not isinstance(file_path, str):
            raise ValidationError(
                "file_path must be a non-empty string",
                class_name,
                method_name
            )

        try:
            with open(file_path, "rb") as f:
                content = f.read()

            file_name = file_path.split("/")[-1]

            return cls(
                file_name=file_name,
                file_bytes=content,
                card_id=card_id,
                field_id=field_id,
                organization_id=organization_id,
                replace_files=replace_files
            )

        except Exception as exc:
            raise IOError(str(exc)) from exc


# ============================================================
# MAIN TEST
# ============================================================
if __name__ == "__main__":
    req = FileUploadRequest("a.txt", b"data", "1", "f", "org")
    print(req.file_name)