# ============================================================
# Dependencies
# ============================================================
from abc import ABC, abstractmethod

from pipebridge.workflow.context.executionContext import ExecutionContext
from pipebridge.workflow.policies.baseExecutionPolicy import BaseExecutionPolicy
from pipebridge.workflow.steps.baseStep import BaseStep


class PolicyResolver(ABC):
    """
    Resolves the policy to be applied for each step execution.

    This abstraction allows the engine to remain unaware of policy
    details while still enabling different steps to receive different
    execution behavior.

    :example:
        >>> callable(PolicyResolver.resolve)
        True
    """

    @abstractmethod
    def resolve(self, step: BaseStep, context: ExecutionContext) -> BaseExecutionPolicy:
        """
        Resolve the policy that should wrap the provided step execution.

        :param step: BaseStep = Step being executed
        :param context: ExecutionContext = Shared workflow context

        :return: BaseExecutionPolicy = Policy to apply

        :example:
            >>> callable(PolicyResolver.resolve)
            True
        """
        raise NotImplementedError
