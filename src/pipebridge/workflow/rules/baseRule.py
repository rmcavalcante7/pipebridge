# ============================================================
# Dependencies
# ============================================================
from abc import ABC, abstractmethod
from typing import Any


class BaseRule(ABC):
    """
    Abstract base class for reusable workflow validation rules.

    A rule represents a business or execution constraint that must be
    satisfied before workflow steps are executed.

    Rules are intentionally generic and independent from any specific
    domain context. Concrete flows should provide a specialized context
    object that extends :class:`ExecutionContext`.

    :attribute priority: int = Execution priority (lower values run first)

    :example:
        >>> callable(BaseRule.execute)
        True
    """

    priority: int = 100

    def __str__(self) -> str:
        """
        Return a human-readable representation.

        :return: str = String representation

        :example:
            >>> class ExampleRule(BaseRule):
            ...     def execute(self, context):
            ...         return None
            >>> str(ExampleRule())
            '<ExampleRule priority=100>'
        """
        return f"<{self.__class__.__name__} priority={self.priority}>"

    def __repr__(self) -> str:
        """
        Return a developer-friendly representation.

        :return: str = Debug representation

        :example:
            >>> class ExampleRule(BaseRule):
            ...     def execute(self, context):
            ...         return None
            >>> "ExampleRule" in repr(ExampleRule())
            True
        """
        return f"<{self.__class__.__name__}() priority={self.priority}>"

    @abstractmethod
    def execute(self, context: Any) -> None:
        """
        Execute rule validation.

        :param context: Any = Shared execution context

        :return: None

        :raises ValidationError:
            When the rule is violated

        :example:
            >>> callable(BaseRule.execute)
            True
        """
        raise NotImplementedError
