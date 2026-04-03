import json
from pipefy.service.file.flows.pipeline.uploadPipelineContext import UploadPipelineContext


class AttachStep:
    """
    Pipeline step responsible for attaching files to a Pipefy card field.

    This step performs the final stage of the upload process by sending
    a GraphQL mutation to update the card field with the provided files.

    RESPONSIBILITIES:
        - Serialize file paths
        - Build GraphQL mutation
        - Execute mutation via HTTP client

    SIDE EFFECTS:
        - Updates remote Pipefy card field

    :example:
        >>> callable(AttachStep.execute)
        True
    """

    def __str__(self) -> str:
        """
        Human-readable representation.

        :return: str
        """
        return f"<AttachStep>"

    def __repr__(self) -> str:
        """
        Developer-friendly representation.

        :return: str
        """
        return f"<AttachStep()>"

    def execute(self, context: UploadPipelineContext) -> None:
        """
        Executes attachment logic.

        :param context: UploadPipelineContext

        :return: None

        :raises RequestError:
            When API request fails
        """
        request = context.request

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

