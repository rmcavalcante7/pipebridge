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

# ============================================================
# Validation Errors
# ============================================================
class ValidationError(PipefyError):
    """
    Raised when input validation fails.
    """
    pass


class ParsingError(PipefyError):
    """
    Raised when API response parsing fails.
    """
    pass


class RequestError(PipefyError):
    """
    Raised when an API request fails.
    """
    pass


class IntegrationError(PipefyError):
    """
    Raised when external integrations fail (e.g., FileService).
    """
    pass


class UnexpectedResponseError(PipefyError):
    """
    Raised when API response does not match expected structure.
    """
    pass

# ============================================================
# AUTH BASE EXCEPTION
# ============================================================

class AuthenticationError(PipefyError):
    """
    Base exception for authentication-related errors.
    """
    pass


class MissingTokenError(AuthenticationError):
    """
    Raised when no authentication token is provided.
    """
    pass


class InvalidTokenError(AuthenticationError):
    """
    Raised when the provided token is invalid.
    """
    pass


class ExpiredTokenError(AuthenticationError):
    """
    Raised when the authentication token has expired.
    """
    pass


class UnauthorizedError(AuthenticationError):
    """
    Raised when the user is not authorized to perform an action.
    """
    pass


# ============================================================
# Context Helper
# ============================================================
def getExceptionContext(obj: object) -> tuple[str, str]:
    """
    Extracts class and method name for exception context.

    :param obj: object = Instance where exception occurred
    :return: tuple[str, str] = (class_name, method_name)
    """
    class_name = obj.__class__.__name__
    method_name = inspect.currentframe().f_back.f_code.co_name  # type: ignore

    return class_name, method_name

def buildErrorMessage(
    instance: object,
    method_name: str,
    message: str
) -> str:
    """
    Builds a standardized error message including class and method context.

    This function ensures all exceptions follow a consistent format,
    improving observability and debugging.

    :param instance: object = Instance where the error occurred
    :param method_name: str = Name of the method where the error occurred
    :param message: str = Original error message

    :return: str = Formatted error message

    :example:
        >>> class Example:
        ...     def run(self):
        ...         raise Exception(
        ...             buildErrorMessage(self, "run", "Something went wrong")
        ...         )
    """
    return (
        f"Class: {instance.__class__.__name__}\n"
        f"Method: {method_name}\n"
        f"Error: {message}"
    )


def raiseWithContext(
    instance: object,
    exc: Exception
) -> None:
    """
    Re-raises an exception with enriched contextual information.

    This helper should be used to wrap lower-level exceptions while preserving
    the original traceback using 'from exc'.

    :param instance: object = Instance where the exception occurred
    :param exc: Exception = Original exception

    :raises PipefyError:
        Always raises a PipefyError with contextual information

    :example:
        >>> try:
        ...     int("invalid")
        ... except Exception as e:
        ...     raiseWithContext(object(), e)
    """
    method_name: str = inspect.currentframe().f_back.f_code.co_name  # type: ignore

    raise PipefyError(
        buildErrorMessage(instance, method_name, str(exc))
    ) from exc


# ============================================================
# Dependencies
# ============================================================
# from typing import List


# class ValidationError(Exception):
#     """
#     Represents a validation failure when comparing Card data
#     against Phase schema.
#
#     :param message: str = Error message
#     :param fields: list[str] = Fields that failed validation
#     """
#
#     def __init__(self, message: str, fields: List[str]) -> None:
#         super().__init__(message)
#         self.fields: List[str] = fields


# ============================================================
# Main (Usage Example)
# ============================================================

if __name__ == "__main__":
    """
    Simple execution example demonstrating exception usage.
    """

    class ExampleService:
        def execute(self) -> None:
            """
            Example method that raises a contextualized exception.

            :raises PipefyError:
                When execution fails

            :example:
                >>> service = ExampleService()
                >>> service.execute()
            """
            try:
                int("not_a_number")
            except Exception as exc:
                raiseWithContext(self, exc)

    service = ExampleService()

    try:
        service.execute()
    except PipefyError as error:
        print("Captured PipefyError:")
        print(error)