"""
Result model for card move flows.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class CardMoveResult:
    """
    Structured result returned by the safe card move flow.

    :param success: bool = Whether the move completed successfully
    :param response: dict[str, Any] = Raw move mutation response

    :example:
        >>> result = CardMoveResult(success=True)
        >>> result.success
        True
    """

    success: bool
    response: Dict[str, Any] = field(default_factory=dict)
