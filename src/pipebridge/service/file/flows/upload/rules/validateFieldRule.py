from pipebridge.exceptions import ValidationError
from pipebridge.exceptions.core.utils import getExceptionContext
from pipebridge.dispatcher.field.fieldType import FieldType
from pipebridge.service.file.flows.upload.context.uploadPipelineContext import (
    UploadPipelineContext,
)
from pipebridge.workflow.rules.baseRule import BaseRule


class ValidateFieldRule(BaseRule):
    """
    Validate whether the target field exists in the applicable schema.

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
            When the field does not exist in the applicable schema or is not an
            attachment field

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

        field = None
        if context.config.validate_field_in_current_phase:
            card = context.card_service.getCardModel(request.card_id)
            if card.current_phase is None:
                raise ValidationError(
                    message="Card current phase is unavailable for upload validation",
                    class_name=class_name,
                    method_name=method_name,
                )

            field = context.card_service.getCardCurrentPhaseField(
                request.card_id, request.field_id
            )
            if field is None:
                raise ValidationError(
                    message=(
                        f"Field '{request.field_id}' does not exist in the current "
                        f"phase schema '{card.current_phase.id}'"
                    ),
                    class_name=class_name,
                    method_name=method_name,
                )
        else:
            field = context.card_service.getCardPipeField(
                request.card_id, request.field_id
            )
            if field is None:
                raise ValidationError(
                    message=(
                        f"Field '{request.field_id}' does not exist in the card pipe "
                        "schema"
                    ),
                    class_name=class_name,
                    method_name=method_name,
                )

        if field.type != FieldType.ATTACHMENT:
            raise ValidationError(
                message=f"Field '{request.field_id}' is not an attachment field",
                class_name=class_name,
                method_name=method_name,
            )
