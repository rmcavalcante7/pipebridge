# ============================================================
# Dependencies
# ============================================================
import json

from pipefy.service.file.flows.pipeline.uploadPipelineContext import UploadPipelineContext


class MergeAttachmentsStep:
    """
    Pipeline step responsible for merging existing attachments with new files.

    This step ensures that existing attachments are preserved when
    `replace_files=False`.

    BEHAVIOR:
        - If replace_files=True → no action
        - If replace_files=False → existing files are fetched and merged

    RESPONSIBILITIES:
        - Retrieve current card attachments
        - Normalize file paths
        - Merge with new files

    :example:
        >>> callable(MergeAttachmentsStep.execute)
        True
    """

    def __str__(self) -> str:
        """
        Human-readable representation.

        :return: str
        """
        return f"<MergeAttachmentsStep>"

    def __repr__(self) -> str:
        """
        Developer-friendly representation.

        :return: str
        """
        return f"<MergeAttachmentsStep()>"

    def execute(self, context: UploadPipelineContext) -> None:
        """
        Executes merge logic.

        :param context: UploadPipelineContext

        :return: None
        """
        request = context.request

        if request.replace_files:
            return

        card = context.card_service.getCardModel(request.card_id)

        if request.field_id not in card.fields_map:
            return

        raw_value = card.fields_map[request.field_id].value

        if not raw_value:
            return

        try:
            urls = json.loads(raw_value)

            existing_files = [
                context.integration.extractFilePath(url)
                for url in urls
            ]

            context.files = existing_files + context.files

        except Exception:
            return