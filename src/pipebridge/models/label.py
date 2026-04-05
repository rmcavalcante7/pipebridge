# ============================================================
# Dependencies
# ============================================================
from typing import Dict, Optional, Any
import inspect

from pipebridge.models.base import BaseModel
from pipebridge.exceptions import RequestError


class Label(BaseModel):
    """
    Represents a Pipefy label.
    """

    def __init__(self, id: str, name: Optional[str]) -> None:
        """
        Initialize a Pipefy label model.

        :param id: str = Label identifier
        :param name: str | None = Label name
        """
        self.id: str = id
        self.name: Optional[str] = name

    @classmethod
    def fromDict(cls, data: Dict[str, Any]) -> "Label":
        """
        Safely parse a Label from structured data.

        :param data: dict = Raw label data

        :return: Label = Parsed Label instance

        :raises RequestError:
            When parsing fails critically

        :example:
            >>> label = Label.fromDict({"id": "1", "name": "Bug"})
            >>> isinstance(label, Label)
            True
        """
        try:
            if not isinstance(data, dict):
                raise ValueError("Invalid label data")

            return cls(id=str(data.get("id", "")), name=data.get("name"))

        except Exception as exc:
            raise RequestError(
                f"Class: {cls.__name__}\n" f"Method: fromDict\n" f"Error: {str(exc)}"
            ) from exc


# ============================================================
# Main Test
# ============================================================

if __name__ == "__main__":
    sample = {"id": "label_1", "name": "High Priority"}

    label = Label.fromDict(sample)
    print(label.id, label.name)
