# ============================================================
# Dependencies
# ============================================================
from __future__ import annotations

from typing import Any, Mapping, Optional


# ============================================================
# Base Exception
# ============================================================
class PipefyError(Exception):
    """
    Base exception for all Pipefy SDK errors.

    This base class keeps backward compatibility with the original
    ``class_name``/``method_name`` format while also enriching exceptions
    with metadata that can be used by retry policies, logging, debugging,
    and higher-level orchestration layers.

    :param message: str = Human-readable error description
    :param class_name: Optional[str] = Origin class name
    :param method_name: Optional[str] = Origin method name
    :param error_code: Optional[str] = Stable machine-readable error code
    :param context: Optional[Mapping[str, Any]] = Structured error context
    :param cause: Optional[Exception] = Original exception cause
    :param retryable: bool = Indicates whether the failure is transient
    """

    default_error_code: str = "pipebridge.error"
    default_retryable: bool = False

    def __init__(
        self,
        message: str,
        class_name: Optional[str] = None,
        method_name: Optional[str] = None,
        *,
        error_code: Optional[str] = None,
        context: Optional[Mapping[str, Any]] = None,
        cause: Optional[Exception] = None,
        retryable: Optional[bool] = None,
    ) -> None:
        """
        Initialize the structured SDK exception.

        :param message: str = Human-readable error message
        :param class_name: str | None = Origin class name
        :param method_name: str | None = Origin method name
        :param error_code: str | None = Stable machine-readable error code
        :param context: Mapping[str, Any] | None = Structured context payload
        :param cause: Exception | None = Original exception
        :param retryable: bool | None = Whether the error is transient
        """
        self.message = message
        self.class_name = class_name
        self.method_name = method_name
        self.error_code = error_code or self.default_error_code
        self.context = dict(context or {})
        self.cause = cause
        self.retryable = self.default_retryable if retryable is None else retryable

        formatted_message = self._formatMessage(
            message=message,
            class_name=class_name,
            method_name=method_name,
        )

        super().__init__(formatted_message)

    # ============================================================
    # Helper Methods
    # ============================================================
    def _formatMessage(
        self,
        message: str,
        class_name: Optional[str],
        method_name: Optional[str],
    ) -> str:
        """
        Formats the error message with context.

        :param message: str = Original error message
        :param class_name: Optional[str] = Class name
        :param method_name: Optional[str] = Method name
        :return: str = Formatted message
        """
        parts = []

        if class_name:
            parts.append(f"Class: {class_name}")

        if method_name:
            parts.append(f"Method: {method_name}")

        parts.append(f"Error: {message}")

        return "\n".join(parts)

    def toDict(self) -> dict[str, Any]:
        """
        Serialize the exception metadata to a dictionary.

        :return: dict[str, Any] = Structured exception representation

        :example:
            >>> error = PipefyError("failure", error_code="test.error")
            >>> error.toDict()["error_code"]
            'test.error'
        """
        return {
            "message": self.message,
            "formatted_message": str(self),
            "class_name": self.class_name,
            "method_name": self.method_name,
            "error_code": self.error_code,
            "context": dict(self.context),
            "retryable": self.retryable,
            "cause": repr(self.cause) if self.cause is not None else None,
        }
