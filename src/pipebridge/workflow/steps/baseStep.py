# ============================================================
# Dependencies
# ============================================================
from abc import ABC, abstractmethod
from typing import Any


class BaseStep(ABC):
    """
    Abstract base class for reusable workflow steps.

    A step represents one unit of execution within a workflow.

    This class intentionally contains no retry or resilience policy.
    Execution policies are applied externally by the execution engine.

    Concrete steps may optionally expose tags or an execution profile
    so that policy resolvers can choose the appropriate policy without
    coupling the step to a specific resilience implementation.

    :attribute tags: tuple[str, ...] = Declarative step tags
    :attribute execution_profile: str = Optional policy resolution hint

    :example:
        >>> callable(BaseStep.execute)
        True
    """

    tags: tuple[str, ...] = ()
    execution_profile: str = "default"

    @abstractmethod
    def execute(self, context: Any) -> None:
        """
        Execute step logic.

        :param context: Any = Shared workflow context

        :return: None

        :raises Exception:
            When step execution fails

        :example:
            >>> callable(BaseStep.execute)
            True
        """
        raise NotImplementedError

    def getExecutionKey(self) -> str:
        """
        Return a stable identifier for policy state isolation.

        :return: str = Stable execution key

        :example:
            >>> class ExampleStep(BaseStep):
            ...     def execute(self, context):
            ...         return None
            >>> ExampleStep().getExecutionKey()
            'ExampleStep'
        """
        return self.__class__.__name__

    def __str__(self) -> str:
        """
        Return a human-readable representation.

        :return: str = String representation

        :example:
            >>> class ExampleStep(BaseStep):
            ...     def execute(self, context):
            ...         return None
            >>> str(ExampleStep())
            '<ExampleStep profile=default>'
        """
        return f"<{self.__class__.__name__} " f"profile={self.execution_profile}>"

    def __repr__(self) -> str:
        """
        Return a developer-friendly representation.

        :return: str = Debug representation

        :example:
            >>> class ExampleStep(BaseStep):
            ...     def execute(self, context):
            ...         return None
            >>> "ExampleStep" in repr(ExampleStep())
            True
        """
        return (
            f"<{self.__class__.__name__}("
            f"profile={self.execution_profile}, tags={self.tags})>"
        )
