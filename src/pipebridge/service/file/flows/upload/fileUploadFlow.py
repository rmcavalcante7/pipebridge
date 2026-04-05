# ============================================================
# Dependencies
# ============================================================
from typing import List, Optional, Sequence

from pipebridge.exceptions import RequestError, ValidationError, getExceptionContext
from pipebridge.exceptions.file import FileUploadError
from pipebridge.models.file.fileUploadRequest import FileUploadRequest
from pipebridge.integrations.file.fileUploadResult import FileUploadResult

from pipebridge.service.file.flows.upload.baseFileUploadFlow import BaseFileUploadFlow
from pipebridge.service.file.flows.upload.config.uploadConfig import UploadConfig
from pipebridge.service.file.flows.upload.context.uploadPipelineContext import (
    UploadPipelineContext,
)
from pipebridge.workflow.engine.executionEngine import ExecutionEngine
from pipebridge.workflow.policies.circuitBreakerPolicy import CircuitBreakerPolicy
from pipebridge.workflow.policies.policyChain import PolicyChain
from pipebridge.workflow.policies.profilePolicyResolver import ProfilePolicyResolver
from pipebridge.workflow.policies.retryPolicy import RetryPolicy
from pipebridge.workflow.resilience.circuitBreaker import CircuitBreaker

# ------------------------------------------------------------
# Pipeline
# ------------------------------------------------------------
from pipebridge.workflow.steps.baseStep import BaseStep
from pipebridge.service.file.flows.upload.steps.createPresignedUrlStep import (
    CreatePresignedUrlStep,
)
from pipebridge.service.file.flows.upload.steps.uploadStep import UploadStep
from pipebridge.service.file.flows.upload.steps.mergeAttachmentsStep import (
    MergeAttachmentsStep,
)
from pipebridge.service.file.flows.upload.steps.attachStep import AttachStep

# ------------------------------------------------------------
# Rules
# ------------------------------------------------------------
from pipebridge.workflow.rules.ruleEngine import RuleEngine
from pipebridge.workflow.rules.baseRule import BaseRule
from pipebridge.service.file.flows.upload.rules.validateFileBytesRule import (
    ValidateFileBytesRule,
)
from pipebridge.service.file.flows.upload.rules.validateFieldRule import (
    ValidateFieldRule,
)
from pipebridge.service.file.flows.upload.rules.validateCardPhaseRule import (
    ValidateCardPhaseRule,
)
from pipebridge.service.file.fileServiceContext import FileServiceContext


