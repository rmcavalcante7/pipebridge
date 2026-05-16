# ============================================================
# Dependencies
# ============================================================
from typing import Any, Dict, List, Optional

from pipebridge.models.base import BaseModel
from pipebridge.models.connectedRepoItem import ConnectedRepoItem
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
        array_value: Optional[List[Any]] = None,
        native_value: Any = None,
        connected_items: Optional[List[ConnectedRepoItem]] = None,
    ) -> None:
        """
        Initialize a card field model.

        :param id: str = Field identifier
        :param label: str | None = Human-readable field label
        :param type: str | None = Pipefy field type
        :param value: Any = Raw field value
        :param report_value: Any = Report-oriented field value
        :param array_value: list[Any] | None = Array-typed field value
        :param native_value: Any = Native/display value returned by the API
        :param connected_items: list[ConnectedRepoItem] | None = Connected repo items
        """
        self.id: str = id
        self.label: Optional[str] = label
        self.type: Optional[str] = type
        self.value: Any = value
        self.report_value: Any = report_value
        self.array_value: List[Any] = list(array_value or [])
        self.native_value: Any = native_value
        self.connected_items: List[ConnectedRepoItem] = list(connected_items or [])

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
            array_value_raw: Any = data.get("array_value")
            array_value: List[Any] = (
                list(array_value_raw) if isinstance(array_value_raw, list) else []
            )
            native_value: Any = data.get("native_value")

            connected_items_raw: Any = data.get("connectedRepoItems") or []
            connected_items: List[ConnectedRepoItem] = []
            if isinstance(connected_items_raw, list):
                for item in connected_items_raw:
                    if isinstance(item, dict):
                        connected_items.append(ConnectedRepoItem.fromDict(item))

            return cls(
                id=field_id,
                label=label,
                type=field_type,
                value=value,
                report_value=report_value,
                array_value=array_value,
                native_value=native_value,
                connected_items=connected_items,
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
