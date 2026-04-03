from typing import Any

from pipefy.dispatcher.field.fieldHandlerRegistry import FieldHandlerRegistry


class FieldDispatcher:
    """
    Dispatches field updates to the correct handler.

    :param registry: FieldHandlerRegistry = Handler registry

    :example:
        >>> dispatcher = FieldDispatcher(FieldHandlerRegistry())
        >>> callable(dispatcher.dispatch)
        True
    """

    def __init__(self, registry: FieldHandlerRegistry) -> None:
        """
        Initializes the dispatcher.

        :param registry: FieldHandlerRegistry = Handler registry
        """
        self._registry: FieldHandlerRegistry = registry

    def dispatch(
        self,
        card_id: str,
        field_id: str,
        field_type: str,
        value: Any
    ) -> str:
        """
        Dispatches field update to the appropriate handler.

        :param card_id: str = Card identifier
        :param field_id: str = Field identifier
        :param field_type: str = Field type
        :param value: Any = Field value

        :return: str = GraphQL mutation

        :raises ValidationError:
            When handler is not found or value is invalid

        :example:
            >>> dispatcher = FieldDispatcher(FieldHandlerRegistry())
            >>> callable(dispatcher.dispatch)
            True
        """
        handler = self._registry.getHandler(field_type)

        return handler.buildMutation(
            card_id=card_id,
            field_id=field_id,
            value=value
        )