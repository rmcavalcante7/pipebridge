# ============================================================
# Dependencies
# ============================================================
import time
from typing import Dict, List

from pipefy.service.file.flows.pipeline.steps.baseStep import BaseStep
from pipefy.service.file.flows.pipeline.uploadPipelineContext import UploadPipelineContext
from pipefy.service.file.flows.pipeline.resilience.circuitBreaker import CircuitBreaker


class StepEngine:
    """
    Executes pipeline steps with retry, exponential backoff, jitter,
    and circuit breaker protection.

    FEATURES:
        - Retry per step
        - Exponential backoff
        - Jitter (prevents retry storms)
        - Retry condition per exception
        - Circuit breaker per step
        - Fail-fast behavior

    DESIGN:
        - Stateless execution
        - Step-controlled retry policy
        - Circuit breaker isolated per step type

    :param steps: list[BaseStep]

    :example:
        >>> callable(StepEngine.execute)
        True
    """

    # ============================================================
    # Constructor
    # ============================================================

    def __init__(self, steps: List[BaseStep]) -> None:
        """
        Initializes StepEngine.

        :param steps: list[BaseStep]

        :raises ValueError:
            When steps is None
        """
        if steps is None:
            raise ValueError("steps cannot be None")

        self._steps: List[BaseStep] = steps
        self._circuit_breakers: Dict[str, CircuitBreaker] = {}

    # ============================================================
    # Public Methods
    # ============================================================

    def execute(self, context: UploadPipelineContext) -> None:
        """
        Executes all steps with retry, backoff, jitter, and circuit breaker.

        Execution flow per step:
            1. Check circuit breaker state
            2. Execute step (if allowed)
            3. On success → reset circuit
            4. On failure → increment failure
            5. Apply retry policy

        :param context: UploadPipelineContext

        :return: None

        :raises Exception:
            When step fails after retries or circuit is open
        """
        for step in self._steps:
            circuit = self._getCircuitBreaker(step, context)

            # --------------------------------------------------------
            # Circuit breaker check
            # --------------------------------------------------------
            if not circuit.canExecute():
                raise Exception(
                    f"[StepEngine] Circuit OPEN for step {step}"
                )

            max_attempts = context.config.retry.max_retries

            for attempt in range(1, max_attempts + 1):
                start_time = time.perf_counter()

                try:
                    print(
                        f"[StepEngine] Executing {step} "
                        f"(attempt {attempt}/{max_attempts})"
                    )

                    step.execute(context)

                    elapsed = (time.perf_counter() - start_time) * 1000

                    print(
                        f"[StepEngine] Step OK: {step} "
                        f"({elapsed:.2f} ms)"
                    )

                    # --------------------------------------------------------
                    # Circuit success
                    # --------------------------------------------------------
                    circuit.onSuccess()

                    break

                except Exception as exc:
                    elapsed = (time.perf_counter() - start_time) * 1000

                    print(
                        f"[StepEngine] Step FAILED: {step} "
                        f"(attempt {attempt}/{max_attempts}) "
                        f"({elapsed:.2f} ms) → {exc}"
                    )

                    # --------------------------------------------------------
                    # Circuit failure
                    # --------------------------------------------------------
                    circuit.onFailure()

                    # --------------------------------------------------------
                    # Retry condition
                    # --------------------------------------------------------
                    if not step.shouldRetry(exc):
                        print(
                            f"[StepEngine] Non-retryable error in {step}"
                        )
                        raise

                    # --------------------------------------------------------
                    # Max retries reached
                    # --------------------------------------------------------
                    if attempt == max_attempts:
                        print(
                            f"[StepEngine] Max retries reached for {step}"
                        )
                        raise

                    # --------------------------------------------------------
                    # Jitter Backoff
                    # --------------------------------------------------------
                    delay = step.getJitterDelay(attempt)

                    print(
                        f"[StepEngine] Retrying {step} in {delay:.2f}s "
                        f"(jitter applied)"
                    )

                    time.sleep(delay)

    # ============================================================
    # Helper Methods
    # ============================================================

    def _getCircuitBreaker(self, step: BaseStep, context: UploadPipelineContext) -> CircuitBreaker:
        """
        Retrieves or creates a circuit breaker for a given step.

        Each step type has its own isolated circuit breaker.

        :param step: BaseStep
        :param context: UploadPipelineContext

        :return: CircuitBreaker
        """
        key = step.__class__.__name__

        if key not in self._circuit_breakers:
            cfg = context.config.circuit

            self._circuit_breakers[key] = CircuitBreaker(
                failure_threshold=cfg.failure_threshold,
                recovery_timeout=cfg.recovery_timeout
            )

        return self._circuit_breakers[key]
    # ============================================================
    # Dunder Methods
    # ============================================================

    def __str__(self) -> str:
        return f"<StepEngine steps={len(self._steps)}>"

    def __repr__(self) -> str:
        return f"<StepEngine(steps={self._steps})>"