from typing import List, Optional

from pipefy.models.file.fileUploadRequest import FileUploadRequest
from pipefy.service.file.flows.baseFileUploadFlow import BaseFileUploadFlow
from pipefy.service.file.flows.pipeline.uploadPipelineContext import UploadPipelineContext

from pipefy.service.file.flows.pipeline.steps.uploadStep import UploadStep
from pipefy.service.file.flows.pipeline.steps.attachStep import AttachStep
from pipefy.service.file.flows.pipeline.steps.mergeAttachmentsStep import MergeAttachmentsStep

from pipefy.integrations.file.fileUploadResult import FileUploadResult
from pipefy.exceptions.utils import getExceptionContext
from pipefy.service.file.flows.rules import BaseRule

from pipefy.service.file.flows.rules.ruleEngine import RuleEngine
from pipefy.service.file.flows.rules.validateFileBytesRule import ValidateFileBytesRule
from pipefy.service.file.flows.rules.validateFieldRule import ValidateFieldRule
from pipefy.service.file.flows.rules.validateCardPhaseRule import ValidateCardPhaseRule


class FileUploadFlowV2(BaseFileUploadFlow):
    """
    Advanced upload flow with strongly-typed pipeline.

    Improvements over V1:
        - Pipeline-based execution
        - Strong typing (no dict)
        - Retry support
        - Extensible architecture

    :example:
        >>> callable(FileUploadFlowV2.execute)
        True
    """

    def __init__(self, context) -> None:
        self._ctx = context

        self._pipeline = [
            UploadStep(),
            MergeAttachmentsStep(),
            AttachStep()
        ]
        self._rules: List[BaseRule] = [
            ValidateFileBytesRule(),
            ValidateFieldRule(),
            ValidateCardPhaseRule()
        ]

        self._rule_engine: Optional[RuleEngine] = None

    def execute(self, request: FileUploadRequest, extra_rules: Optional[list[BaseRule]] = None):

        presigned = self._createPresignedUrl(
            request.file_name,
            request.organization_id
        )

        data = presigned.get("data", {})
        presigned_data = data.get("createPresignedUrl", {})

        upload_url = presigned_data.get("url")
        download_url = presigned_data.get("downloadUrl")

        file_path = self._ctx.file_integration.extractFilePath(upload_url)

        context = UploadPipelineContext(
            request=request,
            client=self._ctx.client,
            card_service=self._ctx.card_service,
            integration=self._ctx.file_integration,
            upload_url=upload_url,
            download_url=download_url,
            files=[file_path]
        )

        if extra_rules:
            self._rules.extend(extra_rules)

        self._rule_engine = RuleEngine(rules=self._rules)

        self._rule_engine.execute(context)

        for step in self._pipeline:
            print(f"Executing step: {step}")
            step.execute(context)

        return FileUploadResult(
            file_path=context.files,
            download_url=context.download_url,
            success=True
        )

    def _createPresignedUrl(self, file_name, organization_id):
        query = f"""
        mutation {{
            createPresignedUrl(
                input: {{
                    organizationId: {organization_id},
                    fileName: "{file_name}"
                }}
            ) {{
                url
                downloadUrl
            }}
        }}
        """
        return self._ctx.client.sendRequest(query)