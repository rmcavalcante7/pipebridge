from abc import ABC, abstractmethod
from pipefy.service.file.flows.pipeline.uploadPipelineContext import UploadPipelineContext


class BaseUploadStep(ABC):
    """
    Abstract base class for all upload pipeline steps.

    This class defines the contract that all pipeline steps must follow.

    Each step:
        - Receives a strongly-typed UploadPipelineContext
        - Performs a single, well-defined responsibility
        - May mutate the context

    DESIGN PRINCIPLES:
        - Single Responsibility Principle (SRP)
        - Open/Closed Principle (OCP)
        - Pipeline composability

    :example:
        >>> callable(BaseUploadStep.execute)
        True
    """

    def __str__(self) -> str:
        """
        Returns a human-readable representation of the step.

        :return: str

        :example:
            >>> str(BaseUploadStep)
            "<BaseUploadStep>"
        """
        return f"<{self.__class__.__name__}>"

    def __repr__(self) -> str:
        """
        Returns a developer-friendly representation.

        :return: str

        :example:
            >>> repr(BaseUploadStep)
            "<BaseUploadStep()>"
        """
        return f"<{self.__class__.__name__}()>"

    @abstractmethod
    def execute(self, context: UploadPipelineContext) -> None:
        """
        Executes step logic.

        :param context: UploadPipelineContext = Shared execution context

        :return: None

        :raises NotImplementedError:
            When not implemented by subclass
        """
        raise NotImplementedError

