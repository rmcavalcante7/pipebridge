# ============================================================
# Dependencies
# ============================================================
from typing import Any

from pipefy.models.phaseField import PhaseField

from pipefy.exceptions.utils import getExceptionContext
from pipefy.exceptions.validation.invalidPhaseError import InvalidPhaseError
from pipefy.exceptions.validation.fieldNotInPhaseError import FieldNotInPhaseError
from pipefy.exceptions.validation.invalidFieldOptionError import InvalidFieldOptionError
from pipefy.exceptions.validation.requiredFieldError import RequiredFieldError


class FieldValidator:
    """
    Validates field updates against Pipefy domain rules.

    This class ensures that values provided for field updates are valid
    according to the field metadata retrieved from Pipefy.

    Validation includes:
        - Phase consistency
        - Field existence in phase
        - Required field validation
        - Option constraints (select fields)

    :example:
        >>> validator = FieldValidator()
        >>> callable(validator.validate)
        True
    """

    # ============================================================
    # Public Methods
    # ============================================================

    def validate(
        self,
        current_phase_id: str,
        expected_phase_id: str,
        field_id: str,
        phase_field: PhaseField,
        value: Any
    ) -> None:
        """
        Validates a field update.

        :param current_phase_id: str = Current card phase ID
        :param expected_phase_id: str = Expected phase ID
        :param field_id: str = Field identifier
        :param phase_field: PhaseField = Field metadata from phase
        :param value: Any = New value to assign

        :return: None

        :raises InvalidPhaseError:
            When card is not in expected phase
        :raises FieldNotInPhaseError:
            When field is not part of the phase
        :raises RequiredFieldError:
            When required field is empty
        :raises InvalidFieldOptionError:
            When value is not within allowed options

        :example:
            >>> validator = FieldValidator()
            >>> callable(validator.validate)
            True
        """
        class_name, method_name = getExceptionContext(self)

        # --------------------------------------------------------
        # Phase validation
        # --------------------------------------------------------
        if expected_phase_id and current_phase_id != expected_phase_id:
            raise InvalidPhaseError(
                message="Card is not in the expected phase",
                class_name=class_name,
                method_name=method_name
            )

        # --------------------------------------------------------
        # Field existence validation
        # --------------------------------------------------------
        if phase_field is None:
            raise FieldNotInPhaseError(
                message=f"Field '{field_id}' does not belong to the current phase",
                class_name=class_name,
                method_name=method_name
            )

        # --------------------------------------------------------
        # Required validation
        # --------------------------------------------------------
        if phase_field.required:
            if value is None or (isinstance(value, str) and not value.strip()):
                raise RequiredFieldError(
                    message=f"Field '{field_id}' is required",
                    class_name=class_name,
                    method_name=method_name
                )

        # --------------------------------------------------------
        # Options validation (ONLY when options exist)
        # --------------------------------------------------------
        self._validateOptions(
            field_id=field_id,
            phase_field=phase_field,
            value=value,
            class_name=class_name,
            method_name=method_name
        )

    # ============================================================
    # Private Methods
    # ============================================================

    def _validateOptions(
        self,
        field_id: str,
        phase_field: PhaseField,
        value: Any,
        class_name: str,
        method_name: str
    ) -> None:
        """
        Validates value against allowed options.

        :param field_id: str = Field identifier
        :param phase_field: PhaseField = Field metadata
        :param value: Any = Value to validate
        :param class_name: str = Class context
        :param method_name: str = Method context

        :return: None

        :raises InvalidFieldOptionError:
            When value is not allowed
        """
        options = phase_field.options or []

        if not options:
            return

        # --------------------------------------------------------
        # Single value
        # --------------------------------------------------------
        if isinstance(value, str):
            if value not in options:
                raise InvalidFieldOptionError(
                    message=f"Invalid value '{value}' for field '{field_id}'. Allowed: {options}",
                    class_name=class_name,
                    method_name=method_name
                )

        # --------------------------------------------------------
        # List value
        # --------------------------------------------------------
        elif isinstance(value, list):
            invalid_values = [v for v in value if v not in options]

            if invalid_values:
                raise InvalidFieldOptionError(
                    message=f"Invalid values {invalid_values} for field '{field_id}'. Allowed: {options}",
                    class_name=class_name,
                    method_name=method_name
                )

        # --------------------------------------------------------
        # Invalid type
        # --------------------------------------------------------
        else:
            raise InvalidFieldOptionError(
                message=f"Invalid type for field '{field_id}'. Expected str or list[str]",
                class_name=class_name,
                method_name=method_name
            )


# ============================================================
# MAIN TEST
# ============================================================

if __name__ == "__main__":
    """
    Simple execution test.
    """
    validator = FieldValidator()
    print("FieldValidator loaded successfully.")