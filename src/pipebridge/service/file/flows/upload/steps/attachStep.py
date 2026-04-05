# ============================================================
# Dependencies
# ============================================================
import json

from pipebridge.workflow.steps.baseStep import BaseStep
from pipebridge.service.file.flows.upload.context.uploadPipelineContext import (
    UploadPipelineContext,
)
from pipebridge.exceptions.file import AttachmentUpdateError
from pipebridge.exceptions.core.utils import getExceptionContext


class AttachStep(BaseStep):
    """
    Pipeline step responsible for attaching files to a Pipefy card field.

    RESPONSIBILITIES:
        - Serialize file paths
        - Execute GraphQL mutation
        - Update remote field
        - Reuse external execution policies through the network profile

    :example:
        >>> callable(AttachStep.execute)
        True
    """

    execution_profile: str = "network"

    # ============================================================
    # Execution
    # ============================================================

    def execute(self, context: UploadPipelineContext) -> None:
        """
        Execute attachment logic.

        :param context: UploadPipelineContext

        :return: None

        :raises AttachmentUpdateError:
            When request fails

        :example:
            >>> callable(AttachStep.execute)
            True
        """
        class_name, method_name = getExceptionContext(self)

        request = context.request

        try:
            mutation = f"""
            mutation {{
              updateCardField(input: {{
                card_id: "{request.card_id}",
                field_id: "{request.field_id}",
                new_value: {json.dumps(context.files)}
              }}) {{
                success
              }}
            }}
            """

            context.client.sendRequest(mutation)

        except Exception as exc:
            raise AttachmentUpdateError(
                message=str(exc),
                class_name=class_name,
                method_name=method_name,
                cause=exc,
                retryable=getattr(exc, "retryable", False),
            ) from exc
