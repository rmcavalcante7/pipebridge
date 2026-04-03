from pipefy.service.file.flows.pipeline.uploadPipelineContext import UploadPipelineContext
from pipefy.exceptions import ValidationError
from pipefy.exceptions.utils import getExceptionContext


class ValidateFieldStep:
    """
    Validates if the field exists in the card.

    :example:
        >>> callable(ValidateFieldStep.execute)
        True
    """

    def __str__(self) -> str:
        return "<ValidateFieldStep>"

    def __repr__(self) -> str:
        return "<ValidateFieldStep()>"

    def execute(self, context: UploadPipelineContext) -> None:
        """
        Validates field existence.

        :param context: UploadPipelineContext

        :raises ValidationError:
            When field does not exist
        """
        class_name, method_name = getExceptionContext(self)

        request = context.request
        card = context.card_service.getCardModel(request.card_id)

        if str(request.field_id) not in str(card.fields_map):
            raise ValidationError(
                f"Field '{request.field_id}' does not exist in card",
                class_name,
                method_name
            )

