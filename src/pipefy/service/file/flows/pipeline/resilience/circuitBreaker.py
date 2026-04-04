# ============================================================
# Dependencies
# ============================================================
import time
from enum import Enum


class CircuitState(Enum):
    """
    Represents circuit breaker states.
    """

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """
    Implements Circuit Breaker pattern for fault tolerance.

    PURPOSE:
        Prevent repeated execution of failing operations,
        protecting external systems and improving system stability.

    STATES:
        CLOSED:
            - Normal operation
            - Failures are counted

        OPEN:
            - Execution blocked
            - After threshold reached

        HALF_OPEN:
            - Test mode
            - Allows limited execution

    :param failure_threshold: int = Failures before opening circuit
    :param recovery_timeout: float = Time before retry (seconds)

    :example:
        >>> cb = CircuitBreaker(3, 5)
        >>> cb.state == CircuitState.CLOSED
        True
    """

    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout: float = 10.0
    ) -> None:
        """
        Initializes CircuitBreaker.

        :param failure_threshold: int
        :param recovery_timeout: float

        :raises ValueError:
            When parameters are invalid
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
        Returns current circuit state.

        This is a read-only property to expose internal state safely.

        :return: CircuitState

        :example:
            >>> cb = CircuitBreaker()
            >>> cb.state == CircuitState.CLOSED
            True
        """
        return self._state

    @property
    def failureCount(self) -> int:
        """
        Returns current failure count.

        :return: int
        """
        return self._failure_count

    def isOpen(self) -> bool:
        """
        Checks if circuit is open.

        :return: bool
        """
        return self._state == CircuitState.OPEN
    # ============================================================
    # Public Methods
    # ============================================================

    def canExecute(self) -> bool:
        """
        Determines whether execution is allowed.

        :return: bool

        :example:
            >>> cb = CircuitBreaker()
            >>> isinstance(cb.canExecute(), bool)
            True
        """
        if self._state == CircuitState.CLOSED:
            return True

        if self._state == CircuitState.OPEN:
            if self._isRecoveryTimeElapsed():
                self._state = CircuitState.HALF_OPEN
                return True
            return False

        if self._state == CircuitState.HALF_OPEN:
            return True

        return False

    def onSuccess(self) -> None:
        """
        Resets circuit after successful execution.
        """
        self._failure_count = 0
        self._state = CircuitState.CLOSED

    def onFailure(self) -> None:
        """
        Records failure and updates circuit state.
        """
        self._failure_count += 1
        self._last_failure_time = time.time()

        if self._failure_count >= self._failure_threshold:
            self._state = CircuitState.OPEN

    # ============================================================
    # Internal Methods
    # ============================================================

    def _isRecoveryTimeElapsed(self) -> bool:
        return (time.time() - self._last_failure_time) >= self._recovery_timeout

    # ============================================================
    # Dunder Methods
    # ============================================================

    def __str__(self) -> str:
        return f"<CircuitBreaker state={self._state.value} failures={self._failure_count}>"

    def __repr__(self) -> str:
        return f"<CircuitBreaker(state={self._state}, failures={self._failure_count})>"