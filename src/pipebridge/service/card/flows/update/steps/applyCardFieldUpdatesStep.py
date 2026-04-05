from pipebridge.service.card.flows.update.context.cardUpdateContext import (
    CardUpdateContext,
)
from pipebridge.service.card.mutations.cardMutations import CardMutations
from pipebridge.workflow.steps.baseStep import BaseStep


class ApplyCardFieldUpdatesStep(BaseStep):
    """
    Apply resolved field updates to Pipefy.
    """

    execution_profile = "network-write"

    def execute(self, context: CardUpdateContext) -> None:
        """
        Execute all resolved field updates against the Pipefy API.

        :param context: CardUpdateContext = Shared update-flow execution context

        :return: None
        """
        for operation in context.resolved_operations:
            mutation = CardMutations.updateCardField(
                card_id=context.request.card_id,
                field_id=operation.field_id,
                value=operation.new_value,
            )
            context.responses[operation.field_id] = context.client.sendRequest(
                mutation,
                timeout=60,
            )
