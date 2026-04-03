# ============================================================
# Dependencies
# ============================================================
from typing import Dict, Optional, Any
import inspect

from pipefy.models.base import BaseModel
from pipefy.models.phase import Phase
from pipefy.exceptions import RequestError


class PhaseHistory(BaseModel):
    """
    Represents a card phase history entry.
    """

    def __init__(
        self,
        phase: Phase,
        first_time_in: Optional[str],
        last_time_in: Optional[str]
    ) -> None:
        self.phase: Phase = phase
        self.first_time_in: Optional[str] = first_time_in
        self.last_time_in: Optional[str] = last_time_in

    @classmethod
    def fromDict(cls, data: Dict[str, Any]) -> "PhaseHistory":
        """
        Safely parse a PhaseHistory entry.

        This method tolerates partial or inconsistent data
        and skips invalid structures when necessary.

        :param data: dict = Raw phase history data

        :return: PhaseHistory = Parsed instance

        :raises RequestError:
            When parsing fails critically

        :example:
            >>> data = {"phase": {"id": "1"}, "firstTimeIn": None}
            >>> ph = PhaseHistory.fromDict(data)
            >>> isinstance(ph, PhaseHistory)
            True
        """
        try:
            if not isinstance(data, dict):
                raise ValueError("Invalid phase history data")

            phase_data: Dict[str, Any] = data.get("phase") or {}

            if not isinstance(phase_data, dict):
                raise ValueError("Invalid phase structure")

            return cls(
                phase=Phase.fromDict(phase_data),
                first_time_in=data.get("firstTimeIn"),
                last_time_in=data.get("lastTimeIn")
            )

        except Exception as exc:
            raise RequestError(
                f"Class: {cls.__name__}\n"
                f"Method: fromDict\n"
                f"Error: {str(exc)}"
            ) from exc


# ============================================================
# Main Test
# ============================================================

if __name__ == "__main__":
    sample = {
        "phase": {"id": "phase_1", "name": "Start"},
        "firstTimeIn": "2024-01-01",
        "lastTimeIn": "2024-01-02"
    }

    ph = PhaseHistory.fromDict(sample)
    print(ph.phase.name, ph.first_time_in)