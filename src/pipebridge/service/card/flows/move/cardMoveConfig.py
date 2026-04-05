"""
Configuration object for card move flow execution.
"""

from typing import Optional

from pipebridge.workflow.config.circuitBreakerConfig import CircuitBreakerConfig
from pipebridge.workflow.config.retryConfig import RetryConfig


class CardMoveConfig:
    """
    Configuration for safe card phase transitions.

    :param retry: RetryConfig | None = Retry policy configuration
    :param circuit: CircuitBreakerConfig | None = Circuit breaker configuration
    :param validate_required_fields: bool = Whether the flow must validate
        required fields from the destination phase before moving the card
    :param load_target_phase_schema: bool = Whether to load the destination
        phase schema even when required-field validation is disabled
    """

    def __init__(
        self,
        retry: Optional[RetryConfig] = None,
        circuit: Optional[CircuitBreakerConfig] = None,
        validate_required_fields: bool = True,
        load_target_phase_schema: bool = True,
    ) -> None:
        """
        Initialize move-flow configuration.

        :param retry: RetryConfig | None = Retry policy configuration
        :param circuit: CircuitBreakerConfig | None = Circuit breaker configuration
        :param validate_required_fields: bool = Whether destination required
            fields must be validated before the move mutation
        :param load_target_phase_schema: bool = Whether destination phase
            metadata must be loaded proactively

        :return: None

        :example:
            >>> config = CardMoveConfig(validate_required_fields=True)
            >>> config.validate_required_fields
            True
        """
        self.retry = retry or RetryConfig()
        self.circuit = circuit or CircuitBreakerConfig()
        self.validate_required_fields = validate_required_fields
        self.load_target_phase_schema = load_target_phase_schema

    def requiresTargetPhaseSchema(self) -> bool:
        """
        Determine whether destination phase metadata must be loaded.

        :return: bool = Whether the move flow needs the target phase schema

        :example:
            >>> CardMoveConfig().requiresTargetPhaseSchema()
            True
        """
        return any(
            (
                self.load_target_phase_schema,
                self.validate_required_fields,
            )
        )
