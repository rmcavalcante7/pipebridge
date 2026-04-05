"""
Usage example for safe card phase transition.
"""

from __future__ import annotations

import argparse

from pipebridge import CardMoveConfig
from pipebridge.exceptions import RequiredFieldError, ValidationError
from useCases.common import add_connection_arguments, build_api, print_section


def main() -> None:
    """
    Execute the safe card move example.
    """
    parser = argparse.ArgumentParser(
        description="Safely move a card to another phase after validating transition rules.",
    )
    add_connection_arguments(parser)
    parser.add_argument("--card-id", required=True, help="Card identifier.")
    parser.add_argument(
        "--destination-phase-id",
        required=True,
        help="Destination phase identifier.",
    )
    parser.add_argument(
        "--expected-current-phase-id",
        help="Optional expected current phase identifier.",
    )
    args = parser.parse_args()

    api = build_api(token=args.token, base_url=args.base_url)

    print_section("Safe Move")
    try:
        result = api.cards.moveSafely(
            card_id=args.card_id,
            destination_phase_id=args.destination_phase_id,
            expected_current_phase_id=args.expected_current_phase_id,
            config=CardMoveConfig(validate_required_fields=True),
        )
        print("Move executed successfully.")
        print(result)
    except RequiredFieldError as exc:
        print("Move blocked because required fields are still pending.")
        print(f"Destination phase: {exc.context.get('destination_phase_name')}")
        for field_info in exc.context.get("pending_required_fields", []):
            print(
                f"- {field_info.get('field_id')} | "
                f"label={field_info.get('field_label')} | "
                f"type={field_info.get('field_type')}"
            )
    except ValidationError as exc:
        print("Move blocked because the transition is not allowed.")
        print(f"Destination phase: {exc.context.get('destination_phase_name')}")
        print(f"Allowed transitions: {exc.context.get('allowed_transitions')}")


if __name__ == "__main__":
    main()
