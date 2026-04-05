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


class AttachmentUpdateHandler(BaseCardFieldUpdateHandler):
    """
    Resolve attachment field updates.
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
        Resolve attachment updates into a final list of file references.

        :param field_id: str = Logical field identifier
        :param field_type: str = Pipefy field type
        :param input_value: Any = Raw caller-provided value
        :param current_field: Field | None = Current card field state
        :param phase_field: PhaseField | None = Current phase field metadata

        :return: ResolvedFieldUpdate = Normalized update operation

        :raises ValidationError:
            When input is not a list of string file paths
        """
        class_name, method_name = getExceptionContext(self)
        if not isinstance(input_value, list) or not all(
            isinstance(item, str) for item in input_value
        ):
            raise ValidationError(
                message="Attachment fields require a list of file paths",
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
