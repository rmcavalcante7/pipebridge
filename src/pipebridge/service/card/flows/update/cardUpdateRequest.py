"""
Structured request model for card field updates.
"""

from typing import Any, Dict, Optional

from pipebridge.exceptions import ValidationError
from pipebridge.exceptions.core.utils import getExceptionContext


class CardUpdateRequest:
    """
    Structured request object for card update flows.

    :param card_id: str = Card identifier
    :param fields: Dict[str, Any] = Field values mapped by logical field ID
    :param expected_phase_id: str | None = Optional expected current phase ID
    """

    def __init__(
        self,
        card_id: str,
        fields: Dict[str, Any],
        expected_phase_id: Optional[str] = None,
    ) -> None:
        """
        Initialize a structured request for card field updates.

        :param card_id: str = Card identifier
        :param fields: dict[str, Any] = Field values keyed by logical field ID
        :param expected_phase_id: str | None = Optional expected current phase ID

        :raises ValidationError:
            When request attributes are invalid
        """
        class_name, method_name = getExceptionContext(self)

        if not isinstance(card_id, str) or not card_id.strip():
            raise ValidationError(
                message="card_id must be a non-empty string",
                class_name=class_name,
                method_name=method_name,
            )

        if not isinstance(fields, dict) or not fields:
            raise ValidationError(
                message="fields must be a non-empty dictionary",
                class_name=class_name,
                method_name=method_name,
            )

        if expected_phase_id is not None and not isinstance(expected_phase_id, str):
            raise ValidationError(
                message="expected_phase_id must be a string when provided",
                class_name=class_name,
                method_name=method_name,
            )

        self.card_id = card_id
        self.fields = fields
        self.expected_phase_id = expected_phase_id
