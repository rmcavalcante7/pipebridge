# ============================================================
# Dependencies
# ============================================================
import time
from collections.abc import Callable

from pipebridge.workflow.config.retryConfig import RetryConfig
from pipebridge.workflow.context.executionContext import ExecutionContext
from pipebridge.workflow.policies.backoffStrategy import (
    BackoffStrategy,
    ExponentialBackoffStrategy,
)
from pipebridge.workflow.policies.baseExecutionPolicy import BaseExecutionPolicy
from pipebridge.workflow.policies.jitterStrategy import (
    FullJitterStrategy,
    JitterStrategy,
)
from pipebridge.workflow.steps.baseStep import BaseStep
from pipebridge.exceptions.workflow import RetryExhaustedError


class RetryPolicy(BaseExecutionPolicy):
    """
    Execution policy that retries wrapped execution according to a policy.

    This policy is independent from the engine and from the step. It only
    requires a retry configuration, a retry condition, and optional backoff
    and jitter strategies.

    :param config: RetryConfig = Retry behavior configuration
    :param retry_condition: Callable[[Exception], bool] = Predicate deciding whether to retry
    :param backoff_strategy: BackoffStrategy | None = Delay calculation strategy
    :param jitter_strategy: JitterStrategy | None = Delay randomization strategy
    :param sleeper: Callable[[float], None] | None = Sleep function for delays

    :example:
        >>> policy = RetryPolicy(
        ...     config=RetryConfig(max_retries=1, base_delay=0.0),
        ...     retry_condition=lambda exc: False
        ... )
        >>> isinstance(policy, RetryPolicy)
        True
    """

    def __init__(
        self,
        config: RetryConfig,
        retry_condition: Callable[[Exception], bool],
        backoff_strategy: BackoffStrategy | None = None,
        jitter_strategy: JitterStrategy | None = None,
        sleeper: Callable[[float], None] | None = None,
    ) -> None:
        """
        Initialize RetryPolicy.

        :param config: RetryConfig = Retry behavior configuration
        :param retry_condition: Callable[[Exception], bool] = Predicate deciding whether to retry
        :param backoff_strategy: BackoffStrategy | None = Delay calculation strategy
        :param jitter_strategy: JitterStrategy | None = Delay randomization strategy
        :param sleeper: Callable[[float], None] | None = Sleep function for delays

        :return: None

        :example:
            >>> policy = RetryPolicy(
            ...     config=RetryConfig(),
            ...     retry_condition=lambda exc: True
            ... )
            >>> isinstance(policy, RetryPolicy)
            True
        """
        self._config: RetryConfig = config
        self._retry_condition = retry_condition
        self._backoff_strategy = backoff_strategy or ExponentialBackoffStrategy()
        self._jitter_strategy = jitter_strategy or FullJitterStrategy()
        self._sleeper = sleeper or time.sleep

    def execute(
        self, step: BaseStep, context: ExecutionContext, next_call: Callable[[], None]
    ) -> None:
        """
        Execute wrapped call with retry behavior.

        :param step: BaseStep = Step being executed
        :param context: ExecutionContext = Shared workflow context
        :param next_call: Callable[[], None] = Wrapped execution callable

        :return: None

        :raises Exception:
            When execution fails and should not be retried
        :raises Exception:
            When maximum retries are exhausted

        :example:
            >>> state = {"attempts": 0}
            >>> def flaky():
            ...     state["attempts"] += 1
            ...     if state["attempts"] < 2:
            ...         raise RuntimeError("temporary")
            >>> class ExampleStep(BaseStep):
            ...     def execute(self, context):
            ...         return None
            >>> policy = RetryPolicy(
            ...     config=RetryConfig(max_retries=2, base_delay=0.0),
            ...     retry_condition=lambda exc: "temporary" in str(exc),
            ...     sleeper=lambda delay: None
            ... )
            >>> policy.execute(ExampleStep(), ExecutionContext(), flaky)
            >>> state["attempts"]
            2
        """
        max_attempts = self._config.max_retries

        for attempt in range(1, max_attempts + 1):
            try:
                next_call()
                return
            except Exception as exc:
                if attempt == max_attempts:
                    raise RetryExhaustedError(
                        message=str(exc),
                        class_name=self.__class__.__name__,
                        method_name="execute",
                        context={
                            "step_key": step.getExecutionKey(),
                            "attempts": attempt,
                        },
                        cause=exc,
                    ) from exc

                if not self._retry_condition(exc):
                    raise

                delay = self._backoff_strategy.getDelay(self._config, attempt)
                delay = self._jitter_strategy.apply(delay)
                self._sleeper(delay)
