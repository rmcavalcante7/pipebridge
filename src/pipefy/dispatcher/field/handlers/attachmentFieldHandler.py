from typing import Any, List

from pipefy.exceptions import ValidationError, getExceptionContext
from pipefy.dispatcher.field.fieldHandler import FieldHandler


class AttachmentFieldHandler(FieldHandler):
    """
    Handles attachment field updates.

    :example:
        >>> callable(AttachmentFieldHandler.buildMutation)
        True
    """

    def buildMutation(self, card_id: str, field_id: str, value: Any) -> str:
        """
        Builds mutation for attachment fields.

        :param card_id: str
        :param field_id: str
        :param value: list[str]

        :return: str

        :raises ValidationError:
            When value is not a list of strings
        """
        class_name, method_name = getExceptionContext(self)

        if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
            raise ValidationError(
                message="Attachment value must be a list of strings",
                class_name=class_name,
                method_name=method_name
            )

        urls: str = str(value).replace("'", '"')

        return f"""
        mutation {{
            updateCardAttachmentFieldValue(
                input: {{
                    cardId: "{card_id}",
                    fieldId: "{field_id}",
                    value: {urls}
                }}
            ) {{
                field {{ id }}
            }}
        }}
        """