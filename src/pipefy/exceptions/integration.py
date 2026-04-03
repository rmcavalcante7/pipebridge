from pipefy.exceptions.base import PipefyError


class IntegrationError(PipefyError):
    """
    Raised when external integrations fail.
    """
    pass