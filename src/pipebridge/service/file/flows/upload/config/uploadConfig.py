# ============================================================
# Dependencies
# ============================================================
from typing import Optional

from pipebridge.workflow.config.retryConfig import RetryConfig
from pipebridge.workflow.config.circuitBreakerConfig import (
    CircuitBreakerConfig,
)


class UploadConfig:
    """
    Configuration for upload flow execution policies.

    This object preserves the existing public API while internally
    supporting the refactored workflow/policy engine.

    :param retry: Optional[RetryConfig] = Retry configuration
    :param circuit: Optional[CircuitBreakerConfig] = Circuit breaker configuration

    :example:
        >>> cfg = UploadConfig()
        >>> isinstance(cfg.retry, RetryConfig)
        True
    """

    def __init__(
        self,
        retry: Optional[RetryConfig] = None,
        circuit: Optional[CircuitBreakerConfig] = None,
    ) -> None:
        """
        Initialize UploadConfig.

        :param retry: Optional[RetryConfig] = Retry configuration
        :param circuit: Optional[CircuitBreakerConfig] = Circuit breaker configuration

        :return: None

        :example:
            >>> cfg = UploadConfig()
            >>> isinstance(cfg.circuit, CircuitBreakerConfig)
            True
        """
        self.retry: RetryConfig = retry or RetryConfig()
        self.circuit: CircuitBreakerConfig = circuit or CircuitBreakerConfig()
