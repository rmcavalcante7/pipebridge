from pipefy.exceptions.base import PipefyError


class ConfigurationError(PipefyError):
    """
    Base exception for configuration errors.
    """
    pass


class PipefyInitializationError(ConfigurationError):
    """
    Raised when SDK initialization fails.
    """
    pass

class MissingBaseUrlError(ConfigurationError):
    """
    Raised when base_url is not provided.

    :param message: str
    :param class_name: str
    :param method_name: str
    """
    pass