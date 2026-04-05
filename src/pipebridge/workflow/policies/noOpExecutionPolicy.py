# ============================================================
# Dependencies
# ============================================================
from collections.abc import Callable

from pipebridge.workflow.context.executionContext import ExecutionContext
from pipebridge.workflow.policies.baseExecutionPolicy import BaseExecutionPolicy
from pipebridge.workflow.steps.baseStep import BaseStep


class NoOpExecutionPolicy(BaseExecutionPolicy):
    """
    Policy that simply forwards execution with no additional behavior.

    :example:
        >>> callable(NoOpExecutionPolicy.execute)
        True
    """

    def execute(
        self, step: BaseStep, context: ExecutionContext, next_call: Callable[[], None]
    ) -> None:
        """
        Execute the wrapped call without modification.

        :param step: BaseStep = Step being executed
        :param context: ExecutionContext = Shared workflow context
        :param next_call: Callable[[], None] = Wrapped execution callable

        :return: None

        :example:
            >>> called = {"value": False}
            >>> def action():
            ...     called["value"] = True
            >>> class ExampleStep(BaseStep):
            ...     def execute(self, context):
            ...         return None
            >>> NoOpExecutionPolicy().execute(ExampleStep(), ExecutionContext(), action)
            >>> called["value"]
            True
        """
        next_call()
