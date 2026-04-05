from pipebridge.service.card.flows.update.context.cardUpdateContext import (
    CardUpdateContext,
)
from pipebridge.workflow.steps.baseStep import BaseStep


class LoadCardStep(BaseStep):
    """
    Load the current card model into execution context.
    """

    execution_profile = "network-read"

    def execute(self, context: CardUpdateContext) -> None:
        """
        Load the source card before validation and field dispatch.

        :param context: CardUpdateContext = Shared update-flow execution context

        :return: None
        """
        context.card = context.card_service.getCardModel(context.request.card_id)
        context.pipe_id = context.card.pipe_id if context.card is not None else None
        phase = context.card.current_phase if context.card is not None else None
        if phase is None or not phase.id:
            return

        cached_phase = context.pipe_schema_cache.getPhaseSchema(phase.id)
        if cached_phase is not None:
            context.phase = cached_phase
            context.pipe_id = context.pipe_schema_cache.getPipeIdForPhase(phase.id)
            return
