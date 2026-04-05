# ============================================================
# Dependencies
# ============================================================
from typing import Optional, List, Dict, Any
import inspect

from pipebridge.exceptions import RequestError
from pipebridge.models.base import BaseModel
from pipebridge.models.phaseField import PhaseField


class Phase(BaseModel):
    """
    Represents a Pipefy Phase with extended metadata.

    This model supports full parsing including:
    - basic info
    - fields
    - pipe
    - cards preview

    This model is the canonical representation of phase schema metadata. Its
    internal maps exist for efficient lookup, but SDK code should prefer
    semantic helpers instead of direct map access whenever possible.

    Preferred access patterns:

    - ``getField(...)``
    - ``hasField(...)``
    - ``requireField(...)``
    - ``getFieldType(...)``
    - ``getFieldOptions(...)``
    - ``isFieldRequired(...)``
    - ``iterFields()``

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
        cards_preview: Optional[List[Dict[str, Any]]] = None,
        cards_can_be_moved_to_phases: Optional[List["Phase"]] = None,
        next_phase_ids: Optional[List[str]] = None,
    ) -> None:
        """
        Initialize a modeled Pipefy phase schema.

        :param id: str = Phase identifier
        :param name: str | None = Phase name
        :param fields: list[PhaseField] | None = Schema fields configured in the phase
        :param cards_preview: list[dict[str, Any]] | None = Optional cards preview payload
        :param cards_can_be_moved_to_phases: list[Phase] | None = Allowed move targets
        :param next_phase_ids: list[str] | None = Allowed target phase identifiers
        """
        self.id: str = id
        self.name: Optional[str] = name

        # ============================================================
        # INTERNAL STORAGE (FIX)
        # ============================================================
        self._fields: List[PhaseField] = fields or []
        self.cards_preview: List[Dict[str, Any]] = cards_preview or []
        self._cards_can_be_moved_to_phases: List["Phase"] = (
            cards_can_be_moved_to_phases or []
        )
        self.next_phase_ids: List[str] = list(next_phase_ids or [])

        # ============================================================
        # Fast lookup map (LIKE CARD)
        # ============================================================
        self.fields_map: Dict[str, PhaseField] = {
            field.id: field for field in self._fields if field and field.id
        }
        self.cards_can_be_moved_to_phases_map: Dict[str, "Phase"] = {
            phase.id: phase
            for phase in self._cards_can_be_moved_to_phases
            if phase and phase.id
        }

    def __getitem__(self, field_id: str) -> PhaseField:
        """
        Retrieve a field using dictionary-like access.

        This is preserved as a convenience layer, but semantic helpers such
        as ``getField()`` and ``requireField()`` should be preferred in SDK
        code.

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
                    parse_errors.append(f"PhaseField parse error: {str(exc)}")
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
                    parse_errors.append(f"Card preview parse error: {str(exc)}")
                    continue

            # ============================================================
            # PHASE TRANSITIONS
            # ============================================================
            move_targets_data: List[Any] = (
                data.get("cards_can_be_moved_to_phases") or []
            )
            cards_can_be_moved_to_phases: List["Phase"] = []
            for item in move_targets_data:
                try:
                    if isinstance(item, dict) and item.get("id") is not None:
                        cards_can_be_moved_to_phases.append(
                            cls(
                                id=str(item.get("id", "")),
                                name=item.get("name"),
                            )
                        )
                except Exception as exc:
                    parse_errors.append(f"Move target phase parse error: {str(exc)}")
                    continue

            next_phase_ids = [
                str(phase_id)
                for phase_id in (data.get("next_phase_ids") or [])
                if phase_id is not None
            ]

            # ============================================================
            # BUILD OBJECT
            # ============================================================
            phase = cls(
                id=id,
                name=name,
                fields=fields,
                cards_preview=cards_preview,
                cards_can_be_moved_to_phases=cards_can_be_moved_to_phases,
                next_phase_ids=next_phase_ids,
            )

            phase._parse_errors = parse_errors

            return phase

        except Exception as exc:
            raise RequestError(
                f"Class: {cls.__name__}\n" f"Method: fromDict\n" f"Error: {str(exc)}"
            ) from exc

    # ============================================================
    # HELPERS
    # ============================================================

    def getField(self, field_id: str) -> Optional[PhaseField]:
        """
        Retrieve a field metadata by its identifier.

        This is the preferred non-raising accessor for phase schema fields.

        :param field_id: str = Field identifier

        :return: PhaseField | None

        :example:
            >>> phase = Phase.fromDict({"id": "1", "fields": []})
            >>> phase.getField("x") is None
            True
        """
        return self.fields_map.get(field_id)

    def getFieldType(self, field_id: str) -> Optional[str]:
        """
        Retrieve the configured type of a phase field.

        :param field_id: str = Field identifier

        :return: str | None = Field type when available
        """
        field = self.getField(field_id)
        return field.type if field else None

    def requireFieldType(self, field_id: str) -> str:
        """
        Retrieve the configured type of a phase field and fail if missing.

        :param field_id: str = Field identifier

        :return: str = Field type

        :raises RequestError:
            When the field does not exist or has no type
        """
        field_type = self.getFieldType(field_id)
        if not field_type:
            raise RequestError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: requireFieldType\n"
                f"Error: Field '{field_id}' does not expose a type in phase '{self.id}'"
            )
        return field_type

    def getFieldLabel(self, field_id: str) -> Optional[str]:
        """
        Retrieve the configured label of a phase field.

        :param field_id: str = Field identifier

        :return: str | None = Field label when available
        """
        field = self.getField(field_id)
        return field.label if field else None

    def getFieldOptions(self, field_id: str) -> List[str]:
        """
        Retrieve the configured options of a phase field.

        :param field_id: str = Field identifier

        :return: list[str] = Configured field options
        """
        field = self.getField(field_id)
        return list(field.options) if field and field.options else []

    def requireFieldOptions(self, field_id: str) -> List[str]:
        """
        Retrieve the configured options of a phase field and fail if empty.

        :param field_id: str = Field identifier

        :return: list[str] = Configured field options

        :raises RequestError:
            When the field does not exist or has no configured options
        """
        options = self.getFieldOptions(field_id)
        if not options:
            raise RequestError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: requireFieldOptions\n"
                f"Error: Field '{field_id}' has no configured options in phase '{self.id}'"
            )
        return options

    def isFieldRequired(self, field_id: str) -> bool:
        """
        Check whether a phase field is required.

        :param field_id: str = Field identifier

        :return: bool = Whether the field is required
        """
        field = self.getField(field_id)
        return bool(field.required) if field else False

    def hasField(self, field_id: str) -> bool:
        """
        Check whether a field belongs to this phase.

        :param field_id: str = Field identifier

        :return: bool = Whether the field exists
        """
        return self.getField(field_id) is not None

    def requireField(self, field_id: str) -> PhaseField:
        """
        Retrieve a phase field and fail when it does not exist.

        :param field_id: str = Field identifier

        :return: PhaseField = Requested field schema

        :raises RequestError:
            When the field does not exist in the phase
        """
        field = self.getField(field_id)
        if field is None:
            raise RequestError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: requireField\n"
                f"Error: Field '{field_id}' does not exist in phase '{self.id}'"
            )
        return field

    def iterFields(self) -> List[PhaseField]:
        """
        Return all phase fields as an ordered list.

        :return: list[PhaseField] = Phase fields
        """
        return list(self.fields)

    def getMoveTargetPhase(self, phase_id: str) -> Optional["Phase"]:
        """
        Retrieve an allowed destination phase by identifier.

        :param phase_id: str = Destination phase identifier

        :return: Phase | None = Allowed destination phase when available
        """
        return self.cards_can_be_moved_to_phases_map.get(phase_id)

    def canMoveToPhase(self, phase_id: str) -> bool:
        """
        Check whether cards from this phase can be moved to a destination.

        :param phase_id: str = Destination phase identifier

        :return: bool = Whether the transition is allowed
        """
        return self.getMoveTargetPhase(phase_id) is not None

    def iterMoveTargetPhases(self) -> List["Phase"]:
        """
        Return all destination phases configured as valid transitions.

        :return: list[Phase] = Allowed move target phases
        """
        return list(self._cards_can_be_moved_to_phases)

    def getFieldsByType(self, field_type: str) -> List[PhaseField]:
        """
        Retrieve all phase fields matching a given type.

        :param field_type: str = Field type

        :return: list[PhaseField] = Matching field schemas
        """
        return [field for field in self.fields if field and field.type == field_type]
