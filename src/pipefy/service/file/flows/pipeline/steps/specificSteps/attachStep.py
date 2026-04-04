# ============================================================
# Dependencies
# ============================================================
import json

from pipefy.service.file.flows.pipeline.steps.baseStep import BaseStep
from pipefy.service.file.flows.pipeline.uploadPipelineContext import UploadPipelineContext
from pipefy.exceptions import RequestError
from pipefy.exceptions.utils import getExceptionContext


class AttachStep(BaseStep):
    """
    Pipeline step responsible for attaching files to a Pipefy card field.

    RESPONSIBILITIES:
        - Serialize file paths
        - Execute GraphQL mutation
        - Update remote field

    :example:
        >>> callable(AttachStep.execute)
        True
    """

    # ============================================================
    # Execution
    # ============================================================

    def execute(self, context: UploadPipelineContext) -> None:
        """
        Executes attachment logic.

        :param context: UploadPipelineContext

        :return: None

        :raises RequestError:
            When request fails
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
            raise RequestError(
                message=str(exc),
                class_name=class_name,
                method_name=method_name
            ) from exc