from dataclasses import dataclass


@dataclass
class CircuitBreakerConfig:
    """
    Configuration for circuit breaker.

    :param failure_threshold: int
    :param recovery_timeout: float
    """
    failure_threshold: int = 3
    recovery_timeout: float = 10.0