
from pipefy.exceptions.base import PipefyError


# ============================================================
# Exceptions
# ============================================================


class FileUploadError(PipefyError):
    """Raised when file upload fails."""
    pass


class FileAttachError(Exception):
    """Raised when attaching file to card fails."""
    pass

class FileValidationError(Exception):
    """Raised when file validation fails."""
    pass