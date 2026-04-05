# ============================================================
# Dependencies
# ============================================================
import time
from enum import Enum


class CircuitState(Enum):
    """
    Represents circuit breaker states.

    :example:
        >>> CircuitState.CLOSED.value
        'closed'
    """

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """
    Implements the circuit breaker pattern for workflow execution.

    :param failure_threshold: int = Failures required to open the circuit
    :param recovery_timeout: float = Seconds before half-open transition

    :example:
        >>> breaker = CircuitBreaker(3, 5.0)
        >>> breaker.state == CircuitState.CLOSED
        True
    """

    def __init__(
        self, failure_threshold: int = 3, recovery_timeout: float = 10.0
    ) -> None:
        """
        Initialize CircuitBreaker.

        :param failure_threshold: int = Failures required to open the circuit
        :param recovery_timeout: float = Seconds before half-open transition

        :return: None

        :raises ValueError:
            When parameters are invalid

        :example:
            >>> breaker = CircuitBreaker()
            >>> breaker.failureCount
            0
        """
        if failure_threshold <= 0:
            raise ValueError("failure_threshold must be > 0")

        if recovery_timeout <= 0:
            raise ValueError("recovery_timeout must be > 0")

        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._failure_count = 0
        self._last_failure_time = 0.0
        self._state = CircuitState.CLOSED

    @property
    def state(self) -> CircuitState:
        """
        Return the current circuit state.

        :return: CircuitState = Current state

        :example:
            >>> CircuitBreaker().state == CircuitState.CLOSED
            True
        """
        return self._state

    @property
    def failureCount(self) -> int:
        """
        Return the current failure count.

        :return: int = Current failure count

        :example:
            >>> CircuitBreaker().failureCount
            0
        """
        return self._failure_count

    def canExecute(self) -> bool:
        """
        Determine whether execution is allowed.

        :return: bool = True when execution is allowed

        :example:
            >>> isinstance(CircuitBreaker().canExecute(), bool)
            True
        """
        if self._state == CircuitState.CLOSED:
            return True

        if self._state == CircuitState.OPEN:
            if self._isRecoveryTimeElapsed():
                self._state = CircuitState.HALF_OPEN
                return True
            return False

        return self._state == CircuitState.HALF_OPEN

    def onSuccess(self) -> None:
        """
        Record successful execution and close the circuit.

        :return: None

        :example:
            >>> breaker = CircuitBreaker()
            >>> breaker.onSuccess()
            >>> breaker.state == CircuitState.CLOSED
            True
        """
        self._failure_count = 0
        self._state = CircuitState.CLOSED

    def onFailure(self) -> None:
        """
        Record a failure and update circuit state.

        :return: None

        :example:
            >>> breaker = CircuitBreaker(failure_threshold=1, recovery_timeout=1.0)
            >>> breaker.onFailure()
            >>> breaker.state == CircuitState.OPEN
            True
        """
        self._failure_count += 1
        self._last_failure_time = time.time()

        if self._failure_count >= self._failure_threshold:
            self._state = CircuitState.OPEN

    def _isRecoveryTimeElapsed(self) -> bool:
        """
        Determine whether the recovery timeout has elapsed.

        :return: bool = True when timeout has elapsed
        """
        return (time.time() - self._last_failure_time) >= self._recovery_timeout

    def __str__(self) -> str:
        """
        Return a human-readable representation.

        :return: str = String representation

        :example:
            >>> "CircuitBreaker" in str(CircuitBreaker())
            True
        """
        return (
            f"<CircuitBreaker state={self._state.value} "
            f"failures={self._failure_count}>"
        )

    def __repr__(self) -> str:
        """
        Return a developer-friendly representation.

        :return: str = Debug representation

        :example:
            >>> "CircuitBreaker" in repr(CircuitBreaker())
            True
        """
        return (
            f"<CircuitBreaker(state={self._state}, " f"failures={self._failure_count})>"
        )
