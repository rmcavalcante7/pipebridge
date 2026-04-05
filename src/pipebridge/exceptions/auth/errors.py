"""
Authentication-related exceptions for the Pipefy SDK.
"""

from pipebridge.exceptions.core.base import PipefyError


class AuthenticationError(PipefyError):
    """
    Base exception for authentication failures.

    This category groups all token and authorization problems raised by the
    SDK when communicating with Pipefy.
    """

    default_error_code = "auth.error"


class MissingTokenError(AuthenticationError):
    """
    Raised when an authentication token is missing.
    """

    default_error_code = "auth.missing_token"


class InvalidTokenError(AuthenticationError):
    """
    Raised when an authentication token is invalid.
    """

    default_error_code = "auth.invalid_token"


class ExpiredTokenError(AuthenticationError):
    """
    Raised when an authentication token has expired.
    """

    default_error_code = "auth.expired_token"


class UnauthorizedError(AuthenticationError):
    """
    Raised when the caller is authenticated but not authorized.
    """

    default_error_code = "auth.unauthorized"
