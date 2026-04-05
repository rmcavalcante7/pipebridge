"""
Configuration-related exceptions for the Pipefy SDK.
"""

from pipebridge.exceptions.core.base import PipefyError


class ConfigurationError(PipefyError):
    """
    Base exception for invalid SDK configuration.
    """

    default_error_code = "config.error"


class PipefyInitializationError(ConfigurationError):
    """
    Raised when SDK initialization fails.
    """

    default_error_code = "config.initialization"


class MissingBaseUrlError(ConfigurationError):
    """
    Raised when ``base_url`` is not provided.
    """

    default_error_code = "config.missing_base_url"
