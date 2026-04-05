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


class ConnectorUpdateHandler(BaseCardFieldUpdateHandler):
    """
    Resolve connector field updates.

    Connector fields are represented by related card or record identifiers.
    The SDK currently models them as a single string identifier.
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
        Resolve connector updates into a related item identifier.

        :param field_id: str = Logical field identifier
        :param field_type: str = Pipefy field type
        :param input_value: Any = Raw caller-provided value
        :param current_field: Field | None = Current card field state
        :param phase_field: PhaseField | None = Current phase field metadata

        :return: ResolvedFieldUpdate = Normalized update operation

        :raises ValidationError:
            When input is not a string identifier
        """
        class_name, method_name = getExceptionContext(self)
        if not isinstance(input_value, str):
            raise ValidationError(
                message="Connector fields require a string identifier",
                class_name=class_name,
                method_name=method_name,
            )

        return ResolvedFieldUpdate(
            field_id=field_id,
            field_type=field_type,
            input_value=input_value,
            current_field=current_field,
            phase_field=phase_field,
            new_value=input_value,
        )
