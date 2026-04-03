from pipefy.service.file.flows.pipeline.uploadPipelineContext import UploadPipelineContext
from pipefy.exceptions import ValidationError
from pipefy.exceptions.utils import getExceptionContext
from pipefy.service.file.flows.rules import BaseRule


class ValidateFileBytesRule(BaseRule):
    """
    Pipeline step responsible for validating file content.

    This step ensures that the file payload (file_bytes) is present
    before attempting upload.

    IMPORTANT:
        This step validates only the file content and does NOT perform:
            - request structure validation
            - business rule validation
            - field or card validation

    :example:
        >>> callable(ValidateFileBytesRule.execute)
        True
    """

    def execute(self, context: UploadPipelineContext) -> None:
        """
        Executes file content validation.

        :param context: UploadPipelineContext

        :return: None

        :raises ValidationError:
            When file_bytes is empty or invalid
        """
        class_name, method_name = getExceptionContext(self)

        request = context.request

        if not request.file_bytes:
            raise ValidationError(
                "file_bytes cannot be empty",
                class_name,
                method_name
            )