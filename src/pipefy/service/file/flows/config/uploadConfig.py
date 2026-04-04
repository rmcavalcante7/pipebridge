from dataclasses import dataclass, field

from pipefy.service.file.flows.config.retryConfig import RetryConfig
from pipefy.service.file.flows.config.circuitBreakerConfig import CircuitBreakerConfig


@dataclass
class UploadConfig:
    """
    Configuration for upload flow behavior.

    :param retry: RetryConfig
    :param circuit: CircuitBreakerConfig

    :example:
        >>> cfg = UploadConfig()
        >>> isinstance(cfg.retry, RetryConfig)
        True
    """

    retry: RetryConfig = field(default_factory=RetryConfig)
    circuit: CircuitBreakerConfig = field(default_factory=CircuitBreakerConfig)