# ============================================================
# Dependencies
# ============================================================
from dataclasses import dataclass


@dataclass
class CircuitBreakerConfig:
    """
    Configuration for circuit breaker behavior.

    :param failure_threshold: int = Failures required to open the circuit
    :param recovery_timeout: float = Seconds before half-open transition

    :example:
        >>> config = CircuitBreakerConfig(failure_threshold=2, recovery_timeout=1.0)
        >>> config.failure_threshold
        2
    """

    failure_threshold: int = 3
    recovery_timeout: float = 10.0
