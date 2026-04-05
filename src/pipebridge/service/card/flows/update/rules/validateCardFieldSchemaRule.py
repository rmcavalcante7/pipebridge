from datetime import datetime
from typing import Any

from pipebridge.dispatcher.field.fieldType import FieldType
from pipebridge.exceptions import ValidationError, getExceptionContext
from pipebridge.service.card.flows.update.context.cardUpdateContext import (
    CardUpdateContext,
)
from pipebridge.workflow.rules.baseRule import BaseRule


class ValidateCardFieldSchemaRule(BaseRule):
    """
    Validate field existence, options and basic type compatibility.
    """

    priority = 30

    def execute(self, context: CardUpdateContext) -> None:
        """
        Validate field existence, options and basic type compatibility.

        :param context: CardUpdateContext = Shared update-flow execution context

        :return: None

        :raises ValidationError:
            When a requested field is invalid for the current phase schema
        """
        if not any(
            (
                context.config.validate_field_existence,
                context.config.validate_field_options,
                context.config.validate_field_type,
            )
        ):
            return

        phase = context.phase
        if phase is None:
            return

        class_name, method_name = getExceptionContext(self)

        for field_id, value in context.request.fields.items():
            phase_field = phase.getField(field_id)

            if context.config.validate_field_existence and phase_field is None:
                raise ValidationError(
                    message=f"Field '{field_id}' does not belong to the current phase",
                    class_name=class_name,
                    method_name=method_name,
                )

            if phase_field is None:
                continue

            if context.config.validate_field_options and phase.getFieldOptions(
                field_id
            ):
                self._validateOptions(
                    field_id=field_id,
                    field_type=phase.getFieldType(field_id) or "",
                    value=value,
                    allowed_options=phase.getFieldOptions(field_id),
                    class_name=class_name,
                    method_name=method_name,
                )

            if context.config.validate_field_type:
                self._validateTypeCompatibility(
                    field_id=field_id,
                    field_type=phase.getFieldType(field_id) or "",
                    value=value,
                    class_name=class_name,
                    method_name=method_name,
                )

    @staticmethod
    def _validateTypeCompatibility(
        field_id: str,
        field_type: str,
        value: Any,
        class_name: str,
        method_name: str,
    ) -> None:
        if field_type in (
            FieldType.SHORT_TEXT,
            FieldType.LONG_TEXT,
            FieldType.EMAIL,
            FieldType.PHONE,
            FieldType.CPF,
            FieldType.CNPJ,
            FieldType.TIME,
            FieldType.SELECT,
            FieldType.LABEL_SELECT,
            FieldType.RADIO_HORIZONTAL,
            FieldType.RADIO_VERTICAL,
            FieldType.CONNECTOR,
        ):
            valid = isinstance(value, str)
        elif field_type in (FieldType.NUMBER, FieldType.CURRENCY):
            valid = isinstance(value, (int, float, str))
        elif field_type in (FieldType.DATE, FieldType.DATETIME, FieldType.DUE_DATE):
            valid = isinstance(value, (str, datetime))
        elif field_type in (FieldType.ASSIGNEE, FieldType.ASSIGNEE_SELECT):
            valid = isinstance(value, str) or (
                isinstance(value, list) and all(isinstance(item, str) for item in value)
            )
        elif field_type == FieldType.ATTACHMENT:
            valid = isinstance(value, list) and all(
                isinstance(item, str) for item in value
            )
        elif field_type in (
            FieldType.CHECKLIST_HORIZONTAL,
            FieldType.CHECKLIST_VERTICAL,
        ):
            valid = isinstance(value, list) and all(
                isinstance(item, str) for item in value
            )
        else:
            valid = True

        if not valid:
            raise ValidationError(
                message=(
                    f"Value '{value}' is not compatible with field "
                    f"'{field_id}' of type '{field_type}'"
                ),
                class_name=class_name,
                method_name=method_name,
            )

    @staticmethod
    def _validateOptions(
        field_id: str,
        field_type: str,
        value: Any,
        allowed_options: list[str],
        class_name: str,
        method_name: str,
    ) -> None:
        option_field_types = {
            FieldType.SELECT,
            FieldType.LABEL_SELECT,
            FieldType.RADIO_HORIZONTAL,
            FieldType.RADIO_VERTICAL,
        }
        checklist_field_types = {
            FieldType.CHECKLIST_HORIZONTAL,
            FieldType.CHECKLIST_VERTICAL,
        }

        if field_type in option_field_types and value not in allowed_options:
            raise ValidationError(
                message=(
                    f"Invalid option '{value}' for field '{field_id}'. "
                    f"Allowed options: {allowed_options}"
                ),
                class_name=class_name,
                method_name=method_name,
            )

        if field_type in checklist_field_types:
            invalid_options = (
                [item for item in value if item not in allowed_options]
                if isinstance(value, list)
                else [value]
            )

            if invalid_options:
                raise ValidationError(
                    message=(
                        f"Invalid options {invalid_options} for field '{field_id}'. "
                        f"Allowed options: {allowed_options}"
                    ),
                    class_name=class_name,
                    method_name=method_name,
                )
