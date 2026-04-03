from pipefy.exceptions.base import PipefyError


class FieldNotInPhaseError(PipefyError):
    """
    Raised when a field does not belong to the current phase.

    :example:
        >>> isinstance(FieldNotInPhaseError("error"), FieldNotInPhaseError)
        True
    """
    pass