"""
Core exception types and helpers shared across the SDK.
"""

from pipebridge.exceptions.core.api import PipefyAPIError
from pipebridge.exceptions.core.base import PipefyError
from pipebridge.exceptions.core.integration import IntegrationError
from pipebridge.exceptions.core.parsing import ParsingError, UnexpectedResponseError
from pipebridge.exceptions.core.request import RequestError
from pipebridge.exceptions.core.utils import getExceptionContext

__all__ = [
    "PipefyError",
    "PipefyAPIError",
    "IntegrationError",
    "ParsingError",
    "UnexpectedResponseError",
    "RequestError",
    "getExceptionContext",
]
