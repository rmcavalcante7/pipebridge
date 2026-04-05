from datetime import datetime, timezone
from typing import Any, Optional

from pipebridge.exceptions import ValidationError, getExceptionContext
from pipebridge.models.field import Field
from pipebridge.models.phaseField import PhaseField
from pipebridge.service.card.flows.update.dispatcher.baseCardFieldUpdateHandler import (
    BaseCardFieldUpdateHandler,
)
from pipebridge.service.card.flows.update.dispatcher.resolvedFieldUpdate import (
    ResolvedFieldUpdate,
)


class DateUpdateHandler(BaseCardFieldUpdateHandler):
    """
    Resolve date and datetime field updates.

    Datetime values are normalized to UTC with a trailing ``Z`` so the SDK
    stays aligned with the payload shape observed in Pipefy frontend traffic.
    """

    def resolve(
        self,
        field_id: str,
        field_type: str,
        input_value: Any,
        current_field: Optional[Field] = None,
        phase_field: Optional[PhaseField] = None,
    ) -> ResolvedFieldUpdate:
        """
        Resolve date-like updates into their serialized representation.

        :param field_id: str = Logical field identifier
        :param field_type: str = Pipefy field type
        :param input_value: Any = Raw caller-provided value
        :param current_field: Field | None = Current card field state
        :param phase_field: PhaseField | None = Current phase field metadata

        :return: ResolvedFieldUpdate = Normalized update operation

        :raises ValidationError:
            When input is not a string or datetime instance
        """
        class_name, method_name = getExceptionContext(self)
        if isinstance(input_value, datetime):
            normalized = self._normalizeDatetime(input_value)
        elif isinstance(input_value, str):
            normalized = input_value
        else:
            raise ValidationError(
                message="Date fields require a string or datetime value",
                class_name=class_name,
                method_name=method_name,
            )

        return ResolvedFieldUpdate(
            field_id=field_id,
            field_type=field_type,
            input_value=input_value,
            current_field=current_field,
            phase_field=phase_field,
            new_value=normalized,
        )

    @staticmethod
    def _normalizeDatetime(value: datetime) -> str:
        """
        Normalize a Python datetime into UTC ISO-8601 with ``Z`` suffix.

        Naive datetimes are treated as UTC to preserve deterministic SDK
        behavior and avoid implicit local-time serialization.

        :param value: datetime = Input Python datetime

        :return: str = UTC serialized datetime with ``Z`` suffix

        :example:
            >>> DateUpdateHandler._normalizeDatetime(
            ...     datetime(2026, 4, 6, 14, 3, 25, 414000, tzinfo=timezone.utc)
            ... )
            '2026-04-06T14:03:25.414000Z'
        """
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        else:
            value = value.astimezone(timezone.utc)

        return value.isoformat().replace("+00:00", "Z")
