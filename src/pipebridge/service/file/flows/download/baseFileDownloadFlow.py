# ============================================================
# Dependencies
# ============================================================
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from pipebridge.models.file.fileDownloadRequest import FileDownloadRequest


class BaseFileDownloadFlow(ABC):
    """
    Abstract contract for file download flows.

    This base class keeps the file subdomain symmetrical: both upload and
    download are explicit flows with stable execution contracts.

    :example:
        >>> callable(BaseFileDownloadFlow.execute)
        True
    """

    @abstractmethod
    def execute(self, request: FileDownloadRequest) -> List[Path]:
        """
        Execute the download flow.

        :param request: FileDownloadRequest = Structured download request

        :return: List[Path] = Saved file paths

        :raises NotImplementedError:
            When the concrete flow does not implement execution

        :example:
            >>> callable(BaseFileDownloadFlow.execute)
            True
        """
        raise NotImplementedError(
            f"{self.__class__.__name__}.execute must be implemented"
        )
