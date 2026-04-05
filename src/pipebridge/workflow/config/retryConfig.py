# ============================================================
# Dependencies
# ============================================================
from dataclasses import dataclass


@dataclass
class RetryConfig:
    """
    Configuration for retry behavior.

    :param max_retries: int = Maximum number of execution attempts
    :param base_delay: float = Base delay used by backoff strategies

    :example:
        >>> config = RetryConfig(max_retries=2, base_delay=0.1)
        >>> config.max_retries
        2
    """

    max_retries: int = 3
    base_delay: float = 0.5
