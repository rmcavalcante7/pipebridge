from pipebridge.exceptions.validation.errors import ValidationError


class InvalidPhaseError(ValidationError):
    """
    Raised when a card is not in the expected phase.

    :example:
        >>> isinstance(InvalidPhaseError("error"), InvalidPhaseError)
        True
    """

    default_error_code = "validation.phase.invalid"
