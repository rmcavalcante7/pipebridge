# ============================================================
# Dependencies
# ============================================================
import random
from abc import ABC, abstractmethod


class JitterStrategy(ABC):
    """
    Contract for adding jitter to a computed backoff delay.

    :example:
        >>> callable(JitterStrategy.apply)
        True
    """

    @abstractmethod
    def apply(self, delay: float) -> float:
        """
        Apply jitter to the provided delay.

        :param delay: float = Backoff delay before jitter

        :return: float = Jitter-adjusted delay
        """
        raise NotImplementedError


class FullJitterStrategy(JitterStrategy):
    """
    Full jitter strategy that returns a random delay in ``[0, delay]``.

    :example:
        >>> strategy = FullJitterStrategy()
        >>> 0.0 <= strategy.apply(1.0) <= 1.0
        True
    """

    def apply(self, delay: float) -> float:
        """
        Apply full jitter to the provided delay.

        :param delay: float = Backoff delay before jitter

        :return: float = Jitter-adjusted delay

        :example:
            >>> strategy = FullJitterStrategy()
            >>> 0.0 <= strategy.apply(0.5) <= 0.5
            True
        """
        if delay <= 0:
            return 0.0

        return random.uniform(0, delay)
