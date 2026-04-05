from pipebridge.exceptions import ValidationError
from pipebridge.exceptions.core.utils import getExceptionContext
from pipebridge.service.file.flows.upload.context.uploadPipelineContext import (
    UploadPipelineContext,
)
from pipebridge.workflow.rules.baseRule import BaseRule


class ValidateFieldRule(BaseRule):
    """
    Validate whether the target field exists in the card.

    :example:
        >>> callable(ValidateFieldRule.execute)
        True
    """

    priority = 20

    def execute(self, context: UploadPipelineContext) -> None:
        """
        Execute field existence validation.

        :param context: UploadPipelineContext = Shared upload execution context

        :return: None

        :raises ValidationError:
            When the field does not exist in the card

        :example:
            >>> callable(ValidateFieldRule.execute)
            True
        """
        class_name, method_name = getExceptionContext(self)

        request = context.request

        if not request.card_id:
            raise ValidationError(
                message=f"card_id is required for {self.__class__.__name__}",
                class_name=class_name,
                method_name=method_name,
            )

        card = context.card_service.getCardModel(request.card_id)

        if not card.hasField(request.field_id):
            raise ValidationError(
                message=f"Field '{request.field_id}' does not exist in card",
                class_name=class_name,
                method_name=method_name,
            )
