# ============================================================
# Dependencies:
# - None
# ============================================================

from __future__ import annotations


# ============================================================
# Base Exceptions
# ============================================================

# ============================================================
# Dependencies
# ============================================================
import inspect
from typing import Optional


# ============================================================
# Base Exception
# ============================================================
class PipefyError(Exception):
    """
    Base exception for all Pipefy SDK errors.

    Provides standardized error message formatting including:
    - Class name
    - Method name
    - Custom message

    :param message: str = Human-readable error description
    :param class_name: Optional[str] = Origin class name
    :param method_name: Optional[str] = Origin method name
    """

    def __init__(
        self,
        message: str,
        class_name: Optional[str] = None,
        method_name: Optional[str] = None
    ) -> None:
        self.class_name = class_name
        self.method_name = method_name

        formatted_message = self._formatMessage(
            message=message,
            class_name=class_name,
            method_name=method_name
        )

        super().__init__(formatted_message)

    # ============================================================
    # Helper Methods
    # ============================================================
    def _formatMessage(
        self,
        message: str,
        class_name: Optional[str],
        method_name: Optional[str]
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