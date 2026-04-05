"""
Integration tests for the live card update flow.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pytest

from pipebridge.dispatcher.field.fieldType import FieldType
from pipebridge.models.card import Card
from pipebridge.models.phaseField import PhaseField
from pipebridge.service.card.flows.update.cardUpdateConfig import CardUpdateConfig


def _build_text_value(field: PhaseField) -> str:
    safe_label = (field.label or field.id or "FIELD").strip().replace(" ", "_")
    return f"{safe_label}_TESTE_PYTEST_SDK"


def _build_date_value() -> str:
    return datetime.now(timezone.utc).isoformat()


def _build_calendar_date_value() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def _build_time_value() -> str:
    return "12:12"


def _build_email_value(field: PhaseField) -> str:
    safe_label = (field.label or field.id or "field").strip().replace(" ", "_").lower()
    return f"{safe_label}@pytest-pipfey.local"


def _build_currency_value(card: Card, field: PhaseField) -> str:
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


def _build_select_value(card: Card, field: PhaseField) -> tuple[bool, Any]:
    current_value = card.getFieldValue(field.id)
    options = field.options or []
    if not options:
        return False, None
    if current_value in options and len(options) > 1:
        for option in options:
            if option != current_value:
                return True, option
    return True, options[0]


def _build_number_value(card: Card, field: PhaseField) -> str:
    current_value = card.getFieldValue(field.id)
    if current_value is None:
        return "123"
    try:
        return str(int(float(str(current_value).replace(",", "."))) + 1)
    except Exception:
        return "123"


def _resolve_update_value(
    card: Card,
    field: PhaseField,
    target_assignee_name: str | None = None,
) -> tuple[bool, Any]:
    field_type = field.type or ""

    if field_type in (FieldType.SHORT_TEXT, FieldType.LONG_TEXT):
        return True, _build_text_value(field)
    if field_type in (
        FieldType.SELECT,
        FieldType.LABEL_SELECT,
        FieldType.RADIO_HORIZONTAL,
        FieldType.RADIO_VERTICAL,
    ):
        return _build_select_value(card, field)
    if field_type in (FieldType.CHECKLIST_HORIZONTAL, FieldType.CHECKLIST_VERTICAL):
        options = field.options or []
        return (True, options[: min(2, len(options))]) if options else (False, None)
    if field_type == FieldType.NUMBER:
        return True, _build_number_value(card, field)
    if field_type == FieldType.CURRENCY:
        return True, _build_currency_value(card, field)
    if field_type == FieldType.EMAIL:
        return True, _build_email_value(field)
    if field_type == FieldType.DATE:
        return True, _build_calendar_date_value()
    if field_type == FieldType.TIME:
        return True, _build_time_value()
    if field_type in (FieldType.DATETIME, FieldType.DUE_DATE):
        return True, _build_date_value()
    if field_type in (FieldType.ATTACHMENT, FieldType.CONNECTOR):
        return False, None
    if field_type in (FieldType.ASSIGNEE, FieldType.ASSIGNEE_SELECT):
        return (True, [target_assignee_name]) if target_assignee_name else (False, None)
    return False, None


@pytest.mark.integration
def test_card_update_flow_live(live_pipefy_api: Any) -> None:
    """
    Exercise the real card update flow against a configured live card.
    """
    card_id = "1330664077"
    target_assignee_name = "RAFAEL MOTA CAVALCANTE"

    card = live_pipefy_api.cards.get(card_id)
    current_phase = card.current_phase
    assert current_phase is not None

    phase = live_pipefy_api.phases.get(current_phase.id)
    update_payload: dict[str, Any] = {}

    for phase_field in phase.iterFields():
        if not card.hasField(phase_field.id):
            continue
        supported, value = _resolve_update_value(
            card=card,
            field=phase_field,
            target_assignee_name=target_assignee_name,
        )
        if supported:
            update_payload[phase_field.id] = value

    assert update_payload, "At least one supported field must be found for live update"

    result = live_pipefy_api.cards.updateFields(
        card_id=card_id,
        fields=update_payload,
        expected_phase_id=current_phase.id,
        config=CardUpdateConfig(
            validate_field_existence=True,
            validate_field_options=True,
            validate_field_type=True,
            validate_field_format=True,
        ),
    )

    assert isinstance(result, dict)
    assert result
