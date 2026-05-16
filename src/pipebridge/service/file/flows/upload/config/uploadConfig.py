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
    :param validate_field_in_current_phase: bool = Whether upload field
        existence must be validated strictly against the card current phase
        schema. When disabled, the field may exist anywhere in the pipe schema,
        including start form or another phase.

    :example:
        >>> cfg = UploadConfig()
        >>> isinstance(cfg.retry, RetryConfig)
        True
    """

    def __init__(
        self,
        retry: Optional[RetryConfig] = None,
        circuit: Optional[CircuitBreakerConfig] = None,
        validate_field_in_current_phase: bool = True,
    ) -> None:
        """
        Initialize UploadConfig.

        :param retry: Optional[RetryConfig] = Retry configuration
        :param circuit: Optional[CircuitBreakerConfig] = Circuit breaker configuration
        :param validate_field_in_current_phase: bool = Whether field existence
            is validated only against the current phase schema

        :return: None

        :example:
            >>> cfg = UploadConfig()
            >>> isinstance(cfg.circuit, CircuitBreakerConfig)
            True
        """
        self.retry: RetryConfig = retry or RetryConfig()
        self.circuit: CircuitBreakerConfig = circuit or CircuitBreakerConfig()
        self.validate_field_in_current_phase: bool = validate_field_in_current_phase
