from pipebridge.exceptions import ValidationError, getExceptionContext
from pipebridge.service.card.flows.move.context.cardMoveContext import CardMoveContext
from pipebridge.workflow.steps.baseStep import BaseStep


class MoveCardToPhaseStep(BaseStep):
    """
    Execute the low-level Pipefy mutation that moves a card to another phase.
    """

    execution_profile = "network-write"

    def execute(self, context: CardMoveContext) -> None:
        """
        Execute the validated phase transition through the low-level service.

        :param context: CardMoveContext = Shared move-flow execution context

        :return: None

        :raises ValidationError:
            When the card was not loaded before step execution
        """
        class_name, method_name = getExceptionContext(self)
        if context.card is None:
            raise ValidationError(
                message="card must be loaded before move execution",
                class_name=class_name,
                method_name=method_name,
            )

        context.response = context.card_service.moveCardToPhase(
            card_id=context.request.card_id,
            phase_id=context.request.destination_phase_id,
        )
