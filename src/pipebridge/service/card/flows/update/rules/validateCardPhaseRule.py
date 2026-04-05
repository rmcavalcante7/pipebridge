from pipebridge.exceptions import ValidationError, getExceptionContext
from pipebridge.service.card.flows.update.context.cardUpdateContext import (
    CardUpdateContext,
)
from pipebridge.workflow.rules.baseRule import BaseRule


class ValidateCardPhaseRule(BaseRule):
    """
    Validate that the card is in the expected phase, when requested.
    """

    priority = 20

    def execute(self, context: CardUpdateContext) -> None:
        """
        Validate the card current phase against the expected phase identifier.

        :param context: CardUpdateContext = Shared update-flow execution context

        :return: None

        :raises ValidationError:
            When the card phase does not match the expected phase
        """
        if not context.config.validate_phase:
            return

        expected_phase_id = context.request.expected_phase_id
        if not expected_phase_id:
            return

        class_name, method_name = getExceptionContext(self)

        if context.card is None or context.card.current_phase is None:
            raise ValidationError(
                message="card phase must be loaded before validation",
                class_name=class_name,
                method_name=method_name,
            )

        current_phase_id = context.card.current_phase.id
        if current_phase_id != expected_phase_id:
            raise ValidationError(
                message=(
                    f"Card is in phase '{current_phase_id}', "
                    f"expected '{expected_phase_id}'"
                ),
                class_name=class_name,
                method_name=method_name,
            )
