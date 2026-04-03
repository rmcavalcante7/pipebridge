from pipefy.exceptions.base import PipefyError


class InvalidPhaseError(PipefyError):
    """
    Raised when a card is not in the expected phase.

    :example:
        >>> isinstance(InvalidPhaseError("error"), InvalidPhaseError)
        True
    """
    pass