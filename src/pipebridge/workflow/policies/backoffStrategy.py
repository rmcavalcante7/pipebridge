# ============================================================
# Dependencies
# ============================================================
from abc import ABC, abstractmethod

from pipebridge.workflow.config.retryConfig import RetryConfig


class BackoffStrategy(ABC):
    """
    Contract for delay calculation between retry attempts.

    :example:
        >>> callable(BackoffStrategy.getDelay)
        True
    """

    @abstractmethod
    def getDelay(self, config: RetryConfig, attempt: int) -> float:
        """
        Return delay for the given attempt.

        :param config: RetryConfig = Retry behavior configuration
        :param attempt: int = Current attempt number (1-based)

        :return: float = Delay in seconds

        :raises ValueError:
            When attempt is invalid
        """
        raise NotImplementedError


class ExponentialBackoffStrategy(BackoffStrategy):
    """
    Exponential backoff strategy based on ``base_delay * 2^(attempt-1)``.

    :example:
        >>> strategy = ExponentialBackoffStrategy()
        >>> round(strategy.getDelay(RetryConfig(base_delay=0.5), 2), 2)
        1.0
    """

    def getDelay(self, config: RetryConfig, attempt: int) -> float:
        """
        Calculate exponential backoff delay.

        :param config: RetryConfig = Retry behavior configuration
        :param attempt: int = Current attempt number (1-based)

        :return: float = Delay in seconds

        :raises ValueError:
            When attempt is invalid

        :example:
            >>> strategy = ExponentialBackoffStrategy()
            >>> strategy.getDelay(RetryConfig(base_delay=0.1), 1)
            0.1
        """
        if attempt <= 0:
            raise ValueError("attempt must be >= 1")

        return float(config.base_delay * (2 ** (attempt - 1)))
