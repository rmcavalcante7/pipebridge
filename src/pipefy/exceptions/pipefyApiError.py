from typing import Any, Optional

from pipefy.exceptions.base import PipefyError


class PipefyAPIError(PipefyError):
    """
    Raised when Pipefy API returns an error response.

    This exception represents errors returned directly by the Pipefy API,
    including GraphQL errors, validation issues, and unexpected responses.

    :param message: str = Error message
    :param errors: Optional[Any] = Raw error payload from API
    :param class_name: str = Class name
    :param method_name: str = Method name

    :example:
        >>> isinstance(PipefyAPIError("error"), PipefyAPIError)
        True
    """

    def __init__(
        self,
        message: str,
        errors: Optional[Any] = None,
        class_name: Optional[str] = None,
        method_name: Optional[str] = None
    ) -> None:
        super().__init__(
            message=message,
            class_name=class_name,
            method_name=method_name
        )

        self.errors: Optional[Any] = errors