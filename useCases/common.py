"""
Shared helpers for end-user SDK usage examples.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pipebridge import PipeBridge


def add_connection_arguments(parser: argparse.ArgumentParser) -> None:
    """
    Register common connection arguments used by all usage examples.

    :param parser: argparse.ArgumentParser = Target parser
    """
    parser.add_argument(
        "--token",
        help="Pipefy API token. Falls back to PIPEFY_API_TOKEN when omitted.",
    )
    parser.add_argument(
        "--base-url",
        default=os.getenv("PIPEFY_BASE_URL", "https://app.pipefy.com/queries"),
        help="Pipefy GraphQL endpoint. Defaults to PIPEFY_BASE_URL or the public Pipefy endpoint.",
    )


def build_api(token: Optional[str], base_url: str) -> PipeBridge:
    """
    Build the public Pipefy facade for usage examples.

    :param token: str | None = API token or ``None`` to use environment fallback
    :param base_url: str = Pipefy GraphQL endpoint

    :return: Pipefy = Initialized SDK facade

    :raises ValueError:
        When no token is available
    """
    resolved_token = token or os.getenv("PIPEFY_API_TOKEN", "").strip()
    if not resolved_token:
        raise ValueError(
            "Missing Pipefy token. Pass --token or define PIPEFY_API_TOKEN."
        )

    return PipeBridge(token=resolved_token, base_url=base_url)


def print_section(title: str) -> None:
    """
    Print a formatted section title for example output.

    :param title: str = Section title
    """
    print(f"\n=== {title} ===")
