# ============================================================
# Dependencies
# ============================================================
from typing import List, Optional

from pipefy.exceptions import ValidationError, getExceptionContext
from pipefy.models.file.fileUploadRequest import FileUploadRequest
from pipefy.integrations.file.fileUploadResult import FileUploadResult

from pipefy.service.file.flows.baseFileUploadFlow import BaseFileUploadFlow
from pipefy.service.file.flows.config.uploadConfig import UploadConfig
from pipefy.service.file.flows.pipeline.uploadPipelineContext import UploadPipelineContext

# ------------------------------------------------------------
# Pipeline
# ------------------------------------------------------------
from pipefy.service.file.flows.pipeline.steps.baseStep import BaseStep
from pipefy.service.file.flows.pipeline.steps.stepEngine import StepEngine
from pipefy.service.file.flows.pipeline.steps.specificSteps.createPresignedUrlStep import CreatePresignedUrlStep
from pipefy.service.file.flows.pipeline.steps.specificSteps.uploadStep import UploadStep
from pipefy.service.file.flows.pipeline.steps.specificSteps.mergeAttachmentsStep import MergeAttachmentsStep
from pipefy.service.file.flows.pipeline.steps.specificSteps.attachStep import AttachStep

# ------------------------------------------------------------
# Rules
# ------------------------------------------------------------
from pipefy.service.file.flows.rules.ruleEngine import RuleEngine
from pipefy.service.file.flows.rules.baseRule import BaseRule
from pipefy.service.file.flows.rules.specificRules.validateFileBytesRule import ValidateFileBytesRule
from pipefy.service.file.flows.rules.specificRules.validateFieldRule import ValidateFieldRule
from pipefy.service.file.flows.rules.specificRules.validateCardPhaseRule import ValidateCardPhaseRule


class FileUploadFlowV2(BaseFileUploadFlow):
    """
    Advanced file upload flow using a pipeline and rule engine architecture.

    This flow represents the second version of the upload mechanism, designed
    to provide high scalability, extensibility, and maintainability.

    ARCHITECTURE OVERVIEW:

        1. RuleEngine (Validation Layer)
            - Executes validation rules
            - Ensures request consistency
            - Prevents invalid operations early

        2. StepEngine (Execution Layer)
            - Executes pipeline steps sequentially
            - Handles retry logic per step
            - Mutates execution context

    PIPELINE STEPS:

        1. CreatePresignedUrlStep
            - Generates upload/download URLs via Pipefy API

        2. UploadStep
            - Uploads file bytes to storage (S3)

        3. MergeAttachmentsStep
            - Retrieves existing attachments (if applicable)
            - Merges with new files

        4. AttachStep
            - Sends final attachment list to Pipefy

    DESIGN PRINCIPLES:

        - Single Responsibility Principle (SRP)
        - Open/Closed Principle (OCP)
        - Stateless execution
        - Strong typing (no dict-based context)
        - Extensibility via rules and steps

    :example:
        >>> callable(FileUploadFlowV2.execute)
        True
    """

    # ============================================================
    # Constructor
    # ============================================================

    def __init__(self, context) -> None:
        """
        Initializes FileUploadFlowV2.

        This constructor defines the execution pipeline. No runtime state
        (such as rules or engines) is stored in the instance.

        :param context: FlowContext = Shared dependency container containing:
            - HTTP client
            - Card service
            - File integration

        :return: None

        :raises ValueError:
            When context is invalid
        """
        class_name, method_name = getExceptionContext(self)
        if context is None:
            raise ValidationError(
                message="context cannot be None",
                class_name=class_name,
                method_name=method_name
            )

        self._ctx = context

        self._pipeline: list[BaseStep] = [
            CreatePresignedUrlStep(),
            UploadStep(),
            MergeAttachmentsStep(),
            AttachStep()
        ]

    # ============================================================
    # Public Methods
    # ============================================================

    def execute(
        self,
        request: FileUploadRequest,
        extra_rules: Optional[List[BaseRule]] = None,
        config: Optional[UploadConfig] = None,
    ) -> FileUploadResult:
        """
        Executes the file upload flow.

        This method orchestrates the full upload lifecycle:

            1. Build execution context
            2. Execute validation rules (RuleEngine)
            3. Execute pipeline steps (StepEngine)
            4. Return structured result

        :param config:
        :param request: FileUploadRequest = Upload request data
        :param extra_rules: Optional[List[BaseRule]] = Additional custom rules
        :param config: Optional[UploadConfig] = Configuration for upload process

        :return: FileUploadResult = Structured result of upload process

        :raises ValidationError:
            When any validation rule fails
        :raises Exception:
            When any pipeline step fails

        :example:
            >>> callable(FileUploadFlowV2.execute)
            True
        """
        # --------------------------------------------------------
        # Build execution context (initial state)
        # --------------------------------------------------------
        config = config or UploadConfig()
        context = UploadPipelineContext(
            request=request,
            client=self._ctx.client,
            card_service=self._ctx.card_service,
            integration=self._ctx.file_integration,
            config=config,
            upload_url=None,
            download_url=None,
            files=[]
        )

        # --------------------------------------------------------
        # Build rules dynamically (stateless)
        # --------------------------------------------------------
        rules: List[BaseRule] = []

        # Mandatory rules
        rules.extend(self._getMandatoryRules())

        # Default rules
        rules.extend(self._getDefaultRules())

        # Extra rules (user-defined)
        if extra_rules:
            rules.extend(extra_rules)

        # --------------------------------------------------------
        # Execute validation
        # --------------------------------------------------------
        rule_engine = RuleEngine(rules)
        rule_engine.execute(context)

        # --------------------------------------------------------
        # Execute pipeline
        # --------------------------------------------------------
        step_engine = StepEngine(self._pipeline)
        step_engine.execute(context)

        # --------------------------------------------------------
        # Build result
        # --------------------------------------------------------
        return FileUploadResult(
            file_path=context.files,
            download_url=context.download_url,
            success=True
        )

    # ============================================================
    # Private Methods
    # ============================================================

    def _getMandatoryRules(self) -> List[BaseRule]:
        """
        Returns mandatory validation rules.

        These rules are always executed and cannot be removed.

        :return: list[BaseRule]

        :example:
            >>> callable(FileUploadFlowV2._getMandatoryRules)
            True
        """
        return [
            ValidateFileBytesRule(),
            ValidateFieldRule()
        ]

    def _getDefaultRules(self) -> List[BaseRule]:
        """
        Returns default validation rules.

        These rules provide additional validation but are not strictly mandatory.

        :return: list[BaseRule]

        :example:
            >>> callable(FileUploadFlowV2._getDefaultRules)
            True
        """
        return [
            ValidateCardPhaseRule(),
        ]

    # ============================================================
    # Dunder Methods
    # ============================================================

    def __str__(self) -> str:
        """
        Returns human-readable representation.

        :return: str

        :example:
            >>> ctx = type("Ctx", (), {})()
            >>> str(FileUploadFlowV2(context=ctx))
            '<FileUploadFlowV2>'
        """
        return f"<{self.__class__.__name__}>"

    def __repr__(self) -> str:
        """
        Returns developer-friendly representation.

        :return: str

        :example:
            >>> ctx = type("Ctx", (), {})()
            >>> str(FileUploadFlowV2(context=ctx))
            '<FileUploadFlowV2>'
        """
        return f"<{self.__class__.__name__}()>"