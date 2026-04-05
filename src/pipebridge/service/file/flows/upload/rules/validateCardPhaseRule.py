from pipebridge.exceptions import ValidationError
from pipebridge.exceptions.core.utils import getExceptionContext
from pipebridge.service.file.flows.upload.context.uploadPipelineContext import (
    UploadPipelineContext,
)
from pipebridge.workflow.rules.baseRule import BaseRule


class ValidateCardPhaseRule(BaseRule):
    """
    Validate whether the card is currently in the expected phase.

    This rule is optional by design. When the request does not define
    ``expected_phase_id``, the rule is skipped.

    :example:
        >>> callable(ValidateCardPhaseRule.execute)
        True
    """

    priority = 30

    def execute(self, context: UploadPipelineContext) -> None:
        """
        Execute phase validation for the upload request.

        :param context: UploadPipelineContext = Shared upload execution context

        :return: None

        :raises ValidationError:
            When the card does not belong to the expected phase

        :example:
            >>> callable(ValidateCardPhaseRule.execute)
            True
        """
        class_name, method_name = getExceptionContext(self)

        request = context.request

        if not request.expected_phase_id:
            return

        card = context.card_service.getCardModel(request.card_id)

        if not card:
            raise ValidationError(
                message=(
                    "card was not found in pipeline. "
                    f"card_id searched: {request.card_id}"
                ),
                class_name=class_name,
                method_name=method_name,
            )

        current_phase = card.current_phase
        if current_phase is None:
            raise ValidationError(
                message="Card current phase is unavailable for phase validation",
                class_name=class_name,
                method_name=method_name,
            )

        if str(current_phase.id) != str(request.expected_phase_id):
            raise ValidationError(
                message=(
                    f"Card is in phase '{current_phase.id}', "
                    f"expected '{request.expected_phase_id}'"
                ),
                class_name=class_name,
                method_name=method_name,
            )
