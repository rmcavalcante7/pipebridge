from pipebridge.exceptions import ValidationError, getExceptionContext
from pipebridge.service.card.flows.update.context.cardUpdateContext import (
    CardUpdateContext,
)
from pipebridge.workflow.rules.baseRule import BaseRule


class ValidateCardUpdateRequestRule(BaseRule):
    """
    Validate the minimum shape required for a card update request.
    """

    priority = 10

    def execute(self, context: CardUpdateContext) -> None:
        """
        Validate the minimum shape required for a card update request.

        :param context: CardUpdateContext = Shared update-flow execution context

        :return: None

        :raises ValidationError:
            When the request is structurally inconsistent with loaded context
        """
        class_name, method_name = getExceptionContext(self)

        if context.request is None:
            raise ValidationError(
                message="request cannot be None",
                class_name=class_name,
                method_name=method_name,
            )

        if context.card is None:
            raise ValidationError(
                message="card must be loaded before rule execution",
                class_name=class_name,
                method_name=method_name,
            )
