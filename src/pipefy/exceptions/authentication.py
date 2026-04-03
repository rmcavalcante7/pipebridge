from pipefy.exceptions.base import PipefyError


class AuthenticationError(PipefyError):
    """
    Base exception for authentication errors.
    """
    pass


class MissingTokenError(AuthenticationError):
    """Raised when token is missing."""
    pass


class InvalidTokenError(AuthenticationError):
    """Raised when token is invalid."""
    pass


class ExpiredTokenError(AuthenticationError):
    """Raised when token is expired."""
    pass


class UnauthorizedError(AuthenticationError):
    """Raised when access is unauthorized."""
    pass