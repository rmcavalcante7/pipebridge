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

    RULE PRIORITY:
        Each rule defines its execution priority.

        Lower values → executed first

        :attribute priority: int = Execution priority (lower runs first)

    :example:
        >>> callable(BaseRule.execute)
        True
    """

    priority: int = 100 # default priority

    def __str__(self) -> str:
        """
        Human-readable representation.

        :return: str
        """
        return f"<{self.__class__.__name__} priority={self.priority}>"

    def __repr__(self) -> str:
        """
        Developer-friendly representation.

        :return: str
        """
        return f"<{self.__class__.__name__}() priority={self.priority}>"

    @abstractmethod
    def execute(self, context: UploadPipelineContext) -> None:
        """
        Executes rule validation.

        :param context: UploadPipelineContext = Shared execution context
        :attribute priority: int = Execution priority (lower runs first)

        :return: None

        :raises ValidationError:
            When rule is violated
        """
        raise NotImplementedError

