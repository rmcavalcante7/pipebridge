"""
Transport-level exceptions for HTTP and GraphQL communication.
"""

from pipebridge.exceptions.auth.errors import (
    AuthenticationError,
    InvalidTokenError,
    UnauthorizedError,
)
from pipebridge.exceptions.core.parsing import UnexpectedResponseError
from pipebridge.exceptions.core.request import RequestError


class TransportError(RequestError):
    """
    Base exception for transport-level failures.
    """

    default_error_code = "transport.error"


class TimeoutRequestError(TransportError):
    """
    Raised when a network request exceeds the configured timeout.
    """

    default_error_code = "transport.timeout"
    default_retryable = True


class ConnectionRequestError(TransportError):
    """
    Raised when the SDK cannot establish or maintain a connection.
    """

    default_error_code = "transport.connection"
    default_retryable = True


class RateLimitRequestError(TransportError):
    """
    Raised when the API denies the request due to rate limiting.
    """

    default_error_code = "transport.rate_limit"
    default_retryable = True


class TransportAuthenticationError(AuthenticationError):
    """
    Raised when a transport request fails due to authentication.
    """

    default_error_code = "transport.auth"


class TransportInvalidTokenError(InvalidTokenError):
    """
    Raised when the provided Pipefy token is invalid.
    """

    default_error_code = "transport.invalid_token"


class TransportUnauthorizedError(UnauthorizedError):
    """
    Raised when the authenticated principal lacks permission.
    """

    default_error_code = "transport.unauthorized"


class TransportUnexpectedResponseError(UnexpectedResponseError):
    """
    Raised when a transport response cannot be interpreted safely.
    """

    default_error_code = "transport.unexpected_response"
