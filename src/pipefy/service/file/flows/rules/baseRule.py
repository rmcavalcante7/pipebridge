# ============================================================
# Dependencies
# ============================================================
from abc import ABC, abstractmethod
from pipefy.service.file.flows.pipeline.uploadPipelineContext import UploadPipelineContext


class BaseRule(ABC):
    """
    Abstract base class for all validation rules.

    A rule represents a business constraint that must be satisfied
    before executing the upload process.

    DESIGN PURPOSE:
        - Encapsulate validation logic
        - Enable extensibility
        - Support custom user-defined rules

    CONTRACT:
        - Must implement `execute`
        - Must raise exception when validation fails

    :example:
        >>> callable(BaseRule.execute)
        True
    """

    def __str__(self) -> str:
        """
        Human-readable representation.

        :return: str
        """
        return f"<{self.__class__.__name__}>"

    def __repr__(self) -> str:
        """
        Developer-friendly representation.

        :return: str
        """
        return f"<{self.__class__.__name__}()>"
    
    @abstractmethod
    def execute(self, context: UploadPipelineContext) -> None:
        """
        Executes rule validation.

        :param context: UploadPipelineContext = Shared execution context

        :return: None

        :raises ValidationError:
            When rule is violated
        """
        raise NotImplementedError

