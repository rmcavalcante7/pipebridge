# ============================================================
# Dependencies
# ============================================================
import json

from pipefy.service.file.flows.pipeline.steps.baseStep import BaseStep
from pipefy.service.file.flows.pipeline.uploadPipelineContext import UploadPipelineContext
from pipefy.exceptions import RequestError, ValidationError
from pipefy.exceptions.utils import getExceptionContext


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

    :example:
        >>> callable(MergeAttachmentsStep.execute)
        True
    """

    max_retries: int = 3

    # ============================================================
    # Execution
    # ============================================================

    def execute(self, context: UploadPipelineContext) -> None:
        """
        Executes merge logic.

        :param context: UploadPipelineContext

        :return: None

        :raises RequestError:
            When merge fails
        """
        class_name, method_name = getExceptionContext(self)

        request = context.request

        if request.replace_files:
            return

        try:
            card = context.card_service.getCardModel(request.card_id)

            if request.field_id not in card.fields_map:
                raise ValidationError(
                    message=f'Field {request.field_id} not found in card {request.card_id}',
                    class_name=class_name,
                    method_name=method_name
                )

            raw_value = card.fields_map[request.field_id].value

            if not raw_value:
                raise ValidationError(
                    message=f'No existing attachments found in field {request.field_id} of card {request.card_id}',
                    class_name=class_name,
                    method_name=method_name
                )

            urls = json.loads(raw_value)

            existing_files = [
                context.integration.extractFilePath(url)
                for url in urls
            ]

            context.files = existing_files + context.files

        except Exception as exc:
            raise RequestError(
                message=str(exc),
                class_name=class_name,
                method_name=method_name
            ) from exc