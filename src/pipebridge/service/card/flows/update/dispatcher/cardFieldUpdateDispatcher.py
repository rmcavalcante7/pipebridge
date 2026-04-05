from typing import Any, Optional

from pipebridge.models.field import Field
from pipebridge.models.phaseField import PhaseField
from pipebridge.service.card.flows.update.dispatcher.cardFieldUpdateHandlerRegistry import (
    CardFieldUpdateHandlerRegistry,
)
from pipebridge.service.card.flows.update.dispatcher.resolvedFieldUpdate import (
    ResolvedFieldUpdate,
)


class CardFieldUpdateDispatcher:
    """
    Dispatch field updates to the correct resolution handler.
    """

    def __init__(
        self, registry: Optional[CardFieldUpdateHandlerRegistry] = None
    ) -> None:
        """
        Initialize dispatcher with a handler registry.

        :param registry: CardFieldUpdateHandlerRegistry | None = Optional handler registry
        """
        self._registry = registry or CardFieldUpdateHandlerRegistry()

    def dispatch(
        self,
        field_id: str,
        field_type: str,
        input_value: Any,
        current_field: Optional[Field] = None,
        phase_field: Optional[PhaseField] = None,
    ) -> ResolvedFieldUpdate:
        """
        Dispatch a field update request to the proper field-type handler.

        :param field_id: str = Logical field identifier
        :param field_type: str = Pipefy field type
        :param input_value: Any = Raw caller-provided value
        :param current_field: Field | None = Current card field state
        :param phase_field: PhaseField | None = Current phase field metadata

        :return: ResolvedFieldUpdate = Canonical resolved operation
        """
        handler = self._registry.getHandler(field_type)
        return handler.resolve(
            field_id=field_id,
            field_type=field_type,
            input_value=input_value,
            current_field=current_field,
            phase_field=phase_field,
        )
