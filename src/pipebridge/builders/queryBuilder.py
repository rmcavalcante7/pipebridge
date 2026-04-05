# ============================================================
# Dependencies
# ============================================================
from typing import Dict, List
import inspect

from pipebridge.exceptions import ValidationError


class QueryBuilder:
    """
    Builds GraphQL query fragments dynamically.

    This class is responsible for generating attribute blocks used in
    GraphQL queries for Pipefy entities (e.g., cards).

    It supports:
    - Direct attributes (same name as GraphQL fields)
    - Nested attributes (predefined structures)

    :example:
        >>> attrs = ["id", "title", "fields"]
        >>> result = QueryBuilder.buildCardAttributes(attrs)
        >>> isinstance(result, str)
        True
    """

    NODE_ATTRIBUTES_SAME_NAME: tuple[str, ...] = (
        "age",
        "attachments_count",
        "comments_count",
        "createdAt",
        "id",
        "title",
        "updated_at",
    )

    NODE_ATTRIBUTES: Dict[str, str] = {
        "assignees": "assignees { id name }",
        "labels": "labels { id name color }",
        "fields": "fields { name value }",
        "attachments": "attachments {url}",
    }

    # ============================================================
    # Public Methods
    # ============================================================

    @staticmethod
    def buildCardAttributes(attributes: List[str]) -> str:
        """
        Builds a GraphQL fragment for card attributes.

        This method dynamically constructs a GraphQL selection set
        based on the provided attribute names.

        Supported attribute types:
        - Direct attributes (same name in GraphQL)
        - Predefined nested attributes

        :param attributes: list[str] = List of attribute names to include

        :return: str = GraphQL fragment formatted as a selection set

        :raises InvalidParameterError:
            When an attribute is not recognized

        :example:
            >>> attrs = ["id", "title"]
            >>> fragment = QueryBuilder.buildCardAttributes(attrs)
            >>> fragment.startswith("{")
            True
        """
        try:
            result: str = ""

            for attr in attributes:
                if attr in QueryBuilder.NODE_ATTRIBUTES_SAME_NAME:
                    result += f"{attr}\n"
                else:
                    result += QueryBuilder.NODE_ATTRIBUTES[attr] + "\n"

            return f"{{ {result} }}"

        except KeyError as exc:
            frame = inspect.currentframe()
            method_name = (
                frame.f_code.co_name if frame is not None else "buildCardAttributes"
            )
            raise ValidationError(
                f"Class: {QueryBuilder.__name__}\n"
                f"Method: {method_name}\n"
                f"Error: Invalid attribute: {str(exc)}"
            ) from exc


# ============================================================
# Main (Usage Example)
# ============================================================

if __name__ == "__main__":
    """
    Simple execution example.
    """

    try:
        attributes = ["id", "title", "fields"]

        fragment = QueryBuilder.buildCardAttributes(attributes)

        print("Generated GraphQL fragment:")
        print(fragment)

    except ValidationError as error:
        print("Error occurred:")
        print(error)
