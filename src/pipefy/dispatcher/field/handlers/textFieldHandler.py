from typing import Any

from pipefy.exceptions import ValidationError, getExceptionContext
from pipefy.dispatcher.field.fieldHandler import FieldHandler


class TextFieldHandler(FieldHandler):
    """
    Handles text-based field updates.

    Supports both short_text and long_text fields by receiving
    the appropriate mutation name.

    :param mutation_name: str = GraphQL mutation name

    :example:
        >>> handler = TextFieldHandler("updateCardShortTextFieldValue")
        >>> callable(handler.buildMutation)
        True
    """

    def __init__(self, mutation_name: str) -> None:
        """
        Initializes the TextFieldHandler.

        :param mutation_name: str = GraphQL mutation name
        """
        self._mutation_name: str = mutation_name

    def buildMutation(
        self,
        card_id: str,
        field_id: str,
        value: Any
    ) -> str:
        """
        Builds mutation for text fields.

        :param card_id: str = Card identifier
        :param field_id: str = Field identifier
        :param value: Any = Field value

        :return: str = GraphQL mutation

        :raises ValidationError:
            When value is not a string

        :example:
            >>> handler = TextFieldHandler("updateCardShortTextFieldValue")
            >>> callable(handler.buildMutation)
            True
        """
        class_name, method_name = getExceptionContext(self)

        if not isinstance(value, str):
            raise ValidationError(
                message="Text value must be a string",
                class_name=class_name,
                method_name=method_name
            )

        return f"""
        mutation {{
            {self._mutation_name}(
                input: {{
                    cardId: "{card_id}",
                    fieldId: "{field_id}",
                    value: "{value}"
                }}
            ) {{
                field {{ id }}
            }}
        }}
        """