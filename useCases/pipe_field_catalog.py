"""
Usage example for inspecting a pipe field catalog.
"""

from __future__ import annotations

import argparse

from useCases.common import add_connection_arguments, build_api, print_section


def main() -> None:
    """
    Execute the pipe field catalog example.
    """
    parser = argparse.ArgumentParser(
        description="Inspect phases and fields configured in a Pipefy pipe.",
    )
    add_connection_arguments(parser)
    parser.add_argument("--pipe-id", required=True, help="Pipe identifier.")
    args = parser.parse_args()

    api = build_api(token=args.token, base_url=args.base_url)

    print_section("Pipe Field Catalog")
    pipe = api.pipes.getFieldCatalog(args.pipe_id)

    print(f"Pipe: {pipe.name} ({pipe.id})")
    for phase in pipe.iterPhases():
        print(f"\nPhase: {phase.name} ({phase.id})")
        for field in phase.iterFields():
            print(
                f"- id={field.id} | uuid={field.uuid} | label={field.label} | "
                f"type={field.type} | required={field.required} | options={field.options}"
            )


if __name__ == "__main__":
    main()
