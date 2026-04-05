"""
Usage example for updating supported fields in the current phase of a card.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from typing import Any

from pipebridge import CardUpdateConfig
from pipebridge.dispatcher.field.fieldType import FieldType
from pipebridge.models.card import Card
from pipebridge.models.phaseField import PhaseField
from useCases.common import add_connection_arguments, build_api, print_section


def build_text_value(field: PhaseField) -> str:
    safe_label = (field.label or field.id or "FIELD").strip().replace(" ", "_")
    return f"{safe_label}_USE_CASE_SDK"


def build_datetime_value() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_date_value() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def build_time_value() -> str:
    return "12:12"


def build_email_value(field: PhaseField) -> str:
    safe_label = (field.label or field.id or "field").strip().replace(" ", "_").lower()
    return f"{safe_label}@example-sdk.local"


def build_currency_value(card: Card, field: PhaseField) -> str:
    current_value = card.getFieldValue(field.id)
    if current_value is None:
        return "1234.56"
    try:
        normalized = (
            str(current_value)
            .replace("R$", "")
            .replace("$", "")
            .replace(".", "")
            .replace(",", ".")
            .strip()
        )
        return f"{float(normalized) + 1:.2f}"
    except Exception:
        return "1234.56"


def build_select_value(card: Card, field: PhaseField) -> tuple[bool, Any, str]:
    current_value = card.getFieldValue(field.id)
    options = field.options or []
    if not options:
        return False, None, "field has no configured options"
    if current_value in options and len(options) > 1:
        for option in options:
            if option != current_value:
                return (
                    True,
                    option,
                    f"changed option from '{current_value}' to '{option}'",
                )
    return True, options[0], f"initialized option with '{options[0]}'"


def build_number_value(card: Card, field: PhaseField) -> str:
    current_value = card.getFieldValue(field.id)
    if current_value is None:
        return "123"
    try:
        return str(int(float(str(current_value).replace(",", "."))) + 1)
    except Exception:
        return "123"


def resolve_update_value(
    card: Card,
    field: PhaseField,
    target_assignee_name: str | None = None,
) -> tuple[bool, Any, str]:
    field_type = field.type or ""

    if field_type in (FieldType.SHORT_TEXT, FieldType.LONG_TEXT):
        return True, build_text_value(field), "text field"
    if field_type in (
        FieldType.SELECT,
        FieldType.LABEL_SELECT,
        FieldType.RADIO_HORIZONTAL,
        FieldType.RADIO_VERTICAL,
    ):
        return build_select_value(card, field)
    if field_type in (FieldType.CHECKLIST_HORIZONTAL, FieldType.CHECKLIST_VERTICAL):
        options = field.options or []
        if not options:
            return False, None, "checklist field has no configured options"
        value = options[: min(2, len(options))]
        return True, value, f"using checklist value {value}"
    if field_type == FieldType.NUMBER:
        value = build_number_value(card, field)
        return True, value, f"number set to '{value}'"
    if field_type == FieldType.CURRENCY:
        value = build_currency_value(card, field)
        return True, value, f"currency set to '{value}'"
    if field_type == FieldType.EMAIL:
        value = build_email_value(field)
        return True, value, f"email set to '{value}'"
    if field_type == FieldType.DATE:
        return True, build_date_value(), "date updated with current UTC date"
    if field_type == FieldType.TIME:
        value = build_time_value()
        return True, value, f"time updated with '{value}'"
    if field_type in (FieldType.DATETIME, FieldType.DUE_DATE):
        return True, build_datetime_value(), "datetime updated with current UTC value"
    if field_type in (FieldType.ASSIGNEE, FieldType.ASSIGNEE_SELECT):
        if not target_assignee_name:
            return (
                False,
                None,
                "assignee skipped because no --target-assignee-name was provided",
            )
        return True, [target_assignee_name], f"assignee set to '{target_assignee_name}'"
    if field_type == FieldType.ATTACHMENT:
        return False, None, "attachment intentionally skipped in this example"
    if field_type == FieldType.CONNECTOR:
        return False, None, "connector intentionally skipped in V1 example"
    return False, None, f"unsupported field type '{field_type}'"


def main() -> None:
    """
    Execute the card current-phase update example.
    """
    parser = argparse.ArgumentParser(
        description="Update all supported fields from the current phase of a Pipefy card.",
    )
    add_connection_arguments(parser)
    parser.add_argument("--card-id", required=True, help="Card identifier.")
    parser.add_argument(
        "--target-assignee-name",
        help="Optional assignee display name used for assignee fields.",
    )
    args = parser.parse_args()

    api = build_api(token=args.token, base_url=args.base_url)

    print_section("Load Card And Phase")
    card = api.cards.get(args.card_id)
    current_phase = card.current_phase
    if current_phase is None:
        raise RuntimeError("The target card has no current phase.")

    phase = api.phases.get(current_phase.id)
    print(f"Card: {card.title} ({card.id})")
    print(f"Current phase: {phase.name} ({phase.id})")

    update_payload: dict[str, Any] = {}
    skipped: list[str] = []

    for phase_field in phase.iterFields():
        if not card.hasField(phase_field.id):
            skipped.append(f"{phase_field.id}: field is outside current card payload")
            continue

        supported, value, reason = resolve_update_value(
            card=card,
            field=phase_field,
            target_assignee_name=args.target_assignee_name,
        )
        if supported:
            update_payload[phase_field.id] = value
            print(f"[UPDATE] {phase_field.label} ({phase_field.type}) -> {reason}")
        else:
            skipped.append(f"{phase_field.id}: {reason}")

    if not update_payload:
        raise RuntimeError("No supported field updates were generated for this card.")

    print_section("Apply Updates")
    result = api.cards.updateFields(
        card_id=card.id,
        fields=update_payload,
        expected_phase_id=phase.id,
        config=CardUpdateConfig(
            validate_field_existence=True,
            validate_field_options=True,
            validate_field_type=True,
            validate_field_format=True,
        ),
    )

    print(f"Updated fields: {len(result)}")
    if skipped:
        print_section("Skipped Fields")
        for item in skipped:
            print(f"- {item}")


if __name__ == "__main__":
    main()
