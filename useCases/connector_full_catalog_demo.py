"""
Tenant-specific connector catalog demo.

This script is intentionally zero-argument for local exploration.
It targets the Automation Factory test pipe and prints:

- all connector fields in the pipe
- origin metadata (start form or phase)
- connector capabilities
- connected repo metadata
- dynamic options currently available for each connector

Credential resolution strategy:

1. PIPEFY_API_TOKEN environment variable
2. local encrypted secret file:
   - secret/pipefy_automation_factory.json
   - secret/secret.key
"""

from __future__ import annotations

import json
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

DEFAULT_BASE_URL = "https://app.pipefy.com/queries"
DEFAULT_PIPE_ID = "307064875"
DEFAULT_OPTIONS_LIMIT = 20


def _load_local_token() -> Optional[str]:
    """
    Try to load the local encrypted Pipefy token used in this repository.

    :return: str | None = Decrypted token when available
    """
    token = os.getenv("PIPEFY_API_TOKEN", "").strip()
    if token:
        return token

    secret_path = PROJECT_ROOT / "secret" / "pipefy_automation_factory.json"
    key_path = PROJECT_ROOT / "secret" / "secret.key"

    if not secret_path.exists() or not key_path.exists():
        return None

    try:
        from cryptography.fernet import Fernet
    except Exception:
        return None

    payload = json.loads(secret_path.read_text(encoding="utf-8"))
    encrypted_token = str(payload.get("api_token", "")).strip()
    secret_key = key_path.read_text(encoding="utf-8").strip().encode()

    if not encrypted_token:
        return None

    return Fernet(secret_key).decrypt(encrypted_token.encode()).decode()


def _build_api() -> PipeBridge:
    """
    Build the PipeBridge facade for this local demo.

    :return: PipeBridge = Initialized SDK facade
    """
    token = _load_local_token()
    if not token:
        raise RuntimeError(
            "Unable to resolve Pipefy token. Define PIPEFY_API_TOKEN or keep "
            "the local encrypted secret files under secret/."
        )

    base_url = (
        os.getenv("PIPEFY_BASE_URL", DEFAULT_BASE_URL).strip() or DEFAULT_BASE_URL
    )
    return PipeBridge(token=token, base_url=base_url)


def _print_section(title: str) -> None:
    """
    Print a formatted section title.

    :param title: str = Section title
    """
    print(f"\n=== {title} ===")


def main() -> None:
    """
    Execute the connector catalog exploration flow.
    """
    api = _build_api()
    pipe_id = os.getenv("PIPEBRIDGE_CONNECTOR_DEMO_PIPE_ID", DEFAULT_PIPE_ID)

    _print_section("Pipe")
    pipe = api.pipes.getFieldCatalog(pipe_id)
    print(f"{pipe.name} ({pipe.id})")

    connector_fields = api.connectors.listFields(pipe_id)
    if not connector_fields:
        _print_section("Connector Fields")
        print("No connector fields were found in this pipe.")
        return

    _print_section("Connector Fields")
    print(f"Total connectors: {len(connector_fields)}")

    for connector in connector_fields:
        repo = connector.connected_repo
        phase_repr = (
            f"{connector.phase_name} ({connector.phase_id})"
            if connector.phase_id
            else "-"
        )

        print(
            "\n".join(
                [
                    f"\nfield_id={connector.field_id}",
                    f"label={connector.label}",
                    f"origin={connector.origin_type}",
                    f"phase={phase_repr}",
                    f"required={connector.required}",
                    f"type={connector.type}",
                    f"uuid={connector.uuid}",
                    f"internal_id={connector.internal_id}",
                    f"can_connect_existing={connector.can_connect_existing}",
                    f"can_connect_multiples={connector.can_connect_multiples}",
                    f"can_create_new_connected={connector.can_create_new_connected}",
                    f"help_text={connector.help_text}",
                    (
                        "connected_repo="
                        f"{repo.repo_type if repo else None} | "
                        f"{repo.name if repo else None} | "
                        f"{repo.id if repo else None}"
                    ),
                ]
            )
        )

        _print_section(f"Options for {connector.field_id}")
        try:
            options = api.connectors.listOptions(
                pipe_id=pipe_id,
                field_id=connector.field_id,
                phase_id=connector.phase_id,
                limit=DEFAULT_OPTIONS_LIMIT,
            )
        except Exception as exc:
            print(f"Failed to list options: {exc}")
            continue

        if not options:
            print("No options returned.")
            continue

        print(f"Returned options: {len(options)}")
        for index, option in enumerate(options, start=1):
            lines = [
                f"[{index}] id={option.id}",
                f"    title={option.title}",
                f"    repo_type={option.repo_type}",
                f"    repo_id={option.repo_id}",
                f"    repo_name={option.repo_name}",
                f"    item_type={option.item_type}",
                f"    current_phase={option.current_phase_name} ({option.current_phase_id})",
                f"    path={option.path}",
                f"    url={option.url}",
                f"    uuid={option.uuid}",
            ]
            if option.record_fields:
                lines.append("    record_fields:")
                for field in option.record_fields:
                    lines.append(
                        "      - "
                        f"name={field.get('name')} | "
                        f"value={field.get('value')} | "
                        f"index_name={field.get('index_name')}"
                    )
            print("\n".join(lines))


if __name__ == "__main__":
    main()
