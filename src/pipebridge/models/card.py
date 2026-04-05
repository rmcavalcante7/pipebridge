# ============================================================
# Dependencies
# ============================================================
from datetime import datetime
from typing import Any, Dict, List, Optional
import inspect

from pipebridge.models.base import BaseModel
from pipebridge.models.field import Field
from pipebridge.models.phase import Phase
from pipebridge.models.phaseHistory import PhaseHistory
from pipebridge.models.user import User
from pipebridge.models.label import Label
from pipebridge.exceptions import RequestError, ValidationError


class Card(BaseModel):
    """
    Represents a Pipefy card with full structured data.

    This model is the canonical source of truth for current card state inside
    the SDK. Internal lookup maps are maintained for efficiency, but semantic
    helper methods should be preferred over direct map access whenever
    possible.

    Preferred access patterns:

    - ``getField(...)``
    - ``hasField(...)``
    - ``requireField(...)``
    - ``getFieldValue(...)``
    - ``getFieldType(...)``
    - ``iterFields()``
    """

    def __init__(
        self,
        id: str,
        title: Optional[str],
        pipe_id: Optional[str],
        current_phase: Optional[Phase],
        phases_history: List[PhaseHistory],
        fields: List[Field],
        assignees: List[User],
        labels: List[Label],
    ) -> None:
        """
        Initialize a modeled Pipefy card.

        :param id: str = Card identifier
        :param title: str | None = Card title
        :param pipe_id: str | None = Parent pipe identifier
        :param current_phase: Phase | None = Current phase model
        :param phases_history: list[PhaseHistory] = Historic phase records
        :param fields: list[Field] = Current field values
        :param assignees: list[User] = Assigned users
        :param labels: list[Label] = Applied labels
        """
        self.id: str = id
        self.title: Optional[str] = title
        self.pipe_id: Optional[str] = pipe_id
        self.current_phase: Optional[Phase] = current_phase
        self.phases_history: List[PhaseHistory] = phases_history
        self.assignees: List[User] = assignees

        self.fields: List[Field] = fields
        # ============================================================
        # Fast lookup map (NEW)
        # ============================================================
        self.fields_map: Dict[str, Field] = {
            field.id: field for field in fields if field and field.id
        }

        self.labels: List[Label] = labels
        # ============================================================
        # Labels lookup map (NEW)
        # ============================================================
        self.labels_map: Dict[str, Label] = {
            label.id: label for label in labels if label and label.id
        }

    def __getitem__(self, field_id: str) -> Field:
        """
        Allow direct access to fields via indexing.

        This is kept as a convenience layer, but the preferred access style
        for SDK code is through semantic helpers such as ``getField()`` and
        ``requireField()``.

        :param field_id: str = Field identifier

        :return: Field

        :raises KeyError:
            If field does not exist

        :example:
            >>> card = Card.fromDict({"id": "1", "fields": []})
            >>> try:
            ...     card["x"]
            ... except KeyError:
            ...     True
            True
        """
        return self.fields_map[field_id]

    # ============================================================
    # Factory Methods
    # ============================================================

    @classmethod
    def fromDict(cls, data: Dict[str, Any]) -> Card:
        """
        Safely parse a Card from structured dictionary.

        This method is resilient to partial failures, null values,
        and inconsistent API responses. Invalid items are skipped
        instead of breaking the entire parsing process.

        :param data: dict = Structured card data

        :return: Card = Parsed Card model

        :raises RequestError:
            When input data is invalid or parsing fails critically

        :example:
            >>> data = {"id": "1", "fields": []}
            >>> card = Card.fromDict(data)
            >>> isinstance(card, Card)
            True
        """
        try:
            if not isinstance(data, dict):
                raise ValueError("Invalid card data type")

            # ============================================================
            # Parse error tracking (NEW)
            # ============================================================
            parse_errors: List[str] = []

            # ============================================================
            # BASIC
            # ============================================================
            id: str = str(data.get("id", ""))
            title: Optional[str] = data.get("title")
            pipe_id: Optional[str] = None

            pipe_data = data.get("pipe")
            if isinstance(pipe_data, dict):
                raw_pipe_id = pipe_data.get("id")
                if raw_pipe_id is not None:
                    pipe_id = str(raw_pipe_id)

            # ============================================================
            # PHASE
            # ============================================================
            current_phase_data: Optional[Dict[str, Any]] = data.get("current_phase")

            current_phase: Optional[Phase] = None
            if isinstance(current_phase_data, dict):
                try:
                    current_phase = Phase.fromDict(current_phase_data)
                except Exception as exc:
                    parse_errors.append(f"Phase parse error: {str(exc)}")

            # ============================================================
            # RAW LISTS
            # ============================================================
            phases_history_data: List[Any] = data.get("phases_history") or []
            fields_data: List[Any] = data.get("fields") or []
            assignees_data: List[Any] = data.get("assignees") or []
            labels_data: List[Any] = data.get("labels") or []

            # ============================================================
            # SAFE PARSING
            # ============================================================
            phases_history: List[PhaseHistory] = []
            for item in phases_history_data:
                try:
                    if item:
                        phases_history.append(PhaseHistory.fromDict(item))
                except Exception as exc:
                    parse_errors.append(f"PhaseHistory parse error: {str(exc)}")
                    continue

            fields: List[Field] = []
            for item in fields_data:
                try:
                    if item:
                        fields.append(Field.fromDict(item))
                except Exception as exc:
                    parse_errors.append(f"Field parse error: {str(exc)}")
                    continue

            assignees: List[User] = []
            for item in assignees_data:
                try:
                    if item:
                        assignees.append(User.fromDict(item))
                except Exception as exc:
                    parse_errors.append(f"User parse error: {str(exc)}")
                    continue

            labels: List[Label] = []
            for item in labels_data:
                try:
                    if item:
                        labels.append(Label.fromDict(item))
                except Exception as exc:
                    parse_errors.append(f"Label parse error: {str(exc)}")
                    continue

            # ============================================================
            # BUILD OBJECT
            # ============================================================
            card = cls(
                id=id,
                title=title,
                pipe_id=pipe_id,
                current_phase=current_phase,
                phases_history=phases_history,
                fields=fields,
                assignees=assignees,
                labels=labels,
            )

            # ============================================================
            # Attach parse errors (NEW)
            # ============================================================
            card._parse_errors = parse_errors

            return card

        except Exception as exc:
            raise RequestError(
                f"Class: {cls.__name__}\n" f"Method: fromDict\n" f"Error: {str(exc)}"
            ) from exc

    @classmethod
    def fromResponse(cls, response: Dict[str, Any]) -> "Card":
        """
        Parse API response into Card model.

        :param response: dict = Raw API response
        :return: Card

        :raises RequestError:
            When response structure is invalid
        :raises RequestError:
            When parsing fails

        :example:
            >>> response = {"data": {"card": {"id": "1"}}}
            >>> card = Card.fromResponse(response)
            >>> isinstance(card, Card)
            True
        """
        try:
            card_data: Dict[str, Any] = response.get("data", {}).get("card", {})

            if not card_data:
                raise ValueError("Card not found in response")

            return cls.fromDict(card_data)

        except Exception as exc:
            raise RequestError(
                f"Class: {cls.__name__}\n"
                f"Method: fromResponse\n"
                f"Error: {str(exc)}"
            ) from exc

    def getField(self, field_id: str) -> Optional[Field]:
        """
        Retrieve a field by its ID.

        This is the preferred non-raising accessor for card fields.

        :param field_id: str = Field identifier

        :return: Field | None = Field if found, otherwise None

        :example:
            >>> card = Card.fromDict({"id": "1", "fields": []})
            >>> card.getField("x") is None
            True
        """
        return self.fields_map.get(field_id)

    def hasField(self, field_id: str) -> bool:
        """
        Check whether a field exists in the card.

        :param field_id: str = Field identifier

        :return: bool = Whether the field exists
        """
        return self.getField(field_id) is not None

    def requireField(self, field_id: str) -> Field:
        """
        Retrieve a field and fail semantically when it does not exist.

        :param field_id: str = Field identifier

        :return: Field = Requested field

        :raises ValidationError:
            When the field does not exist in the card
        """
        field = self.getField(field_id)
        if field is None:
            raise ValidationError(
                message=f"Field '{field_id}' does not exist in card '{self.id}'",
                class_name=self.__class__.__name__,
                method_name="requireField",
            )
        return field

    def requireFieldValue(self, field_id: str) -> Any:
        """
        Retrieve the raw value of a field and fail when the field is missing.

        :param field_id: str = Field identifier

        :return: Any = Raw field value

        :raises ValidationError:
            When the field does not exist in the card
        """
        return self.requireField(field_id).value

    def iterFields(self) -> List[Field]:
        """
        Return all card fields as an ordered list.

        :return: list[Field] = Card fields
        """
        return list(self.fields)

    def getFieldsByType(self, field_type: str) -> List[Field]:
        """
        Retrieve all card fields matching a given type.

        :param field_type: str = Field type

        :return: list[Field] = Matching fields
        """
        return [field for field in self.fields if field and field.type == field_type]

    # ============================================================
    # Typed Field Accessors
    # ============================================================

    def getFieldValue(self, field_id: str) -> Optional[Any]:
        """
        Retrieve raw value of a field.

        :param field_id: str = Field identifier

        :return: Any | None = Field value

        :example:
            >>> card = Card.fromDict({"id": "1", "fields": []})
            >>> card.getFieldValue("x") is None
            True
        """
        field = self.getField(field_id)
        return field.value if field else None

    def getFieldType(self, field_id: str) -> Optional[str]:
        """
        Retrieve the field type from the current card payload.

        :param field_id: str = Field identifier

        :return: str | None = Field type when available
        """
        field = self.getField(field_id)
        return field.type if field else None

    def requireFieldType(self, field_id: str) -> str:
        """
        Retrieve the field type and fail when it is unavailable.

        :param field_id: str = Field identifier

        :return: str = Field type

        :raises ValidationError:
            When the field is missing or has no type metadata
        """
        field_type = self.getFieldType(field_id)
        if not field_type:
            raise ValidationError(
                message=f"Field '{field_id}' does not expose a type in card '{self.id}'",
                class_name=self.__class__.__name__,
                method_name="requireFieldType",
            )
        return field_type

    def getFieldLabel(self, field_id: str) -> Optional[str]:
        """
        Retrieve the field label from the current card payload.

        :param field_id: str = Field identifier

        :return: str | None = Field label when available
        """
        field = self.getField(field_id)
        return field.label if field else None

    def isFieldFilled(self, field_id: str) -> bool:
        """
        Check whether a field exists and contains a non-empty value.

        :param field_id: str = Field identifier

        :return: bool = Whether the field is filled
        """
        value = self.getFieldValue(field_id)
        if value is None:
            return False
        if isinstance(value, str):
            return bool(value.strip())
        if isinstance(value, list):
            return len(value) > 0
        return True

    def getText(self, field_id: str) -> Optional[str]:
        """
        Retrieve a text field value.

        :param field_id: str = Field identifier

        :return: str | None

        :example:
            >>> card = Card.fromDict({"id": "1", "fields": []})
            >>> card.getText("x") is None
            True
        """
        value = self.getFieldValue(field_id)
        return str(value) if value is not None else None

    def getNumber(self, field_id: str) -> Optional[float]:
        """
        Retrieve a numeric field value.

        :param field_id: str = Field identifier

        :return: float | None

        :raises ValueError:
            When value cannot be converted to number

        :example:
            >>> card = Card.fromDict({"id": "1", "fields": []})
            >>> card.getNumber("x") is None
            True
        """
        value = self.getFieldValue(field_id)

        if value is None:
            return None

        try:
            return float(value)
        except Exception as exc:
            raise RequestError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: getNumber\n"
                f"Error: Cannot convert value '{value}' to float"
            ) from exc

    def getBoolean(self, field_id: str) -> Optional[bool]:
        """
        Retrieve a boolean field value.

        :param field_id: str = Field identifier

        :return: bool | None

        :example:
            >>> card = Card.fromDict({"id": "1", "fields": []})
            >>> card.getBoolean("x") is None
            True
        """
        value = self.getFieldValue(field_id)

        if value is None:
            return None

        return str(value).lower() in ["true", "1", "yes"]

    def getDate(self, field_id: str) -> Optional[str]:
        """
        Retrieve a date field value (raw string).

        :param field_id: str = Field identifier

        :return: str | None

        :example:
            >>> card = Card.fromDict({"id": "1", "fields": []})
            >>> card.getDate("x") is None
            True
        """
        return self.getText(field_id)

    def getLabel(self, label_id: str) -> Optional[Label]:
        """
        Retrieve a label by its ID.

        :param label_id: str = Label identifier

        :return: Label | None

        :example:
            >>> card = Card.fromDict({"id": "1", "labels": []})
            >>> card.getLabel("x") is None
            True
        """
        return self.labels_map.get(label_id)

    def validateAgainstPhase(self, phase: "Phase") -> None:
        """
        Validate card fields against Phase schema, including type validation.

        This method ensures:
        - required fields are present
        - values match expected field types

        :param phase: Phase = Phase schema

        :return: None

        :raises ValidationError:
            When required fields are missing or type validation fails

        :example:
            >>> card = Card.fromDict({"id": "1", "fields": []})
            >>> phase = Phase.fromDict({"id": "1", "fields": []})
            >>> card.validateAgainstPhase(phase)
        """
        missing_fields = []
        invalid_type_fields = []

        for phase_field in phase.iterFields():
            field_id = phase_field.id
            card_field = self.getField(field_id)

            # ============================================================
            # REQUIRED VALIDATION
            # ============================================================
            if phase_field.required:
                if not card_field or not card_field.value:
                    missing_fields.append(field_id)
                    continue

            # Skip if no value
            if not card_field or card_field.value is None:
                continue

            value = card_field.value
            field_type = phase_field.type

            # ============================================================
            # TYPE VALIDATION
            # ============================================================

            try:
                if field_type in ("short_text", "long_text", "text"):
                    if not isinstance(value, str):
                        raise TypeError()

                elif field_type in ("number",):
                    if not isinstance(value, (int, float)):
                        # tenta cast
                        float(value)

                elif field_type in ("date", "datetime"):
                    if isinstance(value, str):
                        datetime.fromisoformat(value)
                    elif not isinstance(value, datetime):
                        raise TypeError()

                elif field_type in ("bool", "boolean"):
                    if not isinstance(value, bool):
                        raise TypeError()

                elif field_type in ("select", "radio"):
                    if not isinstance(value, str):
                        raise TypeError()

                elif field_type in ("multi_select", "checkbox"):
                    if not isinstance(value, list):
                        raise TypeError()

            except Exception:
                invalid_type_fields.append(field_id)

        # ============================================================
        # FINAL VALIDATION
        # ============================================================

        if missing_fields or invalid_type_fields:
            raise ValidationError(
                message=(
                    f"Validation failed | "
                    f"Missing: {missing_fields} | "
                    f"Invalid types: {invalid_type_fields}"
                ),
                context={"fields": missing_fields + invalid_type_fields},
            )


# ============================================================
# Main Test
# ============================================================

if __name__ == "__main__":
    sample = {
        "id": "123",
        "title": "Test Card",
        "current_phase": {"id": "1", "name": "Start"},
        "phases_history": [],
        "fields": [],
        "assignees": [],
        "labels": [],
    }

    card = Card.fromDict(sample)
    print(card.id, card.title)
