"""
Pipefy API error definitions.
"""

from typing import Any, Optional

from pipebridge.exceptions.core.base import PipefyError


class PipefyAPIError(PipefyError):
    """
    Raised when Pipefy returns an explicit API-level error payload.

    :param message: str = Error message
    :param errors: Any | None = Raw GraphQL or API error payload
    :param class_name: str | None = Class name context
    :param method_name: str | None = Method name context

    :example:
        >>> isinstance(PipefyAPIError("error"), PipefyAPIError)
        True
    """

    default_error_code = "api.error"

    def __init__(
        self,
        message: str,
        errors: Optional[Any] = None,
        class_name: Optional[str] = None,
        method_name: Optional[str] = None,
        *,
        error_code: Optional[str] = None,
        context: Optional[dict[str, Any]] = None,
        cause: Optional[Exception] = None,
        retryable: Optional[bool] = None,
    ) -> None:
        """
        Initialize a Pipefy API error with raw API payload metadata.

        :param message: str = Error message
        :param errors: Any | None = Raw API error payload
        :param class_name: str | None = Origin class name
        :param method_name: str | None = Origin method name
        :param error_code: str | None = Stable machine-readable error code
        :param context: dict[str, Any] | None = Structured error context
        :param cause: Exception | None = Original exception
        :param retryable: bool | None = Whether the failure is transient
        """
        super().__init__(
            message=message,
            class_name=class_name,
            method_name=method_name,
            error_code=error_code,
            context=context,
            cause=cause,
            retryable=retryable,
        )
        self.errors: Optional[Any] = errors
