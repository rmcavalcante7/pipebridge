"""
Structured result for card update flows.
"""

from typing import Any, Dict


class CardUpdateResult:
    """
    Structured result of a card update flow execution.

    :example:
        >>> result = CardUpdateResult(success=True, responses={})
        >>> result.success
        True
    """

    def __init__(self, success: bool, responses: Dict[str, Any]) -> None:
        """
        Initialize a structured card update result.

        :param success: bool = Whether flow execution succeeded
        :param responses: dict[str, Any] = Raw responses keyed by updated field
        """
        self.success = success
        self.responses = responses

    def __repr__(self) -> str:
        """
        Build a concise debug representation of the result.

        :return: str = Debug representation
        """
        return (
            f"CardUpdateResult(success={self.success}, "
            f"fields={len(self.responses)})"
        )
