"""
Unit tests for card mutation builders.
"""

from __future__ import annotations

import pytest

from pipebridge.service.card.mutations.cardMutations import CardMutations


@pytest.mark.unit
def test_create_card_uses_graphql_input_literal_for_fields_attributes() -> None:
    """
    Validate that createCard serializes input objects as GraphQL, not raw JSON.
    """
    query = CardMutations.createCard(
        pipe_id="123",
        title="Card",
        fields_payload=[
            {
                "field_id": "nome_projetos",
                "field_value": '["IA Time"]',
            },
            {
                "field_id": "torre",
                "field_value": "OUTRA",
            },
        ],
    )

    assert 'title: "Card"' in query
    assert "fields_attributes: [{field_id: " in query
    assert '"field_id"' not in query
