from dataclasses import dataclass


@dataclass
class RetryConfig:
    """
    Configuration for retry behavior.

    :param max_retries: int
    :param base_delay: float
    """
    max_retries: int = 3
    base_delay: float = 0.5