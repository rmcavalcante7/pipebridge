# ============================================================
# Dependencies
# ============================================================
import random
from abc import ABC, abstractmethod
from typing import Type

from pipefy.service.file.flows.pipeline.uploadPipelineContext import UploadPipelineContext


class BaseStep(ABC):
    """
    Abstract base class for pipeline steps.

    A step represents a unit of execution within the upload pipeline.

    RETRY STRATEGY:

        Each step defines its own retry behavior via:

            - max_retries
            - retry_base_delay
            - retryable_exceptions
            - shouldRetry()

    DESIGN PRINCIPLES:

        - Open/Closed Principle (OCP)
        - Polymorphic retry control
        - Separation of concerns (execution vs retry policy)

    :attribute max_retries: int = Maximum retry attempts
    :attribute retry_base_delay: float = Base delay in seconds
    :attribute retryable_exceptions: tuple[type[Exception], ...] = Exceptions eligible for retry

    :example:
        >>> callable(BaseStep.execute)
        True
    """

    max_retries: int = 1
    retry_base_delay: float = 0.5
    retryable_exceptions: tuple[Type[Exception], ...] = (Exception,)

    # ============================================================
    # Abstract Methods
    # ============================================================

    @abstractmethod
    def execute(self, context: UploadPipelineContext) -> None:
        """
        Executes step logic.

        :param context: UploadPipelineContext

        :return: None

        :raises Exception:
            When execution fails
        """
        raise NotImplementedError

    # ============================================================
    # Retry Strategy
    # ============================================================

    def shouldRetry(self, exc: Exception) -> bool:
        """
        Determines whether the step should retry based on the exception.

        :param exc: Exception = Raised exception

        :return: bool = True if retry should occur

        :example:
            >>> step = BaseStep.__subclasses__()[0]  # doctest: +ELLIPSIS
        """
        return isinstance(exc, self.retryable_exceptions)

    def getBackoffDelay(
            self,
            context: UploadPipelineContext,
            attempt: int
    ) -> float:
        """
        Calculates exponential backoff delay based on runtime configuration.

        The delay is dynamically obtained from the execution context,
        allowing user-defined retry strategies.

        Formula:
            delay = base_delay * (2 ** (attempt - 1))

        :param context: UploadPipelineContext = Execution context containing config
        :param attempt: int = Current attempt number (1-based)

        :return: float = Delay in seconds

        :raises ValueError:
            When attempt is invalid

        :example:
            >>> class Dummy(BaseStep):
            ...     def execute(self, context): pass
            >>> from pipefy.service.file.flows.config.uploadConfig import UploadConfig
            >>> ctx = type("Ctx", (), {"config": UploadConfig()})()
            >>> d = Dummy()
            >>> isinstance(d.getBackoffDelay(ctx, 1), float)
            True
        """
        if attempt <= 0:
            raise ValueError("attempt must be >= 1")

        base_delay = context.config.retry.base_delay

        return base_delay * (2 ** (attempt - 1))

    import random

    def getJitterDelay(
            self,
            context: UploadPipelineContext,
            attempt: int
    ) -> float:
        """
        Applies jitter to exponential backoff delay.

        Uses FULL JITTER strategy:
            delay = random(0, backoff_delay)

        :param context: UploadPipelineContext
        :param attempt: int

        :return: float

        :example:
            >>> class Dummy(BaseStep):
            ...     def execute(self, context): pass
            >>> from pipefy.service.file.flows.config.uploadConfig import UploadConfig
            >>> ctx = type("Ctx", (), {"config": UploadConfig()})()
            >>> d = Dummy()
            >>> isinstance(d.getJitterDelay(ctx, 1), float)
            True
        """
        base_delay = self.getBackoffDelay(context, attempt)
        return random.uniform(0, base_delay)
    # ============================================================
    # Dunder Methods
    # ============================================================

    def __str__(self) -> str:
        return f"<{self.__class__.__name__} retries={self.max_retries}>"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(retries={self.max_retries})>"