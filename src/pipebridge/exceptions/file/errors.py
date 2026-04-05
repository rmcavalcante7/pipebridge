"""
File-domain exceptions for upload and download flows.
"""

from pipebridge.exceptions.core.request import RequestError


class FileUploadError(RequestError):
    """
    Legacy-compatible base exception for upload flow failures.
    """

    default_error_code = "file.upload"


class FileAttachError(FileUploadError):
    """
    Raised when attaching uploaded files to a card fails.
    """

    default_error_code = "file.attach"


class FileValidationError(FileUploadError):
    """
    Raised when file input validation fails.
    """

    default_error_code = "file.validation"


class FileFlowError(FileUploadError):
    """
    Base exception for file flow failures.
    """

    default_error_code = "file.error"


class PresignedUrlCreationError(FileFlowError):
    """
    Raised when the SDK cannot obtain a presigned upload URL.
    """

    default_error_code = "file.presigned_url"


class FileTransferError(FileFlowError):
    """
    Raised when binary upload/download transfer fails.
    """

    default_error_code = "file.transfer"
    default_retryable = True


class AttachmentMergeError(FileFlowError):
    """
    Raised when attachment state cannot be merged safely.
    """

    default_error_code = "file.attachment_merge"


class AttachmentUpdateError(FileAttachError):
    """
    Raised when the attachment field cannot be updated in Pipefy.
    """

    default_error_code = "file.attachment_update"


class FileDownloadError(RequestError):
    """
    Raised when attachment download flow fails.
    """

    default_error_code = "file.download"
    default_retryable = True
