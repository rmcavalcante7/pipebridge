import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from pipebridge.dispatcher.field.fieldType import FieldType
from pipebridge.exceptions import ValidationError, getExceptionContext
from pipebridge.service.card.flows.update.context.cardUpdateContext import (
    CardUpdateContext,
)
from pipebridge.workflow.rules.baseRule import BaseRule


class ValidateCardFieldFormatRule(BaseRule):
    """
    Validate semantic formats for selected field types.

    This rule is optional by configuration because it adds extra validation
    cost for consumers that want stricter safeguards before issuing updates.
    """

    priority = 40

    _EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
    _PHONE_PATTERN = re.compile(r"^\+?[\d\s().-]{8,}$")
    _CPF_PATTERN = re.compile(r"^\d{3}\.\d{3}\.\d{3}-\d{2}$|^\d{11}$")
    _CNPJ_PATTERN = re.compile(r"^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$|^\d{14}$")
    _TIME_PATTERN = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d$")

    def execute(self, context: CardUpdateContext) -> None:
        """
        Validate semantic formats for selected field types.

        :param context: CardUpdateContext = Shared update-flow execution context

        :return: None

        :raises ValidationError:
            When a supported field receives an invalid semantic format
        """
        if not context.config.validate_field_format:
            return

        if context.phase is None:
            return

        class_name, method_name = getExceptionContext(self)

        for field_id, value in context.request.fields.items():
            field_type = context.phase.getFieldType(field_id)
            if not field_type:
                continue

            self._validateFieldFormat(
                field_id=field_id,
                field_type=field_type,
                value=value,
                class_name=class_name,
                method_name=method_name,
            )

    @classmethod
    def _validateFieldFormat(
        cls,
        field_id: str,
        field_type: str,
        value: Any,
        class_name: str,
        method_name: str,
    ) -> None:
        if field_type == FieldType.EMAIL:
            cls._ensureRegexMatch(
                field_id,
                value,
                cls._EMAIL_PATTERN,
                "Email field requires a valid email address",
                class_name,
                method_name,
            )
            return

        if field_type == FieldType.PHONE:
            cls._ensureRegexMatch(
                field_id,
                value,
                cls._PHONE_PATTERN,
                "Phone field requires a valid phone-like string",
                class_name,
                method_name,
            )
            return

        if field_type == FieldType.CPF:
            cls._ensureRegexMatch(
                field_id,
                value,
                cls._CPF_PATTERN,
                "CPF field requires 11 digits or the mask 000.000.000-00",
                class_name,
                method_name,
            )
            return

        if field_type == FieldType.CNPJ:
            cls._ensureRegexMatch(
                field_id,
                value,
                cls._CNPJ_PATTERN,
                "CNPJ field requires 14 digits or the mask 00.000.000/0000-00",
                class_name,
                method_name,
            )
            return

        if field_type == FieldType.CURRENCY:
            cls._ensureCurrency(field_id, value, class_name, method_name)
            return

        if field_type == FieldType.DATE:
            cls._ensureDate(field_id, value, class_name, method_name)
            return

        if field_type == FieldType.TIME:
            cls._ensureRegexMatch(
                field_id,
                value,
                cls._TIME_PATTERN,
                "Time field requires a valid HH:MM value",
                class_name,
                method_name,
            )

    @staticmethod
    def _ensureRegexMatch(
        field_id: str,
        value: Any,
        pattern: re.Pattern[str],
        message: str,
        class_name: str,
        method_name: str,
    ) -> None:
        if not isinstance(value, str) or not pattern.fullmatch(value.strip()):
            raise ValidationError(
                message=f"{message}: field '{field_id}' received '{value}'",
                class_name=class_name,
                method_name=method_name,
            )

    @staticmethod
    def _ensureCurrency(
        field_id: str,
        value: Any,
        class_name: str,
        method_name: str,
    ) -> None:
        if isinstance(value, (int, float, Decimal)):
            return

        if isinstance(value, str):
            normalized = (
                value.strip()
                .replace("R$", "")
                .replace("$", "")
                .replace(".", "")
                .replace(",", ".")
                .strip()
            )
            try:
                Decimal(normalized)
                return
            except InvalidOperation, ValueError:
                pass

        raise ValidationError(
            message=f"Currency field '{field_id}' requires a numeric or currency-like value",
            class_name=class_name,
            method_name=method_name,
        )

    @staticmethod
    def _ensureDate(
        field_id: str,
        value: Any,
        class_name: str,
        method_name: str,
    ) -> None:
        if isinstance(value, (date, datetime)):
            return

        if isinstance(value, str):
            try:
                date.fromisoformat(value[:10])
                return
            except ValueError:
                pass

        raise ValidationError(
            message=f"Date field '{field_id}' requires an ISO date-like value",
            class_name=class_name,
            method_name=method_name,
        )
