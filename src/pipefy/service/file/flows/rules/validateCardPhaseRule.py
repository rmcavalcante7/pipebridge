from pipefy.service.file.flows.pipeline.uploadPipelineContext import UploadPipelineContext
from pipefy.exceptions import ValidationError
from pipefy.exceptions.utils import getExceptionContext
from pipefy.service.file.flows.rules import BaseRule


class ValidateCardPhaseRule(BaseRule):
    """
    Validates if the card is in the expected phase.

    :example:
        >>> callable(ValidateCardPhaseRule.execute)
        True
    """

    def execute(self, context: UploadPipelineContext) -> None:
        class_name, method_name = getExceptionContext(self)

        request = context.request

        # If no constraint → skip
        if not request.expected_phase_id:
            raise ValidationError(
                message=f"expected_phase_id is required for {self.__class__.__name__}",
                class_name=class_name,
                method_name=method_name
            )

        card = context.card_service.getCardModel(request.card_id)

        if not card:
            raise ValidationError(
                message=f"card was not found in pipeline. card_id searched: {request.card_id}. "
                        f"Information is required for {self.__class__.__name__}",
                class_name=class_name,
                method_name=method_name
            )

        if str(card.current_phase.id) != str(request.expected_phase_id):
            raise ValidationError(
                f"Card is in phase '{card.current_phase.id}', expected '{request.expected_phase_id}'",
                class_name,
                method_name
            )