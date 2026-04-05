from pipebridge.exceptions.core.base import PipefyError


class ParsingError(PipefyError):
    """
    Raised when parsing data fails.
    """

    pass


class UnexpectedResponseError(PipefyError):
    """
    Raised when API response structure is invalid.
    """

    pass
