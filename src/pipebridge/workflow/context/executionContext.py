# ============================================================
# Dependencies
# ============================================================
from typing import Any, Dict, Optional


class ExecutionContext:
    """
    Base context shared across workflow executions.

    This class provides a neutral execution context that can be extended
    by domain-specific flows such as file upload or card updates.

    The base context intentionally contains only metadata storage so that
    generic workflow engines remain decoupled from business-specific data.

    :param metadata: Optional[Dict[str, Any]] = Arbitrary execution metadata

    :example:
        >>> context = ExecutionContext(metadata={"flow": "upload"})
        >>> context.metadata["flow"]
        'upload'
    """

    def __init__(self, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize ExecutionContext.

        :param metadata: Optional[Dict[str, Any]] = Arbitrary execution metadata

        :return: None

        :example:
            >>> context = ExecutionContext()
            >>> isinstance(context.metadata, dict)
            True
        """
        self.metadata: Dict[str, Any] = metadata or {}
