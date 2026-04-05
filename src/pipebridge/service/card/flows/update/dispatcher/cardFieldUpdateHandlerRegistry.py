from pipebridge.dispatcher.field.fieldType import FieldType
from pipebridge.exceptions import ValidationError, getExceptionContext
from pipebridge.service.card.flows.update.dispatcher.baseCardFieldUpdateHandler import (
    BaseCardFieldUpdateHandler,
)
from pipebridge.service.card.flows.update.dispatcher.handlers import (
    AssigneeUpdateHandler,
    AttachmentUpdateHandler,
    ChecklistUpdateHandler,
    ConnectorUpdateHandler,
    DateUpdateHandler,
    NumberUpdateHandler,
    OptionUpdateHandler,
    TextUpdateHandler,
    TimeUpdateHandler,
)


class CardFieldUpdateHandlerRegistry:
    """
    Registry mapping Pipefy field types to update resolution handlers.
    """

    def __init__(
        self,
        extra_handlers: dict[str, BaseCardFieldUpdateHandler] | None = None,
    ) -> None:
        """
        Initialize the field-type handler registry.

        :param extra_handlers: dict[str, BaseCardFieldUpdateHandler] | None =
            Optional custom handlers that augment or override the defaults
        """
        text_handler = TextUpdateHandler()
        date_handler = DateUpdateHandler()
        option_handler = OptionUpdateHandler()
        time_handler = TimeUpdateHandler()
        self._handlers: dict[str, BaseCardFieldUpdateHandler] = {
            FieldType.ATTACHMENT: AttachmentUpdateHandler(),
            FieldType.SHORT_TEXT: text_handler,
            FieldType.LONG_TEXT: text_handler,
            FieldType.EMAIL: text_handler,
            FieldType.PHONE: text_handler,
            FieldType.CPF: text_handler,
            FieldType.CNPJ: text_handler,
            FieldType.SELECT: option_handler,
            FieldType.LABEL_SELECT: option_handler,
            FieldType.RADIO_HORIZONTAL: option_handler,
            FieldType.RADIO_VERTICAL: option_handler,
            FieldType.NUMBER: NumberUpdateHandler(),
            FieldType.CURRENCY: NumberUpdateHandler(),
            FieldType.DATETIME: date_handler,
            FieldType.DATE: date_handler,
            FieldType.TIME: time_handler,
            FieldType.DUE_DATE: date_handler,
            FieldType.ASSIGNEE: AssigneeUpdateHandler(),
            FieldType.ASSIGNEE_SELECT: AssigneeUpdateHandler(),
            FieldType.CHECKLIST_HORIZONTAL: ChecklistUpdateHandler(),
            FieldType.CHECKLIST_VERTICAL: ChecklistUpdateHandler(),
            FieldType.CONNECTOR: ConnectorUpdateHandler(),
        }
        if extra_handlers:
            self._handlers.update(extra_handlers)

    def getHandler(self, field_type: str) -> BaseCardFieldUpdateHandler:
        """
        Retrieve the registered handler for a given field type.

        :param field_type: str = Pipefy field type

        :return: BaseCardFieldUpdateHandler = Registered handler

        :raises ValidationError:
            When the field type is unsupported by the registry
        """
        class_name, method_name = getExceptionContext(self)
        if field_type not in self._handlers:
            raise ValidationError(
                message=f"Unsupported field type: {field_type}",
                class_name=class_name,
                method_name=method_name,
            )
        return self._handlers[field_type]

    def registerHandler(
        self,
        field_type: str,
        handler: BaseCardFieldUpdateHandler,
    ) -> None:
        """
        Register or override a field-type-specific update handler.

        :param field_type: str = Pipefy field type identifier
        :param handler: BaseCardFieldUpdateHandler = Handler implementation
        """
        self._handlers[field_type] = handler
