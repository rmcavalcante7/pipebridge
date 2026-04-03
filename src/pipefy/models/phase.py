# ============================================================
# Dependencies
# ============================================================
from typing import Optional, List, Dict, Any
import inspect

from pipefy.exceptions import RequestError
from pipefy.models.phaseField import PhaseField


class Phase:
    """
    Represents a Pipefy Phase with extended metadata.

    This model supports full parsing including:
    - basic info
    - fields
    - pipe
    - cards preview

    :param id: str = Phase identifier
    :param name: str | None = Phase name
    :param fields: list[dict] = Phase fields
    :param pipe: dict | None = Parent pipe
    :param cards_preview: list[dict] = Preview of cards
    """

    def __init__(
            self,
            id: str,
            name: Optional[str] = None,
            fields: Optional[List[PhaseField]] = None,
            cards_preview: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        self.id: str = id
        self.name: Optional[str] = name

        # ============================================================
        # INTERNAL STORAGE (FIX)
        # ============================================================
        self._fields: List[PhaseField] = fields or []
        self.cards_preview: List[Dict[str, Any]] = cards_preview or []

        # ============================================================
        # Fast lookup map (LIKE CARD)
        # ============================================================
        self.fields_map: Dict[str, PhaseField] = {
            field.id: field
            for field in self._fields
            if field and field.id
        }

    def __getitem__(self, field_id: str) -> PhaseField:
        """
        Retrieve a field using dictionary-like access.

        :param field_id: str = Field identifier

        :return: PhaseField = Field metadata

        :raises KeyError:
            If field does not exist

        :example:
            >>> phase = Phase.fromDict({"id": "1", "fields": []})
            >>> try:
            ...     phase["x"]
            ... except KeyError:
            ...     True
            True
        """
        return self.fields_map[field_id]

    @property
    def fields(self) -> List[PhaseField]:
        """
        Retrieve all phase fields.

        WARNING:
            Prefer using getField() or [] access for O(1) lookup.

        :return: list[PhaseField]

        :example:
            >>> phase = Phase.fromDict({"id": "1", "fields": []})
            >>> isinstance(phase.fields, list)
            True
        """
        return self._fields

    # ============================================================
    # FACTORY
    # ============================================================

    @classmethod
    def fromDict(cls, data: Dict[str, Any]) -> "Phase":
        """
        Safely parse Phase from structured data.

        :param data: dict = Raw phase data

        :return: Phase

        :raises RequestError:
            When parsing fails

        :example:
            >>> phase = Phase.fromDict({"id": "1"})
            >>> isinstance(phase, Phase)
            True
        """
        try:
            if not isinstance(data, dict):
                raise ValueError("Invalid phase data")

            # ============================================================
            # Parse error tracking
            # ============================================================
            parse_errors: List[str] = []

            # ============================================================
            # BASIC
            # ============================================================
            id: str = str(data.get("id", ""))
            name: Optional[str] = data.get("name")

            # ============================================================
            # FIELDS
            # ============================================================
            fields_data: List[Any] = data.get("fields") or []

            fields: List[PhaseField] = []
            for item in fields_data:
                try:
                    if item:
                        fields.append(PhaseField.fromDict(item))
                except Exception as exc:
                    parse_errors.append(
                        f"PhaseField parse error: {str(exc)}"
                    )
                    continue

            # ============================================================
            # CARDS PREVIEW
            # ============================================================
            cards_edges = data.get("cards", {}).get("edges", [])

            cards_preview: List[Dict[str, Any]] = []
            for edge in cards_edges:
                try:
                    node = edge.get("node", {})
                    if node:
                        cards_preview.append(node)
                except Exception as exc:
                    parse_errors.append(
                        f"Card preview parse error: {str(exc)}"
                    )
                    continue

            # ============================================================
            # BUILD OBJECT
            # ============================================================
            phase = cls(
                id=id,
                name=name,
                fields=fields,
                cards_preview=cards_preview
            )

            phase._parse_errors = parse_errors

            return phase

        except Exception as exc:
            raise RequestError(
                f"Class: {cls.__name__}\n"
                f"Method: fromDict\n"
                f"Error: {str(exc)}"
            ) from exc

    # ============================================================
    # HELPERS
    # ============================================================

    def getField(self, field_id: str) -> Optional[PhaseField]:
        """
        Retrieve a field metadata by its identifier.

        :param field_id: str = Field identifier

        :return: PhaseField | None

        :example:
            >>> phase = Phase.fromDict({"id": "1", "fields": []})
            >>> phase.getField("x") is None
            True
        """
        return self.fields_map.get(field_id)

