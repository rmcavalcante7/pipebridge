from pipefy.exceptions.base import PipefyError


class ValidationError(PipefyError):
    """
    Raised when input validation fails.
    """
    pass


class InvalidPhaseError(PipefyError):
    """
    Raised when card is not in expected phase.
    """

class FieldNotInPhaseError(PipefyError):
    """
    Raised when field does not belong to phase.
    """

class InvalidFieldOptionError(PipefyError):
    """
    Raised when value is not in allowed options.
    """

class RequiredFieldError(PipefyError):
    """
    Raised when required field is missing.
    """