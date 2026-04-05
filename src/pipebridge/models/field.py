# ============================================================
# Dependencies
# ============================================================
from typing import Any, Dict, Optional
import inspect

from pipebridge.models.base import BaseModel
from pipebridge.exceptions import RequestError


class Field(BaseModel):
    """
    Represents a card field with metadata and values.
    """

    def __init__(
        self,
        id: str,
        label: Optional[str],
        type: Optional[str],
        value: Any,
        report_value: Any,
    ) -> None:
        """
        Initialize a card field model.

        :param id: str = Field identifier
        :param label: str | None = Human-readable field label
        :param type: str | None = Pipefy field type
        :param value: Any = Raw field value
        :param report_value: Any = Report-oriented field value
        """
        self.id: str = id
        self.label: Optional[str] = label
        self.type: Optional[str] = type
        self.value: Any = value
        self.report_value: Any = report_value

    @classmethod
    def fromDict(cls, data: Dict[str, Any]) -> "Field":
        """
        Safely parse a Field from structured data.

        This method is resilient to null values, missing keys,
        and inconsistent API structures.

        :param data: dict = Raw field data from API

        :return: Field = Parsed Field instance

        :raises RequestError:
            When parsing fails critically

        :example:
            >>> data = {"field": {"id": "1"}, "value": "A", "report_value": "A"}
            >>> field = Field.fromDict(data)
            >>> isinstance(field, Field)
            True
        """
        try:
            if not isinstance(data, dict):
                raise ValueError("Invalid field data type")

            # ============================================================
            # SAFE FIELD METADATA
            # ============================================================
            field_meta: Dict[str, Any] = data.get("field") or {}

            if not isinstance(field_meta, dict):
                field_meta = {}

            field_id: str = str(field_meta.get("id", ""))
            label: Optional[str] = field_meta.get("label")
            field_type: Optional[str] = field_meta.get("type")

            # ============================================================
            # SAFE VALUES
            # ============================================================
            value: Any = data.get("value")
            report_value: Any = data.get("report_value")

            return cls(
                id=field_id,
                label=label,
                type=field_type,
                value=value,
                report_value=report_value,
            )

        except Exception as exc:
            raise RequestError(
                f"Class: {cls.__name__}\n" f"Method: fromDict\n" f"Error: {str(exc)}"
            ) from exc


# ============================================================
# Main Test
# ============================================================

if __name__ == "__main__":
    sample = {
        "field": {"id": "status", "label": "Status", "type": "short_text"},
        "value": "Open",
        "report_value": "Open",
    }

    field = Field.fromDict(sample)
    print(field.id, field.value)
