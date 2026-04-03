from pipefy.exceptions.base import PipefyError


class InvalidFieldOptionError(PipefyError):
    """
    Raised when a field value is not within allowed options.

    :example:
        >>> isinstance(InvalidFieldOptionError("error"), InvalidFieldOptionError)
        True
    """
    pass