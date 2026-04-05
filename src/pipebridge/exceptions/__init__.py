# Base
from pipebridge.exceptions.core.base import PipefyError

# Core
from pipebridge.exceptions.core.api import PipefyAPIError
from pipebridge.exceptions.core.integration import IntegrationError
from pipebridge.exceptions.core.parsing import ParsingError, UnexpectedResponseError
from pipebridge.exceptions.core.request import RequestError
from pipebridge.exceptions.core.utils import getExceptionContext
from pipebridge.exceptions.validation.errors import ValidationError
from pipebridge.exceptions.validation.field import (
    FieldNotInPhaseError,
    InvalidFieldOptionError,
    RequiredFieldError,
)
from pipebridge.exceptions.validation.phase import InvalidPhaseError
from pipebridge.exceptions.transport import (
    ConnectionRequestError,
    RateLimitRequestError,
    TimeoutRequestError,
    TransportAuthenticationError,
    TransportError,
    TransportInvalidTokenError,
    TransportUnauthorizedError,
    TransportUnexpectedResponseError,
)
from pipebridge.exceptions.workflow import (
    CircuitBreakerOpenError,
    RetryExhaustedError,
    RuleExecutionError,
    StepExecutionError,
    WorkflowError,
)
from pipebridge.exceptions.file import (
    AttachmentMergeError,
    AttachmentUpdateError,
    FileAttachError,
    FileDownloadError,
    FileFlowError,
    FileTransferError,
    FileUploadError,
    FileValidationError,
    PresignedUrlCreationError,
)

# Auth
from pipebridge.exceptions.auth import (
    AuthenticationError,
    MissingTokenError,
    InvalidTokenError,
    ExpiredTokenError,
    UnauthorizedError,
)

# Config
from pipebridge.exceptions.config import (
    ConfigurationError,
    PipefyInitializationError,
    MissingBaseUrlError,
)

__all__ = [
    "PipefyError",
    "ValidationError",
    "InvalidPhaseError",
    "FieldNotInPhaseError",
    "InvalidFieldOptionError",
    "RequiredFieldError",
    "ParsingError",
    "UnexpectedResponseError",
    "RequestError",
    "IntegrationError",
    "TransportError",
    "TimeoutRequestError",
    "ConnectionRequestError",
    "RateLimitRequestError",
    "TransportAuthenticationError",
    "TransportInvalidTokenError",
    "TransportUnauthorizedError",
    "TransportUnexpectedResponseError",
    "AuthenticationError",
    "MissingTokenError",
    "InvalidTokenError",
    "ExpiredTokenError",
    "UnauthorizedError",
    "ConfigurationError",
    "PipefyInitializationError",
    "MissingBaseUrlError",
    "WorkflowError",
    "RuleExecutionError",
    "StepExecutionError",
    "RetryExhaustedError",
    "CircuitBreakerOpenError",
    "PipefyAPIError",
    "FileUploadError",
    "FileAttachError",
    "FileValidationError",
    "FileFlowError",
    "PresignedUrlCreationError",
    "FileTransferError",
    "AttachmentMergeError",
    "AttachmentUpdateError",
    "FileDownloadError",
    "getExceptionContext",
]
