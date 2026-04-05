"""
Usage example for cascading pipe inspection through phases, fields, and cards.
"""

from __future__ import annotations

import argparse

from useCases.common import add_connection_arguments, build_api, print_section


def main() -> None:
    """
    Execute the cascading pipe inspection example.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Inspect a Pipefy pipe in cascade order: pipe -> phases -> fields -> cards."
        ),
    )
    add_connection_arguments(parser)
    parser.add_argument("--pipe-id", required=True, help="Pipe identifier.")
    parser.add_argument(
        "--max-cards-per-phase",
        type=int,
        default=5,
        help="Maximum number of cards to print per phase.",
    )
    args = parser.parse_args()

    api = build_api(token=args.token, base_url=args.base_url)

    print_section("Load Pipe")
    pipe = api.pipes.get(args.pipe_id)
    print(f"Pipe: {pipe.name} ({pipe.id})")
    print(f"Organization ID: {pipe.organization_id}")
    print(f"Cards count: {pipe.cards_count}")
    print(f"Phases count: {len(pipe.iterPhases())}")
    print(f"Labels count: {len(pipe.iterLabels())}")
    print(f"Users count: {len(pipe.iterUsers())}")

    for phase_summary in pipe.iterPhases():
        print_section(f"Phase Summary - {phase_summary.name} ({phase_summary.id})")

        phase = api.phases.get(phase_summary.id)
        print(f"Fields count: {len(phase.iterFields())}")
        print(
            f"Allowed move targets: {[(p.id, p.name) for p in phase.iterMoveTargetPhases()]}"
        )

        print("\nFields:")
        for field in phase.iterFields():
            print(
                f"- id={field.id} | "
                f"uuid={field.uuid} | "
                f"label={field.label} | "
                f"type={field.type} | "
                f"required={field.required} | "
                f"options={field.options}"
            )

        cards = api.phases.listCards(phase.id)
        print(f"\nCards in phase: {len(cards)}")

        if not cards:
            continue

        print("\nCard details:")
        for card in cards[: args.max_cards_per_phase]:
            current_phase = card.current_phase
            print(
                f"- card_id={card.id} | "
                f"title={card.title} | "
                f"pipe_id={card.pipe_id} | "
                f"current_phase={current_phase.name if current_phase else None}"
            )

            for card_field in card.iterFields():
                print(
                    f"field_id={card_field.id} | "
                    f"label={card_field.label} | "
                    f"type={card_field.type} | "
                    f"value={card_field.value}"
                )


if __name__ == "__main__":
    main()
