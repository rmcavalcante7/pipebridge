from pipebridge.exceptions import ValidationError, getExceptionContext
from pipebridge.service.card.flows.move.context.cardMoveContext import CardMoveContext
from pipebridge.workflow.steps.baseStep import BaseStep


class LoadCardForMoveStep(BaseStep):
    """
    Load the source card before validating or moving it.
    """

    execution_profile = "network-read"

    def execute(self, context: CardMoveContext) -> None:
        """
        Load the source card and expose it in the move-flow context.

        :param context: CardMoveContext = Shared move-flow execution context

        :return: None

        :raises ValidationError:
            When the loaded card does not expose current phase information
        """
        class_name, method_name = getExceptionContext(self)
        card = context.card_service.getCardModel(context.request.card_id)
        if card.current_phase is None:
            raise ValidationError(
                message="Loaded card does not expose current_phase",
                class_name=class_name,
                method_name=method_name,
            )

        context.card = card
        context.pipe_id = card.pipe_id
