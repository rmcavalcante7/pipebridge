from pipefy.service.file.flows.pipeline.uploadPipelineContext import UploadPipelineContext
from pipefy.exceptions import ValidationError
from pipefy.exceptions.utils import getExceptionContext
from pipefy.service.file.flows.rules.baseRule import BaseRule


class ValidateFieldRule(BaseRule):
    """
    Validates if the field exists in the card.

    :example:
        >>> callable(ValidateFieldRule.execute)
        True
    """

    priority = 20

    def execute(self, context: UploadPipelineContext) -> None:
        """
        Validates field existence.

        :param context: UploadPipelineContext

        :raises ValidationError:
            When field does not exist
        """
        class_name, method_name = getExceptionContext(self)

        request = context.request

        if not request.card_id:
            raise ValidationError(
                message=f"card_id is required for {self.__class__.__name__}",
                class_name=class_name,
                method_name=method_name
            )

        card = context.card_service.getCardModel(request.card_id)

        if str(request.field_id) not in str(card.fields_map):
            raise ValidationError(
                f"Field '{request.field_id}' does not exist in card",
                class_name,
                method_name
            )

