# ============================================================
# Dependencies
# ============================================================
import json

from pipebridge.workflow.steps.baseStep import BaseStep
from pipebridge.service.file.flows.upload.context.uploadPipelineContext import (
    UploadPipelineContext,
)
from pipebridge.exceptions import ValidationError
from pipebridge.exceptions.file import AttachmentMergeError
from pipebridge.exceptions.core.utils import getExceptionContext


class MergeAttachmentsStep(BaseStep):
    """
    Pipeline step responsible for merging existing attachments with new files.

    BEHAVIOR:
        - If replace_files=True → no merge
        - If replace_files=False → merge existing files

    RESPONSIBILITIES:
        - Retrieve card attachments
        - Normalize file paths
        - Merge with new files
        - Reuse external execution policies through the network profile

    :example:
        >>> callable(MergeAttachmentsStep.execute)
        True
    """

    execution_profile: str = "network"

    # ============================================================
    # Execution
    # ============================================================

    def execute(self, context: UploadPipelineContext) -> None:
        """
        Execute merge logic.

        :param context: UploadPipelineContext

        :return: None

        :raises AttachmentMergeError:
            When merge fails

        :example:
            >>> callable(MergeAttachmentsStep.execute)
            True
        """
        class_name, method_name = getExceptionContext(self)

        request = context.request

        if request.replace_files:
            return

        try:
            card = context.card_service.getCardModel(request.card_id)

            if not card.hasField(request.field_id):
                raise ValidationError(
                    message=f"Field {request.field_id} not found in card {request.card_id}",
                    class_name=class_name,
                    method_name=method_name,
                )

            raw_value = card.requireFieldValue(request.field_id)

            if not raw_value:
                return

            urls = json.loads(raw_value)

            existing_files = [context.integration.extractFilePath(url) for url in urls]

            context.files = existing_files + context.files

        except ValidationError:
            raise
        except Exception as exc:
            raise AttachmentMergeError(
                message=str(exc),
                class_name=class_name,
                method_name=method_name,
                cause=exc,
                retryable=getattr(exc, "retryable", False),
            ) from exc
