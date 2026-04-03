# ============================================================
# Dependencies
# ============================================================
from datetime import datetime
from typing import Any, Dict, List, Optional
import inspect

from pipefy.models.base import BaseModel
from pipefy.models.field import Field
from pipefy.models.phase import Phase
from pipefy.models.phaseHistory import PhaseHistory
from pipefy.models.user import User
from pipefy.models.label import Label
from pipefy.exceptions import RequestError, ValidationError


class Card(BaseModel):
    """
    Represents a Pipefy card with full structured data.
    """

    def __init__(
        self,
        id: str,
        title: Optional[str],
        current_phase: Optional[Phase],
        phases_history: List[PhaseHistory],
        fields: List[Field],
        assignees: List[User],
        labels: List[Label]
    ) -> None:
        self.id: str = id
        self.title: Optional[str] = title
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
                current_phase=current_phase,
                phases_history=phases_history,
                fields=fields,
                assignees=assignees,
                labels=labels
            )

            # ============================================================
            # Attach parse errors (NEW)
            # ============================================================
            card._parse_errors = parse_errors

            return card

        except Exception as exc:
            raise RequestError(
                f"Class: {cls.__name__}\n"
                f"Method: fromDict\n"
                f"Error: {str(exc)}"
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

        :param field_id: str = Field identifier

        :return: Field | None = Field if found, otherwise None

        :example:
            >>> card = Card.fromDict({"id": "1", "fields": []})
            >>> card.getField("x") is None
            True
        """
        return self.fields_map.get(field_id)

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

        for field_id, phase_field in phase.fields_map.items():
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
                fields=missing_fields + invalid_type_fields
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
        "labels": []
    }

    card = Card.fromDict(sample)
    print(card.id, card.title)