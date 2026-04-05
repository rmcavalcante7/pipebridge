"""
Usage example for registering a custom card update handler at runtime.
"""

from __future__ import annotations

import argparse
from typing import Any, Optional

from pipebridge.models.field import Field
from pipebridge.models.phaseField import PhaseField
from pipebridge.service.card.flows.update.dispatcher.baseCardFieldUpdateHandler import (
    BaseCardFieldUpdateHandler,
)
from pipebridge.service.card.flows.update.dispatcher.resolvedFieldUpdate import (
    ResolvedFieldUpdate,
)
from useCases.common import add_connection_arguments, build_api, print_section


class UppercaseTextHandler(BaseCardFieldUpdateHandler):
    """
    Example custom handler that uppercases incoming text before update.
    """

    def resolve(
        self,
        field_id: str,
        field_type: str,
        input_value: Any,
        current_field: Optional[Field] = None,
        phase_field: Optional[PhaseField] = None,
    ) -> ResolvedFieldUpdate:
        """
        Transform the incoming text value into an uppercase update payload.

        :param field_id: str = Logical Pipefy field identifier
        :param field_type: str = Field type resolved by the update flow
        :param input_value: Any = Raw input value provided by the caller
        :param current_field: Field | None = Current card field value
        :param phase_field: PhaseField | None = Current phase field metadata

        :return: ResolvedFieldUpdate = Final resolved operation for the flow
        """
        if not isinstance(input_value, str):
            raise TypeError("UppercaseTextHandler requires a string input")

        normalized_value = input_value.strip().upper()
        return ResolvedFieldUpdate(
            field_id=field_id,
            field_type=field_type,
            input_value=input_value,
            current_field=current_field,
            phase_field=phase_field,
            new_value=normalized_value,
        )


def main() -> None:
    """
    Execute the custom handler example.
    """
    parser = argparse.ArgumentParser(
        description="Override a card field update handler for a single update call.",
    )
    add_connection_arguments(parser)
    parser.add_argument("--card-id", required=True, help="Card identifier.")
    parser.add_argument(
        "--field-id", required=True, help="Logical short_text field identifier."
    )
    parser.add_argument("--value", required=True, help="Input text value to transform.")
    args = parser.parse_args()

    api = build_api(token=args.token, base_url=args.base_url)

    print_section("Custom Handler Update")
    result = api.cards.updateField(
        card_id=args.card_id,
        field_id=args.field_id,
        value=args.value,
        extra_handlers={"short_text": UppercaseTextHandler()},
    )
    print(result)

    refreshed_card = api.cards.get(args.card_id)
    print(f"Stored value: {refreshed_card.requireFieldValue(args.field_id)}")


if __name__ == "__main__":
    main()
