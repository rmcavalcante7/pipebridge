# ============================================================
# Dependencies
# ============================================================
from abc import ABC, abstractmethod

from pipebridge.integrations.file.fileUploadResult import FileUploadResult
from pipebridge.models.file.fileUploadRequest import FileUploadRequest


# ============================================================
# BaseFileUploadFlow
# ============================================================
class BaseFileUploadFlow(ABC):
    """
    Abstract base class for file upload flows.

    This class defines the contract for all upload flow implementations.

    Its purpose is to ensure consistency across different versions of
    upload flows (e.g., V1, V2, future versions), enabling safe evolution
    of the system without breaking existing behavior.

    DESIGN PRINCIPLES:
        - Enforces a stable interface (`execute`)
        - Enables polymorphism
        - Supports versioning strategy
        - Avoids conditional logic inside flows

    IMPORTANT:
        This class must NOT contain any implementation logic.
        All logic must be implemented in subclasses.

    :example:
        >>> callable(BaseFileUploadFlow.execute)
        True
    """

    # ============================================================
    # Public API
    # ============================================================

    @abstractmethod
    def execute(self, request: FileUploadRequest) -> FileUploadResult:
        """
        Executes the upload flow.

        This method must be implemented by all concrete flow classes.

        :param request: FileUploadRequest = Upload request object

        :return: FileUploadResult = Result of upload operation

        :raises NotImplementedError:
            When method is not implemented by subclass

        :example:
            >>> callable(BaseFileUploadFlow.execute)
            True
        """
        raise NotImplementedError(
            f"{self.__class__.__name__}.execute must be implemented"
        )


# ============================================================
# MAIN TEST
# ============================================================
if __name__ == "__main__":
    print("BaseFileUploadFlow loaded successfully")
