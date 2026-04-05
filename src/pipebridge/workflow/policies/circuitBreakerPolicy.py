# ============================================================
# Dependencies
# ============================================================
from collections.abc import Callable
from typing import Dict

from pipebridge.workflow.config.circuitBreakerConfig import CircuitBreakerConfig
from pipebridge.workflow.context.executionContext import ExecutionContext
from pipebridge.workflow.policies.baseExecutionPolicy import BaseExecutionPolicy
from pipebridge.workflow.resilience.circuitBreaker import CircuitBreaker
from pipebridge.workflow.steps.baseStep import BaseStep
from pipebridge.exceptions.workflow import CircuitBreakerOpenError


class CircuitBreakerPolicy(BaseExecutionPolicy):
    """
    Execution policy that isolates failures using circuit breakers.

    A circuit breaker is maintained per step execution key so that one
    repeatedly failing step does not affect unrelated steps.

    :param config: CircuitBreakerConfig = Circuit breaker configuration

    :example:
        >>> policy = CircuitBreakerPolicy(CircuitBreakerConfig())
        >>> isinstance(policy, CircuitBreakerPolicy)
        True
    """

    def __init__(
        self,
        config: CircuitBreakerConfig,
        breakers: Dict[str, CircuitBreaker] | None = None,
    ) -> None:
        """
        Initialize CircuitBreakerPolicy.

        :param config: CircuitBreakerConfig = Circuit breaker configuration
        :param breakers: Dict[str, CircuitBreaker] | None = Optional shared breaker store

        :return: None

        :example:
            >>> policy = CircuitBreakerPolicy(CircuitBreakerConfig())
            >>> isinstance(policy, CircuitBreakerPolicy)
            True
        """
        self._config: CircuitBreakerConfig = config
        self._breakers: Dict[str, CircuitBreaker] = (
            breakers if breakers is not None else {}
        )

    def execute(
        self, step: BaseStep, context: ExecutionContext, next_call: Callable[[], None]
    ) -> None:
        """
        Execute wrapped call under circuit breaker protection.

        :param step: BaseStep = Step being executed
        :param context: ExecutionContext = Shared workflow context
        :param next_call: Callable[[], None] = Wrapped execution callable

        :return: None

        :raises CircuitBreakerOpenError:
            When the circuit is open for the step

        :example:
            >>> class ExampleStep(BaseStep):
            ...     def execute(self, context):
            ...         return None
            >>> policy = CircuitBreakerPolicy(CircuitBreakerConfig())
            >>> policy.execute(ExampleStep(), ExecutionContext(), lambda: None)
        """
        breaker = self._getBreaker(step)

        if not breaker.canExecute():
            raise CircuitBreakerOpenError(
                message=f"Circuit OPEN for step '{step.getExecutionKey()}'",
                class_name=self.__class__.__name__,
                method_name="execute",
                context={"step_key": step.getExecutionKey()},
            )

        try:
            next_call()
            breaker.onSuccess()
        except Exception:
            breaker.onFailure()
            raise

    def _getBreaker(self, step: BaseStep) -> CircuitBreaker:
        """
        Retrieve or create a breaker for the provided step.

        :param step: BaseStep = Step being executed

        :return: CircuitBreaker = Step-specific circuit breaker
        """
        key = step.getExecutionKey()

        if key not in self._breakers:
            self._breakers[key] = CircuitBreaker(
                failure_threshold=self._config.failure_threshold,
                recovery_timeout=self._config.recovery_timeout,
            )

        return self._breakers[key]
