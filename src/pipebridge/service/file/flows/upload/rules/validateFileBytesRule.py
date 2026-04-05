from pipebridge.exceptions import ValidationError
from pipebridge.exceptions.core.utils import getExceptionContext
from pipebridge.service.file.flows.upload.context.uploadPipelineContext import (
    UploadPipelineContext,
)
from pipebridge.workflow.rules.baseRule import BaseRule


class ValidateFileBytesRule(BaseRule):
    """
    Validate whether the upload request contains file bytes.

    :example:
        >>> callable(ValidateFileBytesRule.execute)
        True
    """

    priority = 10

    def execute(self, context: UploadPipelineContext) -> None:
        """
        Execute file content validation.

        :param context: UploadPipelineContext = Shared upload execution context

        :return: None

        :raises ValidationError:
            When ``file_bytes`` is empty

        :example:
            >>> callable(ValidateFileBytesRule.execute)
            True
        """
        class_name, method_name = getExceptionContext(self)

        request = context.request

        if not request.file_bytes:
            raise ValidationError(
                message="file_bytes cannot be empty",
                class_name=class_name,
                method_name=method_name,
            )