class FileUploadFlow(BaseFileUploadFlow):
    """
    Advanced file upload flow using a pipeline and rule engine architecture.

    This flow represents the second version of the upload mechanism, designed
    to provide high scalability, extensibility, and maintainability.

    ARCHITECTURE OVERVIEW:

        1. RuleEngine (Validation Layer)
            - Executes validation rules
            - Ensures request consistency
            - Prevents invalid operations early

        2. ExecutionEngine (Execution Layer)
            - Executes pipeline steps sequentially
            - Applies external execution policies per step
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
        >>> callable(FileUploadFlow.execute)
        True
    """

    # ============================================================
    # Constructor
    # ============================================================

    def __init__(self, context: FileServiceContext) -> None:
        """
        Initializes FileUploadFlow.

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
                method_name=method_name,
            )

        self._ctx = context
        self._circuit_breakers: dict[str, CircuitBreaker] = {}

        self._pipeline: list[BaseStep] = [
            CreatePresignedUrlStep(),
            UploadStep(),
            MergeAttachmentsStep(),
            AttachStep(),
        ]

    # ============================================================
    # Public Methods
    # ============================================================

    def execute(
        self,
        request: FileUploadRequest,
        extra_rules: Optional[List[BaseRule]] = None,
        config: Optional[UploadConfig] = None,
        extra_steps_before: Optional[Sequence[BaseStep]] = None,
        extra_steps_after: Optional[Sequence[BaseStep]] = None,
    ) -> FileUploadResult:
        """
        Executes the file upload flow.

        This method orchestrates the full upload lifecycle:

            1. Build execution context
            2. Execute validation rules (RuleEngine)
            3. Execute pipeline steps (ExecutionEngine)
            4. Return structured result

        :param request: FileUploadRequest = Upload request data
        :param extra_rules: Optional[List[BaseRule]] = Additional custom rules
        :param config: Optional[UploadConfig] = Configuration for upload process
        :param extra_steps_before: Optional[Sequence[BaseStep]] = Additional
            custom steps executed before the built-in upload pipeline
        :param extra_steps_after: Optional[Sequence[BaseStep]] = Additional
            custom steps executed after the built-in upload pipeline

        :return: FileUploadResult = Structured result of upload process

        :raises ValidationError:
            When request or rules are invalid
        :raises RuleExecutionError:
            When a validation rule crashes technically
        :raises StepExecutionError:
            When a step crashes technically
        :raises RetryExhaustedError:
            When retry policy exhausts all attempts for a step
        :raises CircuitBreakerOpenError:
            When circuit breaker blocks a step execution
        :raises FileFlowError:
            When a file-domain operation fails semantically

        :example:
            >>> callable(FileUploadFlow.execute)
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
            files=[],
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
        execution_engine = ExecutionEngine(
            steps=self._buildExecutionSteps(
                extra_steps_before=extra_steps_before,
                extra_steps_after=extra_steps_after,
            ),
            policy_resolver=self._buildPolicyResolver(config),
        )
        execution_engine.execute(context)

        # --------------------------------------------------------
        # Build result
        # --------------------------------------------------------
        return FileUploadResult(
            file_path=context.files, download_url=context.download_url, success=True
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
            >>> callable(FileUploadFlow._getMandatoryRules)
            True
        """
        return [ValidateFileBytesRule(), ValidateFieldRule()]

    def _buildExecutionSteps(
        self,
        extra_steps_before: Optional[Sequence[BaseStep]] = None,
        extra_steps_after: Optional[Sequence[BaseStep]] = None,
    ) -> List[BaseStep]:
        """
        Build the final execution pipeline for one upload run.

        This method preserves the SDK base pipeline while allowing consumers
        to inject additional steps before and/or after the built-in upload
        sequence.

        :param extra_steps_before: Sequence[BaseStep] | None = Custom steps
            executed before the SDK base pipeline
        :param extra_steps_after: Sequence[BaseStep] | None = Custom steps
            executed after the SDK base pipeline

        :return: list[BaseStep] = Final execution pipeline

        :raises ValidationError:
            When a provided custom step is not an instance of ``BaseStep``
        """
        class_name, method_name = getExceptionContext(self)

        before = list(extra_steps_before or [])
        after = list(extra_steps_after or [])

        for step in before + after:
            if not isinstance(step, BaseStep):
                raise ValidationError(
                    message="All custom upload steps must inherit from BaseStep",
                    class_name=class_name,
                    method_name=method_name,
                )

        return before + list(self._pipeline) + after

    def _getDefaultRules(self) -> List[BaseRule]:
        """
        Returns default validation rules.

        These rules provide additional validation but are not strictly mandatory.

        :return: list[BaseRule]

        :example:
            >>> callable(FileUploadFlow._getDefaultRules)
            True
        """
        return [
            ValidateCardPhaseRule(),
        ]

    def _buildPolicyResolver(self, config: UploadConfig) -> ProfilePolicyResolver:
        """
        Build the policy resolver used by upload step execution.

        All upload steps currently use the ``network`` execution profile,
        which receives the retry and circuit breaker policies configured
        in :class:`UploadConfig`.

        :param config: UploadConfig = Upload execution policy configuration

        :return: ProfilePolicyResolver = Resolver used by the execution engine

        :example:
            >>> ctx = type("Ctx", (), {})()
            >>> flow = FileUploadFlow(ctx)
            >>> resolver = flow._buildPolicyResolver(UploadConfig())
            >>> isinstance(resolver, ProfilePolicyResolver)
            True
        """
        network_policy = PolicyChain(
            [
                CircuitBreakerPolicy(
                    config=config.circuit, breakers=self._circuit_breakers
                ),
                RetryPolicy(
                    config=config.retry,
                    retry_condition=self._isRetryableUploadException,
                ),
            ]
        )

        return ProfilePolicyResolver(policies_by_profile={"network": network_policy})

    def _isRetryableUploadException(self, exc: Exception) -> bool:
        """
        Determine whether an upload exception should be retried.

        Retry is reserved for failures that are likely transient, such as:
        network instability, timeouts, temporary unavailability, and
        transport/file exceptions explicitly marked as retryable.

        :param exc: Exception = Raised exception during step execution

        :return: bool = True when execution should be retried

        :example:
            >>> ctx = type("Ctx", (), {})()
            >>> flow = FileUploadFlow(ctx)
            >>> flow._isRetryableUploadException(RequestError("timeout"))
            True
        """
        retryable = getattr(exc, "retryable", None)

        if retryable is not None:
            return bool(retryable)

        if isinstance(exc, (RequestError, FileUploadError)):
            message = str(exc).lower()
            transient_tokens = (
                "timeout",
                "connection",
                "temporarily unavailable",
                "connection aborted",
                "connection reset",
                "network",
                "status 500",
                "status 502",
                "status 503",
                "status 504",
            )

            return any(token in message for token in transient_tokens)

        return False

    # ============================================================
    # Dunder Methods
    # ============================================================

    def __str__(self) -> str:
        """
        Returns human-readable representation.

        :return: str

        :example:
            >>> ctx = type("Ctx", (), {})()
            >>> str(FileUploadFlow(context=ctx))
            '<FileUploadFlow>'
        """
        return f"<{self.__class__.__name__}>"

    def __repr__(self) -> str:
        """
        Returns developer-friendly representation.

        :return: str

        :example:
            >>> ctx = type("Ctx", (), {})()
            >>> str(FileUploadFlow(context=ctx))
            '<FileUploadFlow>'
        """
        return f"<{self.__class__.__name__}()>"
