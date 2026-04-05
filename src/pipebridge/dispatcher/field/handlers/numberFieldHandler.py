from typing import Any

from pipebridge.exceptions import ValidationError, getExceptionContext
from pipebridge.dispatcher.field.fieldHandler import FieldHandler


class NumberFieldHandler(FieldHandler):
    """
    Handles numeric field updates.

    Pipefy expects numeric values as strings.

    :example:
        >>> handler = NumberFieldHandler()
        >>> callable(handler.buildMutation)
        True
    """

    def buildMutation(self, card_id: str, field_id: str, value: Any) -> str:
        """
        Builds mutation for numeric fields.

        :param card_id: str = Card identifier
        :param field_id: str = Field identifier
        :param value: Any = Numeric value

        :return: str = GraphQL mutation

        :raises ValidationError:
            When value is not int, float or str

        :example:
            >>> handler = NumberFieldHandler()
            >>> callable(handler.buildMutation)
            True
        """
        class_name, method_name = getExceptionContext(self)

        if not isinstance(value, (int, float, str)):
            raise ValidationError(
                message="Number value must be int, float or string",
                class_name=class_name,
                method_name=method_name,
            )

        return f"""
        mutation {{
            updateCardNumericFieldValue(
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
