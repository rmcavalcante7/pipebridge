"""
Integration tests for live connector discovery and semantic operations.
"""

from __future__ import annotations

from typing import Any

import pytest

from tests.live_examples import DEFAULT_LIVE_PIPE_ID

START_FORM_CONNECTOR_FIELD_ID = "nome_projetos"


@pytest.mark.integration
def test_connector_list_fields_live(live_pipefy_api: Any) -> None:
    """
    Validate live connector schema discovery through the public facade.
    """
    fields = live_pipefy_api.connectors.listFields(DEFAULT_LIVE_PIPE_ID)

    assert isinstance(fields, list)
    assert any(field.field_id == START_FORM_CONNECTOR_FIELD_ID for field in fields)

    connector = next(
        field for field in fields if field.field_id == START_FORM_CONNECTOR_FIELD_ID
    )
    assert connector.connected_repo is not None
    assert connector.connected_repo.id is not None
    assert connector.origin_type == "start_form"


@pytest.mark.integration
def test_connector_option_resolution_and_card_value_live(
    live_pipefy_api: Any, live_card_lifecycle_context: Any
) -> None:
    """
    Validate live connector value reading plus option listing and resolution.
    """
    value = live_pipefy_api.connectors.getCardValue(
        live_card_lifecycle_context.created_card_id,
        START_FORM_CONNECTOR_FIELD_ID,
    )

    if not value.item_ids:
        pytest.skip("Created card does not expose a filled connector value.")
    if not value.items or not value.items[0].title:
        pytest.skip("Connector value does not expose connected item metadata.")

    current_item_id = value.item_ids[0]
    current_item_title = value.items[0].title

    options = live_pipefy_api.connectors.listOptions(
        pipe_id=live_card_lifecycle_context.pipe_id,
        field_id=START_FORM_CONNECTOR_FIELD_ID,
        search=current_item_title[:4],
        limit=20,
    )
    assert any(option.id == current_item_id for option in options)

    resolved = live_pipefy_api.connectors.resolveOption(
        pipe_id=live_card_lifecycle_context.pipe_id,
        field_id=START_FORM_CONNECTOR_FIELD_ID,
        title=current_item_title,
    )
    assert resolved.id == current_item_id


@pytest.mark.integration
def test_connector_set_card_value_live_is_idempotent(
    live_pipefy_api: Any, live_card_lifecycle_context: Any
) -> None:
    """
    Validate live semantic connector update using the current value as replacement.
    """
    value = live_pipefy_api.connectors.getCardValue(
        live_card_lifecycle_context.created_card_id,
        START_FORM_CONNECTOR_FIELD_ID,
    )

    if not value.item_ids:
        pytest.skip("Created card does not expose a filled connector value.")

    live_pipefy_api.connectors.setCardValue(
        card_id=live_card_lifecycle_context.created_card_id,
        field_id=START_FORM_CONNECTOR_FIELD_ID,
        item_ids=list(value.item_ids),
    )

    refreshed = live_pipefy_api.connectors.getCardValue(
        live_card_lifecycle_context.created_card_id,
        START_FORM_CONNECTOR_FIELD_ID,
    )
    assert refreshed.item_ids == value.item_ids
