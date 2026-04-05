from pipebridge.exceptions.validation.errors import ValidationError


class FieldNotInPhaseError(ValidationError):
    """
    Raised when a field does not belong to the current phase.

    :example:
        >>> isinstance(FieldNotInPhaseError("error"), FieldNotInPhaseError)
        True
    """

    default_error_code = "validation.field.not_in_phase"


class InvalidFieldOptionError(ValidationError):
    """
    Raised when a field value is not within the allowed options.

    :example:
        >>> isinstance(InvalidFieldOptionError("error"), InvalidFieldOptionError)
        True
    """

    default_error_code = "validation.field.invalid_option"


class RequiredFieldError(ValidationError):
    """
    Raised when a required field is missing or empty.

    :example:
        >>> isinstance(RequiredFieldError("error"), RequiredFieldError)
        True
    """

    default_error_code = "validation.field.required"
