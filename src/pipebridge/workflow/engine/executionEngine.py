# ============================================================
# Dependencies
# ============================================================
from typing import List, Optional

from pipebridge.exceptions import PipefyError
from pipebridge.exceptions.workflow import StepExecutionError, WorkflowError
from pipebridge.workflow.context.executionContext import ExecutionContext
from pipebridge.workflow.policies.policyResolver import PolicyResolver
from pipebridge.workflow.policies.staticPolicyResolver import StaticPolicyResolver
from pipebridge.workflow.steps.baseStep import BaseStep


class ExecutionEngine:
    """
    Sequential engine that executes steps under resolved policies.

    The engine is intentionally unaware of concrete resilience or
    observability rules. It only asks a resolver which policy must be
    applied to each step and then delegates wrapped execution to that
    policy.

    :param steps: List[BaseStep] = Steps to execute
    :param policy_resolver: Optional[PolicyResolver] = Policy resolver applied per step

    :example:
        >>> callable(ExecutionEngine.execute)
        True
    """

    def __init__(
        self, steps: List[BaseStep], policy_resolver: Optional[PolicyResolver] = None
    ) -> None:
        """
        Initialize ExecutionEngine.

        :param steps: List[BaseStep] = Steps to execute
        :param policy_resolver: Optional[PolicyResolver] = Policy resolver applied per step

        :return: None

        :raises ValueError:
            When steps is None

        :example:
            >>> engine = ExecutionEngine([])
            >>> isinstance(engine, ExecutionEngine)
            True
        """
        if steps is None:
            raise ValueError("steps cannot be None")

        self._steps: List[BaseStep] = steps
        self._policy_resolver: PolicyResolver = (
            policy_resolver or StaticPolicyResolver()
        )

    def execute(self, context: ExecutionContext) -> None:
        """
        Execute all configured steps under resolved policies.

        :param context: ExecutionContext = Shared workflow context

        :return: None

        :raises WorkflowError:
            When any step or policy fails semantically
        :raises StepExecutionError:
            When step execution fails technically

        :example:
            >>> calls = []
            >>> class ExampleStep(BaseStep):
            ...     def execute(self, context):
            ...         calls.append("step")
            >>> ExecutionEngine([ExampleStep()]).execute(ExecutionContext())
            >>> calls
            ['step']
        """
        for step in self._steps:
            policy = self._policy_resolver.resolve(step=step, context=context)

            def execute_step() -> None:
                step.execute(context)

            try:
                policy.execute(
                    step=step,
                    context=context,
                    next_call=execute_step,
                )
            except PipefyError, WorkflowError:
                raise
            except Exception as exc:
                raise StepExecutionError(
                    message=str(exc),
                    class_name=self.__class__.__name__,
                    method_name="execute",
                    cause=exc,
                    context={"step_name": step.__class__.__name__},
                    retryable=getattr(exc, "retryable", False),
                ) from exc

    def __str__(self) -> str:
        """
        Return a human-readable representation.

        :return: str = String representation

        :example:
            >>> str(ExecutionEngine([]))
            '<ExecutionEngine steps=0>'
        """
        return f"<ExecutionEngine steps={len(self._steps)}>"

    def __repr__(self) -> str:
        """
        Return a developer-friendly representation.

        :return: str = Debug representation

        :example:
            >>> "ExecutionEngine" in repr(ExecutionEngine([]))
            True
        """
        return f"<ExecutionEngine(steps={self._steps})>"
