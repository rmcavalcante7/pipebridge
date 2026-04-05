from pipebridge.exceptions import ValidationError, getExceptionContext
from pipebridge.service.card.flows.move.context.cardMoveContext import CardMoveContext
from pipebridge.workflow.rules.baseRule import BaseRule


class ValidateCardMoveRequestRule(BaseRule):
    """
    Validate the basic integrity of a card move request.
    """

    priority = 10

    def execute(self, context: CardMoveContext) -> None:
        """
        Validate source-card availability and optional source-phase expectation.

        :param context: CardMoveContext = Shared move-flow execution context

        :return: None

        :raises ValidationError:
            When the card is not yet loaded
        :raises ValidationError:
            When the card does not expose current phase information
        :raises ValidationError:
            When the expected source phase does not match the current one
        """
        class_name, method_name = getExceptionContext(self)

        if context.card is None:
            raise ValidationError(
                message="card must be loaded before move validation",
                class_name=class_name,
                method_name=method_name,
            )

        if context.card.current_phase is None:
            raise ValidationError(
                message="card current_phase must be available before move validation",
                class_name=class_name,
                method_name=method_name,
            )

        expected_current_phase_id = context.request.expected_current_phase_id
        if (
            expected_current_phase_id
            and context.card.current_phase.id != expected_current_phase_id
        ):
            raise ValidationError(
                message=(
                    "Card is not in the expected source phase. "
                    f"Expected '{expected_current_phase_id}', "
                    f"found '{context.card.current_phase.id}'"
                ),
                class_name=class_name,
                method_name=method_name,
            )
