"""
Configuration object for card update flow execution.
"""

from typing import Optional

from pipebridge.workflow.config.circuitBreakerConfig import CircuitBreakerConfig
from pipebridge.workflow.config.retryConfig import RetryConfig


class CardUpdateConfig:
    """
    Configuration for card update flows.
    """

    def __init__(
        self,
        retry: Optional[RetryConfig] = None,
        circuit: Optional[CircuitBreakerConfig] = None,
        validate_phase: bool = True,
        validate_field_existence: bool = True,
        validate_field_options: bool = True,
        validate_field_type: bool = True,
        validate_field_format: bool = False,
        load_phase_schema: bool = False,
    ) -> None:
        """
        Initialize update-flow configuration.

        :param retry: RetryConfig | None = Retry policy configuration
        :param circuit: CircuitBreakerConfig | None = Circuit breaker configuration
        :param validate_phase: bool = Whether current phase must match the
            expected phase identifier when provided
        :param validate_field_existence: bool = Whether requested fields must
            exist in the current phase schema
        :param validate_field_options: bool = Whether option-like fields must
            be validated against configured options
        :param validate_field_type: bool = Whether basic type compatibility
            must be validated before dispatch
        :param validate_field_format: bool = Whether semantic format rules
            must run before update execution
        :param load_phase_schema: bool = Whether phase schema must be loaded
            proactively even when no schema validation is enabled
        """
        self.retry = retry or RetryConfig()
        self.circuit = circuit or CircuitBreakerConfig()
        self.validate_phase = validate_phase
        self.validate_field_existence = validate_field_existence
        self.validate_field_options = validate_field_options
        self.validate_field_type = validate_field_type
        self.validate_field_format = validate_field_format
        self.load_phase_schema = load_phase_schema

    def requiresPhaseSchema(self) -> bool:
        """
        Determine whether the update flow needs the current phase schema.

        :return: bool = Whether the flow must load phase metadata
        """
        return any(
            (
                self.load_phase_schema,
                self.validate_field_existence,
                self.validate_field_options,
                self.validate_field_type,
                self.validate_field_format,
            )
        )
