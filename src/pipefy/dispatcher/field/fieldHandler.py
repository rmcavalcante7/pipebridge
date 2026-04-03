from abc import ABC, abstractmethod
from typing import Any


class FieldHandler(ABC):
    """
    Base class for all field handlers.

    Each handler is responsible for generating the correct GraphQL mutation
    for a specific Pipefy field type.

    :example:
        >>> callable(FieldHandler.buildMutation)
        True
    """

    @abstractmethod
    def buildMutation(
        self,
        card_id: str,
        field_id: str,
        value: Any
    ) -> str:
        """
        Builds a GraphQL mutation string.

        :param card_id: str = Card identifier
        :param field_id: str = Field identifier
        :param value: Any = Field value

        :return: str = GraphQL mutation

        :raises ValidationError:
            When value is invalid
        """
        raise NotImplementedError