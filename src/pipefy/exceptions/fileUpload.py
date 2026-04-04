
from pipefy.exceptions.base import PipefyError


# ============================================================
# Exceptions
# ============================================================


class FileUploadError(PipefyError):
    """Raised when file upload fails."""
    pass


class FileAttachError(PipefyError):
    """Raised when attaching file to card fails."""
    pass

class FileValidationError(PipefyError):
    """Raised when file validation fails."""
    pass