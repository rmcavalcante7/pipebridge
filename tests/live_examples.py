"""
Shared helpers for destructive live integration tests.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

from pipebridge import CardMoveConfig, CardUpdateConfig, PipefyHttpClient
from pipebridge.exceptions import RequiredFieldError, ValidationError

DEFAULT_LIVE_PIPE_ID = "307064875"
DEFAULT_LIVE_TITLE = "PipeBridge Live Test"
DEFAULT_TEXT_VALUE = "Teste pipefy"
DEFAULT_EMAIL_VALUE = "teste.pipefy@example.com"
DEFAULT_NUMBER_VALUE = "1"
DEFAULT_DATE_VALUE = "2026-01-01"
DEFAULT_DATETIME_VALUE = "2026-01-01T12:12:00+00:00"
DEFAULT_TIME_VALUE = "12:12"
DEFAULT_CREATE_DESCRIPTION_VALUE = "Teste pipefy de cria\u00e7\u00e3o de card"


@dataclass
class ConnectedRepoInfo:
    """
    Metadata required to resolve connector values.
    """

    repo_type: str
    repo_id: str
    repo_name: str | None = None


@dataclass
class LiveCardLifecycleContext:
    """
    Shared result of the destructive live card lifecycle.
    """

    pipe_id: str
    reference_card_id: str | None
    created_card_id: str
    created_title: str
    create_fields: dict[str, Any]
    created_phase_id: str
    created_phase_name: str
    invalid_destination_phase_id: str | None
    invalid_transition_context: dict[str, Any] | None
    pending_required_destination_phase_id: str | None
    pending_required_context: dict[str, Any] | None
    current_phase_update_fields: dict[str, Any]
    move_destination_phase_id: str | None
    move_destination_phase_name: str | None
    destination_phase_update_fields: dict[str, Any]


def build_live_card_lifecycle_context(
    api: Any,
    client: PipefyHttpClient,
    pipe_id: str,
    reference_card_id: str | None = None,
) -> LiveCardLifecycleContext:
    """
    Create a card and exercise the full live lifecycle on that same card only.
    """
    pipe = api.pipes.getFieldCatalog(pipe_id)
    reference_card = api.cards.get(reference_card_id) if reference_card_id else None
    connected_repos = _load_start_form_connected_repos(api, pipe_id)
    assignee_name = _resolve_assignee_name(pipe, reference_card)

    create_title = (
        reference_card.title
        if reference_card and reference_card.title
        else DEFAULT_LIVE_TITLE
    )
    create_fields = _build_start_form_fields(
        api=api,
        client=client,
        pipe=pipe,
        connected_repos=connected_repos,
        reference_card=reference_card,
        assignee_name=assignee_name,
    )
    create_fields["copy_of_descri_o"] = DEFAULT_CREATE_DESCRIPTION_VALUE

    create_result = api.cards.createSafely(
        pipe_id=pipe_id,
        title=create_title,
        fields=create_fields,
    )
    created_card_id = create_result["data"]["createCard"]["card"]["id"]
    created_card = api.cards.get(created_card_id)

    if created_card.current_phase is None:
        raise RuntimeError("Created test card has no current phase.")

    created_phase_id = created_card.current_phase.id
    created_phase_name = created_card.current_phase.name

    all_pipe_phase_ids = [phase.id for phase in pipe.iterPhases()]
    allowed_transitions = _load_allowed_transitions(api, created_phase_id)
    allowed_transition_ids = {item["phase_id"] for item in allowed_transitions}

    invalid_destination_phase_id = next(
        (
            phase_id
            for phase_id in all_pipe_phase_ids
            if phase_id not in allowed_transition_ids and phase_id != created_phase_id
        ),
        None,
    )

    invalid_transition_context: dict[str, Any] | None = None
    if invalid_destination_phase_id is not None:
        try:
            api.cards.moveSafely(
                card_id=created_card_id,
                destination_phase_id=invalid_destination_phase_id,
                expected_current_phase_id=created_phase_id,
                config=CardMoveConfig(validate_required_fields=True),
            )
        except ValidationError as exc:
            invalid_transition_context = exc.context
        else:
            raise AssertionError("Invalid transition unexpectedly succeeded.")

    pending_required_destination_phase_id: str | None = None
    pending_required_context: dict[str, Any] | None = None
    move_destination_phase_id: str | None = None
    move_destination_phase_name: str | None = None

    for candidate in allowed_transitions:
        phase = api.phases.get(candidate["phase_id"])
        required_fields = [field for field in phase.iterFields() if field.required]
        if required_fields and pending_required_destination_phase_id is None:
            pending_required_destination_phase_id = phase.id
            try:
                api.cards.moveSafely(
                    card_id=created_card_id,
                    destination_phase_id=phase.id,
                    expected_current_phase_id=created_phase_id,
                    config=CardMoveConfig(validate_required_fields=True),
                )
            except RequiredFieldError as exc:
                pending_required_context = exc.context
            else:
                raise AssertionError(
                    "Move with pending required fields unexpectedly succeeded."
                )

        if not required_fields and move_destination_phase_id is None:
            move_destination_phase_id = phase.id
            move_destination_phase_name = phase.name

    current_phase = api.phases.get(created_phase_id)
    current_phase_update_fields = _build_phase_update_fields(
        api=api,
        client=client,
        pipe=pipe,
        phase=current_phase,
        reference_card=reference_card,
        assignee_name=assignee_name,
    )
    if current_phase_update_fields:
        api.cards.updateFields(
            card_id=created_card_id,
            fields=current_phase_update_fields,
            expected_phase_id=created_phase_id,
            config=CardUpdateConfig(
                validate_field_existence=True,
                validate_field_options=True,
                validate_field_type=True,
                validate_field_format=True,
            ),
        )

    destination_phase_update_fields: dict[str, Any] = {}
    if move_destination_phase_id is not None:
        api.cards.moveSafely(
            card_id=created_card_id,
            destination_phase_id=move_destination_phase_id,
            expected_current_phase_id=created_phase_id,
            config=CardMoveConfig(validate_required_fields=True),
        )

        moved_phase = api.phases.get(move_destination_phase_id)
        destination_phase_update_fields = _build_phase_update_fields(
            api=api,
            client=client,
            pipe=pipe,
            phase=moved_phase,
            reference_card=reference_card,
            assignee_name=assignee_name,
        )
        if destination_phase_update_fields:
            api.cards.updateFields(
                card_id=created_card_id,
                fields=destination_phase_update_fields,
                expected_phase_id=move_destination_phase_id,
                config=CardUpdateConfig(
                    validate_field_existence=True,
                    validate_field_options=True,
                    validate_field_type=True,
                    validate_field_format=True,
                ),
            )

    return LiveCardLifecycleContext(
        pipe_id=pipe_id,
        reference_card_id=reference_card_id,
        created_card_id=created_card_id,
        created_title=create_title,
        create_fields=create_fields,
        created_phase_id=created_phase_id,
        created_phase_name=created_phase_name,
        invalid_destination_phase_id=invalid_destination_phase_id,
        invalid_transition_context=invalid_transition_context,
        pending_required_destination_phase_id=pending_required_destination_phase_id,
        pending_required_context=pending_required_context,
        current_phase_update_fields=current_phase_update_fields,
        move_destination_phase_id=move_destination_phase_id,
        move_destination_phase_name=move_destination_phase_name,
        destination_phase_update_fields=destination_phase_update_fields,
    )


def should_delete_created_live_card() -> bool:
    """
    Decide whether the created live card should be deleted after the session.
    """
    return os.getenv("PIPEBRIDGE_DELETE_CREATED_TEST_CARD", "1") != "0"


def normalize_live_field_value(value: Any) -> Any:
    """
    Normalize live field values so assertions can compare API payloads safely.
    """
    return _normalize_reference_value(value)


def _load_start_form_connected_repos(
    api: Any, pipe_id: str
) -> dict[str, ConnectedRepoInfo]:
    query_body = """
        id
        start_form_fields {
            id
            type
            connected_repo {
                __typename
                ... on Pipe { id name }
                ... on Table { id name }
            }
        }
    """
    raw = api.pipes.raw.get(pipe_id, query_body)
    field_entries = raw.get("data", {}).get("pipe", {}).get("start_form_fields", [])
    result: dict[str, ConnectedRepoInfo] = {}

    for entry in field_entries:
        field_id = entry.get("id")
        repo = entry.get("connected_repo")
        if field_id and isinstance(repo, dict) and repo.get("id"):
            result[field_id] = ConnectedRepoInfo(
                repo_type=str(repo.get("__typename")),
                repo_id=str(repo.get("id")),
                repo_name=repo.get("name"),
            )

    return result


def _load_allowed_transitions(api: Any, phase_id: str) -> list[dict[str, str]]:
    query_body = """
        id
        name
        cards_can_be_moved_to_phases {
            id
            name
        }
    """
    raw = api.phases.raw.get(phase_id, query_body)
    phases = (
        raw.get("data", {}).get("phase", {}).get("cards_can_be_moved_to_phases", [])
    )
    return [
        {"phase_id": str(phase.get("id")), "phase_name": str(phase.get("name"))}
        for phase in phases
        if phase.get("id")
    ]


def _resolve_assignee_name(pipe: Any, reference_card: Any | None) -> str:
    if reference_card is not None:
        for field_id in (
            "respons_vel_pelo_assessment",
            "desenvolvedor",
            "l_der_de_squad",
        ):
            reference_value = _normalize_reference_value(
                reference_card.getFieldValue(field_id)
            )
            if isinstance(reference_value, list) and reference_value:
                return str(reference_value[0])
            if isinstance(reference_value, str) and reference_value:
                return reference_value

    users = pipe.iterUsers()
    if users:
        user_name = getattr(users[0], "name", None)
        if user_name:
            return str(user_name)

    fallback = os.getenv("PIPEBRIDGE_ASSIGNEE_NAME")
    if fallback:
        return fallback

    raise RuntimeError(
        "Unable to resolve an assignee name for destructive live tests. "
        "Set PIPEBRIDGE_ASSIGNEE_NAME or provide a suitable reference card."
    )


def _build_start_form_fields(
    api: Any,
    client: PipefyHttpClient,
    pipe: Any,
    connected_repos: dict[str, ConnectedRepoInfo],
    reference_card: Any | None,
    assignee_name: str,
) -> dict[str, Any]:
    fields: dict[str, Any] = {}

    for field in pipe.iterStartFormFields():
        reference_value = None
        if reference_card is not None and reference_card.hasField(field.id):
            reference_value = reference_card.getFieldValue(field.id)

        value = _resolve_field_value(
            api=api,
            client=client,
            pipe=pipe,
            field=field,
            reference_value=reference_value,
            assignee_name=assignee_name,
            connected_repo=connected_repos.get(field.id),
        )

        if value is None and field.required:
            raise RuntimeError(
                f"Unable to generate a valid start form value for required field '{field.id}'."
            )
        if value is not None:
            fields[field.id] = value

    return fields


def _build_phase_update_fields(
    api: Any,
    client: PipefyHttpClient,
    pipe: Any,
    phase: Any,
    reference_card: Any | None,
    assignee_name: str,
) -> dict[str, Any]:
    fields: dict[str, Any] = {}

    for field in phase.iterFields():
        reference_value = None
        if reference_card is not None and reference_card.hasField(field.id):
            reference_value = reference_card.getFieldValue(field.id)

        value = _resolve_field_value(
            api=api,
            client=client,
            pipe=pipe,
            field=field,
            reference_value=reference_value,
            assignee_name=assignee_name,
            connected_repo=None,
        )
        if value is None:
            continue
        fields[field.id] = value

    return fields


def _resolve_field_value(
    api: Any,
    client: PipefyHttpClient,
    pipe: Any,
    field: Any,
    reference_value: Any,
    assignee_name: str,
    connected_repo: ConnectedRepoInfo | None,
) -> Any | None:
    field_type = str(field.type or "")
    normalized_reference = _normalize_reference_value(reference_value)

    if field_type in {"short_text", "long_text"}:
        return _coerce_text_value(normalized_reference)
    if field_type == "email":
        return _coerce_email_value(normalized_reference)
    if field_type in {"select", "label_select", "radio_horizontal", "radio_vertical"}:
        options = list(field.options or [])
        if isinstance(normalized_reference, str) and normalized_reference in options:
            return normalized_reference
        return options[0] if options else None
    if field_type in {"checklist_horizontal", "checklist_vertical"}:
        options = list(field.options or [])
        if isinstance(normalized_reference, list):
            valid = [item for item in normalized_reference if item in options]
            if valid:
                return valid
        return options[: min(2, len(options))] if options else None
    if field_type in {"number", "currency"}:
        return _coerce_numeric_value(normalized_reference)
    if field_type == "date":
        return DEFAULT_DATE_VALUE
    if field_type in {"datetime", "due_date"}:
        return DEFAULT_DATETIME_VALUE
    if field_type == "time":
        return DEFAULT_TIME_VALUE
    if field_type in {"assignee", "assignee_select"}:
        if isinstance(normalized_reference, list) and normalized_reference:
            return [str(normalized_reference[0])]
        if isinstance(normalized_reference, str) and normalized_reference:
            return [normalized_reference]
        return [assignee_name]
    if field_type == "connector":
        return _resolve_connector_value(
            api=api,
            client=client,
            connected_repo=connected_repo,
            reference_value=normalized_reference,
        )
    if field_type == "attachment":
        return None

    return None


def _resolve_connector_value(
    api: Any,
    client: PipefyHttpClient,
    connected_repo: ConnectedRepoInfo | None,
    reference_value: Any,
) -> list[str] | None:
    if connected_repo is None:
        return None

    desired_titles: list[str] = []
    if isinstance(reference_value, list):
        desired_titles = [str(item) for item in reference_value if item]
    elif isinstance(reference_value, str) and reference_value:
        desired_titles = [reference_value]

    if connected_repo.repo_type == "Pipe":
        cards = api.cards.list(connected_repo.repo_id)
        candidates = [
            {"id": str(card.id), "title": str(card.title)}
            for card in cards
            if getattr(card, "id", None)
        ]
    elif connected_repo.repo_type == "Table":
        query = f"""
        query {{
          table_records(table_id: "{connected_repo.repo_id}") {{
            edges {{
              node {{
                id
                title
              }}
            }}
          }}
        }}
        """
        raw = client.sendRequest(query)
        candidates = [
            {
                "id": str(edge.get("node", {}).get("id")),
                "title": str(edge.get("node", {}).get("title")),
            }
            for edge in raw.get("data", {}).get("table_records", {}).get("edges", [])
            if edge.get("node", {}).get("id")
        ]
    else:
        return None

    for desired in desired_titles:
        for candidate in candidates:
            if candidate["title"] == desired:
                return [candidate["id"]]

    if candidates:
        return [candidates[0]["id"]]

    return None


def _normalize_reference_value(value: Any) -> Any:
    if not isinstance(value, str):
        return value

    stripped = value.strip()
    if not stripped:
        return stripped

    try:
        parsed = json.loads(stripped)
    except Exception:
        return stripped

    return parsed


def _coerce_text_value(reference_value: Any) -> str:
    if isinstance(reference_value, str) and reference_value.strip():
        return reference_value
    return DEFAULT_TEXT_VALUE


def _coerce_email_value(reference_value: Any) -> str:
    if isinstance(reference_value, str) and "@" in reference_value:
        return reference_value
    return DEFAULT_EMAIL_VALUE


def _coerce_numeric_value(reference_value: Any) -> str:
    if reference_value is None:
        return DEFAULT_NUMBER_VALUE

    if isinstance(reference_value, (int, float)):
        return str(reference_value)

    if isinstance(reference_value, str):
        normalized = (
            reference_value.replace("R$", "")
            .replace("$", "")
            .replace(".", "")
            .replace(",", ".")
            .strip()
        )
        try:
            float(normalized)
            return normalized
        except Exception:
            return DEFAULT_NUMBER_VALUE

    return DEFAULT_NUMBER_VALUE
