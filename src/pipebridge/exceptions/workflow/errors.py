"""
Workflow execution exceptions.
"""

from pipebridge.exceptions.core.base import PipefyError


class WorkflowError(PipefyError):
    """
    Base exception for workflow execution failures.
    """

    default_error_code = "workflow.error"


class RuleExecutionError(WorkflowError):
    """
    Raised when a workflow rule fails technically during execution.
    """

    default_error_code = "workflow.rule_execution"


class StepExecutionError(WorkflowError):
    """
    Raised when a workflow step fails technically during execution.
    """

    default_error_code = "workflow.step_execution"


class RetryExhaustedError(WorkflowError):
    """
    Raised when retry attempts are exhausted.
    """

    default_error_code = "workflow.retry_exhausted"
    default_retryable = False


class CircuitBreakerOpenError(WorkflowError):
    """
    Raised when a circuit breaker blocks step execution.
    """

    default_error_code = "workflow.circuit_open"
    default_retryable = False
