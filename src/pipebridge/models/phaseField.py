# ============================================================
# Dependencies
# ============================================================
from typing import Optional, Dict, Any, List
import inspect

from pipebridge.exceptions import RequestError


class PhaseField:
    """
    Represents a Phase field schema.

    This model encapsulates metadata about a field within a Phase,
    including validation rules and descriptive attributes.

    :param id: str = Field identifier
    :param label: str | None = Field label
    :param type: str | None = Field type
    :param required: bool = Whether field is required
    :param description: str | None = Field description
    :param uuid: str | None = Field UUID exposed by the API
    """

    def __init__(
        self,
        id: str,
        label: Optional[str] = None,
        type: Optional[str] = None,
        required: bool = False,
        description: Optional[str] = None,
        options: Optional[List[str]] = None,
        uuid: Optional[str] = None,
    ) -> None:
        """
        Initialize phase field schema metadata.

        :param id: str = Field identifier
        :param label: str | None = Field label
        :param type: str | None = Pipefy field type
        :param required: bool = Whether the field is required in the phase
        :param description: str | None = Field description
        :param options: list[str] | None = Configured field options
        :param uuid: str | None = Field UUID exposed by the API
        """
        self.id: str = id
        self.label: Optional[str] = label
        self.type: Optional[str] = type
        self.required: bool = required
        self.description: Optional[str] = description
        self.options: List[str] = options or []
        self.uuid: Optional[str] = uuid

    # ============================================================
    # Factory Methods
    # ============================================================

    @classmethod
    def fromDict(cls, data: Dict[str, Any]) -> "PhaseField":
        """
        Safely parse a PhaseField from a dictionary.

        :param data: dict = Raw field data from API

        :return: PhaseField = Parsed PhaseField instance

        :raises RequestError:
            When parsing fails due to invalid structure or types

        :example:
            >>> field = PhaseField.fromDict({"id": "1"})
            >>> isinstance(field, PhaseField)
            True
        """
        try:
            if not isinstance(data, dict):
                raise ValueError("Invalid field data")

            return cls(
                id=str(data.get("id", "")),
                label=data.get("label"),
                type=data.get("type"),
                required=bool(data.get("required", False)),
                description=data.get("description"),
                options=data.get("options", []),
                uuid=data.get("uuid"),
            )

        except Exception as exc:
            raise RequestError(
                f"Class: {cls.__name__}\n" f"Method: fromDict\n" f"Error: {str(exc)}"
            ) from exc
