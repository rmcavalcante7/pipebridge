# ============================================================
# Dependencies
# ============================================================
from abc import ABC, abstractmethod
from collections.abc import Callable

from pipebridge.workflow.context.executionContext import ExecutionContext
from pipebridge.workflow.steps.baseStep import BaseStep


class BaseExecutionPolicy(ABC):
    """
    Contract for execution policies applied around step execution.

    Policies are wrappers that can add orthogonal concerns such as
    retry, jitter, circuit breaker, logging, metrics, or timeouts
    without coupling those concerns to the step or the engine.

    :example:
        >>> callable(BaseExecutionPolicy.execute)
        True
    """

    @abstractmethod
    def execute(
        self, step: BaseStep, context: ExecutionContext, next_call: Callable[[], None]
    ) -> None:
        """
        Execute a policy around the provided call.

        :param step: BaseStep = Step being executed
        :param context: ExecutionContext = Shared workflow context
        :param next_call: Callable[[], None] = Next callable in the chain

        :return: None

        :raises Exception:
            When policy or wrapped execution fails

        :example:
            >>> callable(BaseExecutionPolicy.execute)
            True
        """
        raise NotImplementedError
