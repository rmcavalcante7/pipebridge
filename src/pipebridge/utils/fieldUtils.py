# ============================================================
# Dependencies
# ============================================================
from typing import Any, Dict


class FieldUtils:
    """
    Utility for field operations.
    """

    @staticmethod
    def getFieldValueById(payload: Dict[str, Any], field_id: str) -> Any:
        """
        Extract field value by ID.

        :param payload: dict
        :param field_id: str
        :return: Any
        """
        fields = payload.get("fields", [])

        for field in fields:
            if field["field"]["id"] == field_id:
                return field.get("value")

        return None
