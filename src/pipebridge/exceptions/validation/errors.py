from pipebridge.exceptions.core.base import PipefyError


class ValidationError(PipefyError):
    """
    Base exception for validation failures.

    This type represents user input or domain-state violations detected before
    or during SDK execution.
    """

    default_error_code = "validation.error"
