"""
Executable example for connector discovery, option resolution, and semantic updates.
"""

from __future__ import annotations

import argparse

from useCases.common import add_connection_arguments, build_api, print_section


def main() -> None:
    """
    Inspect connector fields, list options, optionally resolve titles, and
    optionally update a card connector value.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Discover connector fields in a pipe, list dynamic options, resolve "
            "titles to ids, and optionally update a card connector semantically."
        )
    )
    add_connection_arguments(parser)
    parser.add_argument("--pipe-id", required=True, help="Pipe identifier.")
    parser.add_argument(
        "--field-id",
        help="Connector field identifier. When omitted, the example only lists connector fields.",
    )
    parser.add_argument(
        "--phase-id",
        help="Optional phase identifier to disambiguate a connector field.",
    )
    parser.add_argument(
        "--search",
        help="Optional search text used when listing connector options.",
    )
    parser.add_argument(
        "--resolve-title",
        help="Exact connector option title to resolve into a connected item id.",
    )
    parser.add_argument(
        "--card-id",
        help="Card identifier used for get/set/add/remove connector operations.",
    )
    parser.add_argument(
        "--set-item-ids",
        nargs="+",
        help="Replace connector value with these connected item ids.",
    )
    parser.add_argument(
        "--add-item-ids",
        nargs="+",
        help="Add these connected item ids to the connector value.",
    )
    parser.add_argument(
        "--remove-item-ids",
        nargs="+",
        help="Remove these connected item ids from the connector value.",
    )
    args = parser.parse_args()

    api = build_api(token=args.token, base_url=args.base_url)

    print_section("Connector Fields")
    connector_fields = api.connectors.listFields(args.pipe_id)
    for connector in connector_fields:
        repo = connector.connected_repo
        print(
            f"field_id={connector.field_id} | "
            f"label={connector.label} | "
            f"origin={connector.origin_type} | "
            f"phase={connector.phase_name} | "
            f"required={connector.required} | "
            f"repo_type={repo.repo_type if repo else None} | "
            f"repo_name={repo.name if repo else None}"
        )

    if not args.field_id:
        return

    print_section("Connector Field")
    connector = api.connectors.requireField(
        pipe_id=args.pipe_id,
        field_id=args.field_id,
        phase_id=args.phase_id,
    )
    repo = connector.connected_repo
    print(
        f"field_id={connector.field_id} | "
        f"label={connector.label} | "
        f"required={connector.required} | "
        f"can_connect_existing={connector.can_connect_existing} | "
        f"can_connect_multiples={connector.can_connect_multiples} | "
        f"repo_type={repo.repo_type if repo else None} | "
        f"repo_name={repo.name if repo else None}"
    )

    print_section("Connector Options")
    options = api.connectors.listOptions(
        pipe_id=args.pipe_id,
        field_id=args.field_id,
        phase_id=args.phase_id,
        search=args.search,
        limit=10,
    )
    for option in options:
        print(
            f"id={option.id} | "
            f"title={option.title} | "
            f"repo_type={option.repo_type} | "
            f"phase={option.current_phase_name}"
        )
        for field in option.record_fields:
            print(
                "  - "
                f"{field.get('name')} = {field.get('value')} "
                f"({field.get('index_name')})"
            )

    if args.resolve_title:
        print_section("Resolve Title")
        resolved = api.connectors.resolveOption(
            pipe_id=args.pipe_id,
            field_id=args.field_id,
            title=args.resolve_title,
            phase_id=args.phase_id,
        )
        print(f"title={resolved.title} -> id={resolved.id}")

    if args.card_id:
        print_section("Current Card Value")
        current_value = api.connectors.getCardValue(args.card_id, args.field_id)
        print(f"item_ids={current_value.item_ids}")
        if current_value.items:
            for item in current_value.items:
                print(f"- {item.id} | {item.title}")

    if args.card_id and args.set_item_ids:
        print_section("Set Card Value")
        print(
            api.connectors.setCardValue(
                card_id=args.card_id,
                field_id=args.field_id,
                item_ids=list(args.set_item_ids),
            )
        )

    if args.card_id and args.add_item_ids:
        print_section("Add Card Value")
        print(
            api.connectors.addCardValue(
                card_id=args.card_id,
                field_id=args.field_id,
                item_ids=list(args.add_item_ids),
            )
        )

    if args.card_id and args.remove_item_ids:
        print_section("Remove Card Value")
        print(
            api.connectors.removeCardValue(
                card_id=args.card_id,
                field_id=args.field_id,
                item_ids=list(args.remove_item_ids),
            )
        )


if __name__ == "__main__":
    main()
