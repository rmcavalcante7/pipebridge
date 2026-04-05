# ============================================================
# Dependencies
# ============================================================
from collections.abc import Callable
from typing import List

from pipebridge.workflow.context.executionContext import ExecutionContext
from pipebridge.workflow.policies.baseExecutionPolicy import BaseExecutionPolicy
from pipebridge.workflow.steps.baseStep import BaseStep


class PolicyChain(BaseExecutionPolicy):
    """
    Composes multiple execution policies in deterministic order.

    The first policy in the list becomes the outermost wrapper and the
    last policy becomes the innermost wrapper around step execution.

    :param policies: List[BaseExecutionPolicy] = Policies to compose

    :example:
        >>> chain = PolicyChain([])
        >>> isinstance(chain, PolicyChain)
        True
    """

    def __init__(self, policies: List[BaseExecutionPolicy]) -> None:
        """
        Initialize PolicyChain.

        :param policies: List[BaseExecutionPolicy] = Policies to compose

        :return: None

        :example:
            >>> chain = PolicyChain([])
            >>> isinstance(chain, PolicyChain)
            True
        """
        self._policies: List[BaseExecutionPolicy] = policies or []

    def execute(
        self, step: BaseStep, context: ExecutionContext, next_call: Callable[[], None]
    ) -> None:
        """
        Execute all policies around the wrapped call.

        :param step: BaseStep = Step being executed
        :param context: ExecutionContext = Shared workflow context
        :param next_call: Callable[[], None] = Wrapped execution callable

        :return: None

        :example:
            >>> order = []
            >>> class RecordingPolicy(BaseExecutionPolicy):
            ...     def __init__(self, name):
            ...         self._name = name
            ...     def execute(self, step, context, next_call):
            ...         order.append(f"before:{self._name}")
            ...         next_call()
            ...         order.append(f"after:{self._name}")
            >>> class ExampleStep(BaseStep):
            ...     def execute(self, context):
            ...         order.append("step")
            >>> chain = PolicyChain([RecordingPolicy("a"), RecordingPolicy("b")])
            >>> chain.execute(ExampleStep(), ExecutionContext(), lambda: order.append("action"))
            >>> order[:2]
            ['before:a', 'before:b']
        """
        composed_call = next_call

        for policy in reversed(self._policies):
            current_call = composed_call

            def wrapper(
                current_policy: BaseExecutionPolicy = policy,
                current_next: Callable[[], None] = current_call,
            ) -> None:
                """
                Execute one policy layer around the current composed callable.

                :param current_policy: BaseExecutionPolicy = Current policy layer
                :param current_next: Callable[[], None] = Next callable in the chain
                """
                current_policy.execute(step, context, current_next)

            composed_call = wrapper

        composed_call()
