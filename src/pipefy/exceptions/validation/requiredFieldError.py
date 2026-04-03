from pipefy.exceptions.base import PipefyError


class RequiredFieldError(PipefyError):
    """
    Raised when a required field is missing or empty.

    :example:
        >>> isinstance(RequiredFieldError("error"), RequiredFieldError)
        True
    """
    pass