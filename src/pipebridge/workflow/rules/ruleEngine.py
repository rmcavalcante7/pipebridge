# ============================================================
# Dependencies
# ============================================================
from typing import List

from pipebridge.exceptions import PipefyError, ValidationError
from pipebridge.exceptions.workflow import RuleExecutionError, WorkflowError
from pipebridge.workflow.context.executionContext import ExecutionContext
from pipebridge.workflow.rules.baseRule import BaseRule


class RuleEngine:
    """
    Executes workflow rules in deterministic priority order.

    This engine is intentionally generic and can be reused by multiple
    flows that require pre-execution validation.

    :param rules: List[BaseRule] = Rules to be executed

    :example:
        >>> callable(RuleEngine.execute)
        True
    """

    def __init__(self, rules: List[BaseRule]) -> None:
        """
        Initialize RuleEngine.

        :param rules: List[BaseRule] = Rules to be executed

        :return: None

        :example:
            >>> engine = RuleEngine([])
            >>> isinstance(engine, RuleEngine)
            True
        """
        self._rules: List[BaseRule] = sorted(
            rules or [], key=lambda rule: rule.priority
        )

    def execute(self, context: ExecutionContext) -> None:
        """
        Execute all configured rules sequentially.

        :param context: ExecutionContext = Shared workflow context

        :return: None

        :raises ValidationError:
            When a business validation rule fails
        :raises RuleExecutionError:
            When a rule fails technically during execution

        :example:
            >>> class ExampleRule(BaseRule):
            ...     def execute(self, context):
            ...         context.metadata["validated"] = True
            >>> context = ExecutionContext()
            >>> RuleEngine([ExampleRule()]).execute(context)
            >>> context.metadata["validated"]
            True
        """
        for rule in self._rules:
            try:
                rule.execute(context)
            except PipefyError, WorkflowError:
                raise
            except Exception as exc:
                raise RuleExecutionError(
                    message=str(exc),
                    class_name=self.__class__.__name__,
                    method_name="execute",
                    cause=exc,
                    context={"rule_name": rule.__class__.__name__},
                    retryable=getattr(exc, "retryable", False),
                ) from exc

    def __str__(self) -> str:
        """
        Return a human-readable representation.

        :return: str = String representation

        :example:
            >>> str(RuleEngine([]))
            '<RuleEngine rules=0>'
        """
        return f"<RuleEngine rules={len(self._rules)}>"

    def __repr__(self) -> str:
        """
        Return a developer-friendly representation.

        :return: str = Debug representation

        :example:
            >>> "RuleEngine" in repr(RuleEngine([]))
            True
        """
        return f"<RuleEngine(rules={self._rules})>"
