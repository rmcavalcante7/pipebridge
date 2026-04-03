from pipefy.exceptions import ValidationError, getExceptionContext
from pipefy.dispatcher.field.fieldType import FieldType
from pipefy.dispatcher.field.handlers.attachmentFieldHandler import AttachmentFieldHandler
from pipefy.dispatcher.field.handlers.textFieldHandler import TextFieldHandler
from pipefy.dispatcher.field.handlers.numberFieldHandler import NumberFieldHandler
from pipefy.dispatcher.field.handlers.dateFieldHandler import DateFieldHandler
from pipefy.dispatcher.field.handlers.assigneeFieldHandler import AssigneeFieldHandler
from pipefy.dispatcher.field.fieldHandler import FieldHandler


class FieldHandlerRegistry:
    """
    Registry that maps field types to their respective handlers.

    :example:
        >>> registry = FieldHandlerRegistry()
        >>> callable(registry.getHandler)
        True
    """

    def __init__(self) -> None:
        """
        Initializes the registry with all supported handlers.
        """
        self._handlers = {
            FieldType.ATTACHMENT: AttachmentFieldHandler(),
            FieldType.SHORT_TEXT: TextFieldHandler("updateCardShortTextFieldValue"),
            FieldType.LONG_TEXT: TextFieldHandler("updateCardLongTextFieldValue"),
            FieldType.SELECT: TextFieldHandler("updateCardSelectFieldValue"),
            FieldType.NUMBER: NumberFieldHandler(),
            FieldType.DATETIME: DateFieldHandler("updateCardDateTimeFieldValue"),
            FieldType.DUE_DATE: DateFieldHandler("updateCardDueDateFieldValue"),
            FieldType.ASSIGNEE: AssigneeFieldHandler(),
        }

    def getHandler(self, field_type: str) -> FieldHandler:
        """
        Retrieves the handler for a given field type.

        :param field_type: str = Field type identifier

        :return: FieldHandler = Corresponding handler

        :raises ValidationError:
            When field type is not supported

        :example:
            >>> registry = FieldHandlerRegistry()
            >>> callable(registry.getHandler)
            True
        """
        class_name, method_name = getExceptionContext(self)

        if field_type not in self._handlers:
            raise ValidationError(
                message=f"Unsupported field type: {field_type}",
                class_name=class_name,
                method_name=method_name
            )

        return self._handlers[field_type]