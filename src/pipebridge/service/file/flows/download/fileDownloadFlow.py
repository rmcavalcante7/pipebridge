# ============================================================
# Dependencies
# ============================================================
from pathlib import Path
from typing import List
from urllib.parse import unquote, urlparse

from pipebridge.exceptions import ValidationError, getExceptionContext
from pipebridge.exceptions.file import FileDownloadError
from pipebridge.dispatcher.field.fieldType import FieldType
from pipebridge.models.file.fileDownloadRequest import FileDownloadRequest
from pipebridge.service.file.flows.download.baseFileDownloadFlow import (
    BaseFileDownloadFlow,
)
from pipebridge.service.file.flows.download.fileDownloadContext import (
    FileDownloadContext,
)


class FileDownloadFlow(BaseFileDownloadFlow):
    """
    Concrete flow responsible for downloading card attachments.

    This flow loads the card state, extracts the attachment field, downloads
    each binary asset, and persists the files locally.

    :param context: FileDownloadContext = Flow dependencies

    :example:
        >>> callable(FileDownloadFlow.execute)
        True
    """

    def __init__(self, context: FileDownloadContext) -> None:
        """
        Initialize FileDownloadFlow.

        :param context: FileDownloadContext = Flow dependencies

        :return: None

        :raises ValidationError:
            When context is invalid

        :example:
            >>> callable(FileDownloadFlow)
            True
        """
        class_name, method_name = getExceptionContext(self)

        if context is None:
            raise ValidationError(
                message="context cannot be None",
                class_name=class_name,
                method_name=method_name,
            )

        self._context = context

    def execute(self, request: FileDownloadRequest) -> List[Path]:
        """
        Execute the attachment download flow.

        :param request: FileDownloadRequest = Structured download request

        :return: List[Path] = Saved local file paths

        :raises ValidationError:
            When ``request`` is invalid
        :raises FileDownloadError:
            When attachment parsing or binary download fails
        :raises RequestError:
            When lower-level service or transport failures bubble up unchanged

        :example:
            >>> callable(FileDownloadFlow.execute)
            True
        """
        class_name, method_name = getExceptionContext(self)

        if not isinstance(request, FileDownloadRequest):
            raise ValidationError(
                message="request must be a FileDownloadRequest instance",
                class_name=class_name,
                method_name=method_name,
            )

        field = self._context.card_service.getCardPipeField(
            request.card_id,
            request.field_id,
        )
        if field is None:
            raise ValidationError(
                message=(
                    f"Field '{request.field_id}' does not exist in the card pipe schema"
                ),
                class_name=class_name,
                method_name=method_name,
            )

        if field.type != FieldType.ATTACHMENT:
            raise ValidationError(
                message=f"Field '{request.field_id}' is not an attachment field",
                class_name=class_name,
                method_name=method_name,
            )

        attachments = self._context.card_service.listCardAttachmentsByField(
            request.card_id,
            request.field_id,
        )
        if not attachments:
            return []

        try:
            output_path = Path(request.output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            saved_files: List[Path] = []

            for attachment in attachments:
                url = attachment.get("url")
                if not isinstance(url, str) or not url:
                    raise FileDownloadError(
                        message="Attachment download URL is missing or invalid",
                        class_name=class_name,
                        method_name=method_name,
                        context={
                            "card_id": request.card_id,
                            "field_id": request.field_id,
                        },
                    )

                path_hint = attachment.get("path")
                if isinstance(path_hint, str) and path_hint:
                    file_name = unquote(Path(path_hint).name)
                else:
                    parsed_url = urlparse(url)
                    file_name = unquote(Path(parsed_url.path).name)

                content = self._context.file_integration.download(url)

                file_path = output_path / file_name
                file_path.write_bytes(content)
                saved_files.append(file_path)

            return saved_files

        except FileDownloadError:
            raise
        except Exception as exc:
            raise FileDownloadError(
                message=str(exc),
                class_name=class_name,
                method_name=method_name,
                cause=exc,
                retryable=getattr(exc, "retryable", False),
                context={
                    "card_id": request.card_id,
                    "field_id": request.field_id,
                },
            ) from exc
