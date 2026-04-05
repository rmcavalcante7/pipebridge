"""
Structured request model for card move flows.
"""

from typing import Optional

from pipebridge.exceptions import ValidationError
from pipebridge.exceptions.core.utils import getExceptionContext


class CardMoveRequest:
    """
    Structured request object for safe card phase transitions.

    :param card_id: str = Card identifier
    :param destination_phase_id: str = Destination phase identifier
    :param expected_current_phase_id: str | None = Optional expected source
        phase identifier
    """

    def __init__(
        self,
        card_id: str,
        destination_phase_id: str,
        expected_current_phase_id: Optional[str] = None,
    ) -> None:
        """
        Initialize a structured request for a safe card move operation.

        :param card_id: str = Card identifier
        :param destination_phase_id: str = Destination phase identifier
        :param expected_current_phase_id: str | None = Optional expected source
            phase identifier

        :return: None

        :raises ValidationError:
            When any identifier is invalid

        :example:
            >>> request = CardMoveRequest("1", "2")
            >>> request.destination_phase_id
            '2'
        """
        class_name, method_name = getExceptionContext(self)

        if not isinstance(card_id, str) or not card_id.strip():
            raise ValidationError(
                message="card_id must be a non-empty string",
                class_name=class_name,
                method_name=method_name,
            )

        if (
            not isinstance(destination_phase_id, str)
            or not destination_phase_id.strip()
        ):
            raise ValidationError(
                message="destination_phase_id must be a non-empty string",
                class_name=class_name,
                method_name=method_name,
            )

        if expected_current_phase_id is not None and not isinstance(
            expected_current_phase_id, str
        ):
            raise ValidationError(
                message="expected_current_phase_id must be a string when provided",
                class_name=class_name,
                method_name=method_name,
            )

        self.card_id = card_id
        self.destination_phase_id = destination_phase_id
        self.expected_current_phase_id = expected_current_phase_id
