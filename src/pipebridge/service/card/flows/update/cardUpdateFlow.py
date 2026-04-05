from typing import Dict, List, Optional

from pipebridge.exceptions import ValidationError, getExceptionContext
from pipebridge.service.card.flows.update.cardUpdateConfig import CardUpdateConfig
from pipebridge.service.card.flows.update.cardUpdateRequest import CardUpdateRequest
from pipebridge.service.card.flows.update.cardUpdateResult import CardUpdateResult
from pipebridge.service.card.flows.update.context.cardUpdateContext import (
    CardUpdateContext,
)
from pipebridge.service.card.flows.update.dispatcher.baseCardFieldUpdateHandler import (
    BaseCardFieldUpdateHandler,
)
from pipebridge.service.card.flows.update.dispatcher.cardFieldUpdateDispatcher import (
    CardFieldUpdateDispatcher,
)
from pipebridge.service.card.flows.update.dispatcher.cardFieldUpdateHandlerRegistry import (
    CardFieldUpdateHandlerRegistry,
)
from pipebridge.service.card.flows.update.rules import (
    ValidateCardFieldFormatRule,
    ValidateCardFieldSchemaRule,
    ValidateCardPhaseRule,
    ValidateCardUpdateRequestRule,
)
from pipebridge.service.card.flows.update.steps import (
    ApplyCardFieldUpdatesStep,
    LoadCardStep,
    LoadPhaseSchemaStep,
    ResolveCardFieldUpdatesStep,
)
from pipebridge.workflow.engine.executionEngine import ExecutionEngine
from pipebridge.workflow.policies.circuitBreakerPolicy import CircuitBreakerPolicy
from pipebridge.workflow.policies.policyChain import PolicyChain
from pipebridge.workflow.policies.profilePolicyResolver import ProfilePolicyResolver
from pipebridge.workflow.policies.retryPolicy import RetryPolicy
from pipebridge.workflow.resilience.circuitBreaker import CircuitBreaker
from pipebridge.workflow.rules.baseRule import BaseRule
from pipebridge.workflow.rules.ruleEngine import RuleEngine
from pipebridge.workflow.steps.baseStep import BaseStep
from pipebridge.service.card.cardServiceContext import CardServiceContext


class CardUpdateFlow:
    """
    Workflow-driven card update flow.

    This flow separates validation, dispatch and execution concerns:

    1. load current card and optional phase schema
    2. run mandatory and optional validation rules
    3. resolve each field through the dispatcher
    4. apply final updates through Pipefy mutations
    """

    def __init__(self, context: CardServiceContext) -> None:
        """
        Initialize the workflow-driven card update flow.

        :param context: CardServiceContext = Shared dependency container

        :raises ValidationError:
            When the shared context is missing
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
        self._preload_steps: List[BaseStep] = [
            LoadCardStep(),
            LoadPhaseSchemaStep(),
        ]

    def execute(
        self,
        request: CardUpdateRequest,
        extra_rules: Optional[List[BaseRule]] = None,
        config: Optional[CardUpdateConfig] = None,
        extra_handlers: Optional[Dict[str, BaseCardFieldUpdateHandler]] = None,
    ) -> CardUpdateResult:
        """
        Execute the card update flow end-to-end.

        :param request: CardUpdateRequest = Structured update request
        :param extra_rules: list[BaseRule] | None = Optional custom validation rules
        :param config: CardUpdateConfig | None = Optional update flow configuration
        :param extra_handlers: dict[str, BaseCardFieldUpdateHandler] | None =
            Optional custom handlers keyed by field type

        :return: CardUpdateResult = Structured flow result
        """
        config = config or CardUpdateConfig()
        context = CardUpdateContext(
            request=request,
            client=self._ctx.client,
            card_service=self._ctx.card_service,
            phase_service=self._ctx.phase_service,
            pipe_service=self._ctx.pipe_service,
            pipe_schema_cache=self._ctx.pipe_schema_cache,
            config=config,
        )

        preload_engine = ExecutionEngine(
            steps=self._preload_steps,
            policy_resolver=self._buildPolicyResolver(config),
        )
        preload_engine.execute(context)

        rules: List[BaseRule] = [
            ValidateCardUpdateRequestRule(),
            ValidateCardPhaseRule(),
            ValidateCardFieldSchemaRule(),
            ValidateCardFieldFormatRule(),
        ]
        if extra_rules:
            rules.extend(extra_rules)

        RuleEngine(rules).execute(context)

        update_engine = ExecutionEngine(
            steps=self._buildUpdateSteps(extra_handlers=extra_handlers),
            policy_resolver=self._buildPolicyResolver(config),
        )
        update_engine.execute(context)

        return CardUpdateResult(success=True, responses=context.responses)

    def _buildPolicyResolver(self, config: CardUpdateConfig) -> ProfilePolicyResolver:
        """
        Build the execution policy resolver for update steps.

        :param config: CardUpdateConfig = Update flow configuration

        :return: ProfilePolicyResolver = Resolver with read/write network policies
        """
        network_policy = PolicyChain(
            [
                CircuitBreakerPolicy(
                    config=config.circuit,
                    breakers=self._circuit_breakers,
                ),
                RetryPolicy(
                    config=config.retry,
                    retry_condition=self._isRetryableUpdateException,
                ),
            ]
        )

        return ProfilePolicyResolver(
            policies_by_profile={
                "network-read": network_policy,
                "network-write": network_policy,
            }
        )

    @staticmethod
    def _buildUpdateSteps(
        extra_handlers: Optional[Dict[str, BaseCardFieldUpdateHandler]] = None,
    ) -> List[BaseStep]:
        """
        Build update steps using the default dispatcher registry plus any
        caller-provided field-type handlers.

        :param extra_handlers: dict[str, BaseCardFieldUpdateHandler] | None =
            Optional custom handlers keyed by field type

        :return: list[BaseStep] = Ordered update steps
        """
        registry = CardFieldUpdateHandlerRegistry(extra_handlers=extra_handlers)
        return [
            ResolveCardFieldUpdatesStep(
                dispatcher=CardFieldUpdateDispatcher(registry=registry)
            ),
            ApplyCardFieldUpdatesStep(),
        ]

    @staticmethod
    def _isRetryableUpdateException(exc: Exception) -> bool:
        """
        Determine whether an update-flow exception is transient and retryable.

        :param exc: Exception = Captured execution failure

        :return: bool = Whether retry policy should retry the operation
        """
        retryable = getattr(exc, "retryable", None)
        if retryable is not None:
            return bool(retryable)

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
