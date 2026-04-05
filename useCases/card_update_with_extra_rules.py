"""
Usage example for card updates with custom validation rules.
"""

from __future__ import annotations

import argparse

from pipebridge import CardUpdateConfig
from pipebridge.exceptions import ValidationError
from pipebridge.service.card.flows.update.rules.regexFieldPatternRule import (
    RegexFieldPatternRule,
)
from pipebridge.workflow.rules.baseRule import BaseRule
from useCases.common import add_connection_arguments, build_api, print_section


class UppercaseOnlyRule(BaseRule):
    """
    Example custom rule that requires a field value to be uppercase.
    """

    def __init__(self, field_id: str) -> None:
        """
        Initialize the custom uppercase-only rule.

        :param field_id: str = Logical field identifier to validate
        """
        self.field_id = field_id

    def execute(self, context) -> None:
        """
        Validate that the configured field value is fully uppercase.

        :param context: CardUpdateContext = Shared update context

        :raises ValidationError:
            When the field value is not uppercase
        """
        if self.field_id not in context.request.fields:
            return

        value = context.request.fields[self.field_id]
        if not isinstance(value, str) or value != value.upper():
            raise ValidationError(
                message=(
                    f"Field '{self.field_id}' must be uppercase. "
                    f"Received value: '{value}'"
                ),
                class_name=self.__class__.__name__,
                method_name="execute",
            )


def main() -> None:
    """
    Execute the custom card update rules example.
    """
    parser = argparse.ArgumentParser(
        description="Update a card field using extra validation rules provided by the caller.",
    )
    add_connection_arguments(parser)
    parser.add_argument("--card-id", required=True, help="Card identifier.")
    parser.add_argument("--field-id", required=True, help="Logical field identifier.")
    parser.add_argument(
        "--value", required=True, help="Value to be written to the field."
    )
    parser.add_argument(
        "--pattern",
        default=r"^[A-Z0-9_\- ]+$",
        help="Regex pattern used by RegexFieldPatternRule.",
    )
    args = parser.parse_args()

    api = build_api(token=args.token, base_url=args.base_url)

    print_section("Card Update With Extra Rules")
    result = api.cards.updateField(
        card_id=args.card_id,
        field_id=args.field_id,
        value=args.value,
        config=CardUpdateConfig(validate_field_format=True),
        extra_rules=[
            RegexFieldPatternRule({args.field_id: args.pattern}),
            UppercaseOnlyRule(args.field_id),
        ],
    )

    print(result)


if __name__ == "__main__":
    main()
