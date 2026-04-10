from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TransportConfig:
    """
    Transport-level configuration for HTTP communication with Pipefy.

    Defaults preserve the current behavior while allowing TLS and timeout
    customization in a backward-compatible way.
    """

    timeout: int = 30
    verify_ssl: bool = True
    ca_bundle_path: str | None = None
    max_retries: int = 0
    retry_delay_seconds: float = 0.0
    retry_backoff_multiplier: float = 1.0

    def resolveVerifyValue(self) -> bool | str:
        """
        Resolve the value expected by `requests.post(..., verify=...)`.
        """
        if self.ca_bundle_path:
            return self.ca_bundle_path
        return self.verify_ssl
