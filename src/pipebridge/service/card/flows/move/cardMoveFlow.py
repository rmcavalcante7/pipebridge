from typing import List, Optional

from pipebridge.exceptions import ValidationError, getExceptionContext
from pipebridge.service.card.flows.move.cardMoveConfig import CardMoveConfig
from pipebridge.service.card.flows.move.cardMoveRequest import CardMoveRequest
from pipebridge.service.card.flows.move.cardMoveResult import CardMoveResult
from pipebridge.service.card.flows.move.context.cardMoveContext import CardMoveContext
from pipebridge.service.card.flows.move.rules import (
    ValidateCardAllowedTransitionRule,
    ValidateCardMoveRequestRule,
    ValidateCardRequiredFieldsForPhaseRule,
)
from pipebridge.service.card.flows.move.steps import (
    LoadCardForMoveStep,
    LoadDestinationPhaseStep,
    MoveCardToPhaseStep,
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


class CardMoveFlow:
    """
    Workflow-driven safe phase transition flow for cards.

    This flow wraps the low-level ``moveCardToPhase`` operation with
    deterministic validation steps:

    1. load source card
    2. load destination phase schema
    3. validate request and source phase expectation
    4. validate allowed transition targets
    5. validate pending required destination fields
    6. execute the actual move mutation
    """

    def __init__(self, context: CardServiceContext) -> None:
        """
        Initialize the safe card move flow.

        :param context: CardServiceContext = Shared dependency container

        :return: None

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
            LoadCardForMoveStep(),
            LoadDestinationPhaseStep(),
        ]
        self._move_steps: List[BaseStep] = [
            MoveCardToPhaseStep(),
        ]

    def execute(
        self,
        request: CardMoveRequest,
        extra_rules: Optional[List[BaseRule]] = None,
        config: Optional[CardMoveConfig] = None,
    ) -> CardMoveResult:
        """
        Execute the safe card move workflow end-to-end.

        :param request: CardMoveRequest = Structured move request
        :param extra_rules: list[BaseRule] | None = Optional additional rules
        :param config: CardMoveConfig | None = Optional move flow configuration

        :return: CardMoveResult = Structured move execution result

        :raises ValidationError:
            When request or transition validation fails
        :raises RequiredFieldError:
            When destination required fields are still pending
        :raises WorkflowError:
            When the workflow engine fails during execution
        :raises RequestError:
            When the low-level move request fails
        """
        config = config or CardMoveConfig()
        context = CardMoveContext(
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
            ValidateCardMoveRequestRule(),
            ValidateCardAllowedTransitionRule(),
            ValidateCardRequiredFieldsForPhaseRule(),
        ]
        if extra_rules:
            rules.extend(extra_rules)

        RuleEngine(rules).execute(context)

        move_engine = ExecutionEngine(
            steps=self._move_steps,
            policy_resolver=self._buildPolicyResolver(config),
        )
        move_engine.execute(context)

        return CardMoveResult(success=True, response=context.response)

    def _buildPolicyResolver(self, config: CardMoveConfig) -> ProfilePolicyResolver:
        """
        Build the policy resolver used by preload and move execution steps.

        :param config: CardMoveConfig = Move flow configuration

        :return: ProfilePolicyResolver = Resolver with read/write network policy
        """
        network_policy = PolicyChain(
            [
                CircuitBreakerPolicy(
                    config=config.circuit,
                    breakers=self._circuit_breakers,
                ),
                RetryPolicy(
                    config=config.retry,
                    retry_condition=self._isRetryableMoveException,
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
    def _isRetryableMoveException(exc: Exception) -> bool:
        """
        Determine whether a move-flow exception is transient and retryable.

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
