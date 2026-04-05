from typing import Any, List

from pipebridge.exceptions import ValidationError, getExceptionContext
from pipebridge.dispatcher.field.fieldHandler import FieldHandler


class AssigneeFieldHandler(FieldHandler):
    """
    Handles assignee field updates.

    :example:
        >>> handler = AssigneeFieldHandler()
        >>> callable(handler.buildMutation)
        True
    """

    def buildMutation(self, card_id: str, field_id: str, value: Any) -> str:
        """
        Builds mutation for assignee fields.

        :param card_id: str = Card identifier
        :param field_id: str = Field identifier
        :param value: list[str] = List of user IDs

        :return: str = GraphQL mutation

        :raises ValidationError:
            When value is not a list of strings

        :example:
            >>> handler = AssigneeFieldHandler()
            >>> callable(handler.buildMutation)
            True
        """
        class_name, method_name = getExceptionContext(self)

        if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
            raise ValidationError(
                message="Assignee value must be a list of strings",
                class_name=class_name,
                method_name=method_name,
            )

        value_str: str = str(value).replace("'", '"')

        return f"""
        mutation {{
            updateCardAssigneeFieldValue(
                input: {{
                    cardId: "{card_id}",
                    fieldId: "{field_id}",
                    value: {value_str}
                }}
            ) {{
                field {{ id }}
            }}
        }}
        """
