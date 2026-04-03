from pipefy.service.file.flows.pipeline.uploadPipelineContext import UploadPipelineContext
from pipefy.exceptions import ValidationError
from pipefy.exceptions.utils import getExceptionContext


class ValidateCardPhaseStep:
    """
    Validates if the card is in the expected phase.

    :example:
        >>> callable(ValidateCardPhaseStep.execute)
        True
    """

    def __str__(self) -> str:
        return "<ValidateCardPhaseStep>"

    def __repr__(self) -> str:
        return "<ValidateCardPhaseStep()>"

    def execute(self, context: UploadPipelineContext) -> None:
        class_name, method_name = getExceptionContext(self)

        request = context.request

        # If no constraint → skip
        if not request.expected_phase_id:
            return

        card = context.card_service.getCardModel(request.card_id)

        if str(card.current_phase.id) != str(request.expected_phase_id):
            raise ValidationError(
                f"Card is in phase '{card.current_phase.id}', expected '{request.expected_phase_id}'",
                class_name,
                method_name
            )