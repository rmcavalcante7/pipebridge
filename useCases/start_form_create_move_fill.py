"""
Tenant-specific example for creating a card from start form, moving it,
and filling the next phase.
"""

from __future__ import annotations

import argparse

from pipebridge import CardMoveConfig, CardUpdateConfig
from useCases.common import add_connection_arguments, build_api, print_section


def main() -> None:
    """
    Execute a full live cycle: create, update, move, and fill.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Run a validated start-form creation flow and continue the card into the "
            "next phase. This example is tenant-specific and requires connector "
            "record IDs, not display labels."
        ),
    )
    add_connection_arguments(parser)
    parser.add_argument("--pipe-id", required=True, help="Pipe identifier.")
    parser.add_argument(
        "--project-record-id",
        required=True,
        help="Connected record id for the start-form connector field.",
    )
    parser.add_argument(
        "--requester-email",
        required=True,
        help="Requester email used in the start form.",
    )
    parser.add_argument(
        "--direct-leader-email",
        required=True,
        help="Direct leader email used in the start form.",
    )
    parser.add_argument(
        "--assessment-owner-name",
        required=True,
        help="Display name used for backlog assignee fields.",
    )
    parser.add_argument(
        "--title",
        default="PipeBridge Demo",
        help="Card title used during createSafely.",
    )
    parser.add_argument(
        "--tower",
        default="OUTRA",
        help="Option value for the tower field.",
    )
    parser.add_argument(
        "--tower-description",
        default="Automation",
        help="Free-text value for the tower description field.",
    )
    parser.add_argument(
        "--category",
        default="Cria\u00e7\u00e3o",
        help="Option value for the request category field.",
    )
    parser.add_argument(
        "--automation-name",
        default="pipebridge_demo",
        help="Automation name used in the start form.",
    )
    parser.add_argument(
        "--fte",
        default="1",
        help="Estimated FTE value.",
    )
    parser.add_argument(
        "--priority",
        default="Alta",
        help="Priority option value.",
    )
    parser.add_argument(
        "--systems",
        default="Pipefy",
        help="Systems involved value.",
    )
    parser.add_argument(
        "--description",
        default="PipeBridge demo card",
        help="Description value used in the start form.",
    )
    parser.add_argument(
        "--destination-phase-id",
        default="342616259",
        help="Destination phase id for the safe move.",
    )
    parser.add_argument(
        "--fill-text",
        default="Teste pipefy",
        help="Text used for long-text fields in the target phase.",
    )
    parser.add_argument(
        "--complexity",
        default="baixa",
        help="Complexity option used in the target phase.",
    )
    parser.add_argument(
        "--fill-number",
        default="1",
        help="Numeric value used for number fields in the target phase.",
    )
    args = parser.parse_args()

    api = build_api(token=args.token, base_url=args.base_url)

    create_fields = {
        "nome_projetos": [args.project_record_id],
        "torre": args.tower,
        "descreva_a_torre": args.tower_description,
        "email_do_solicitante": args.requester_email,
        "l_der_direto": args.direct_leader_email,
        "qual_a_categoria_desta_solicitacao": args.category,
        "nome_da_automa_o": args.automation_name,
        "respons_vel_pelo_assessment_1": args.requester_email,
        "fte": args.fte,
        "n_vel_de_prioridade": args.priority,
        "mais_informa_es": args.systems,
        "copy_of_descri_o": args.description,
    }

    print_section("Create Safely")
    create_result = api.cards.createSafely(
        pipe_id=args.pipe_id,
        title=args.title,
        fields=create_fields,
    )
    card_id = create_result["data"]["createCard"]["card"]["id"]
    print(f"Created card: {card_id}")

    created_card = api.cards.get(card_id)
    current_phase = created_card.current_phase
    if current_phase is None:
        raise RuntimeError("Created card has no current phase.")

    print_section("Fill Current Phase")
    backlog_update_fields = {
        "assessment_realizado": "Sim",
        "respons_vel_pelo_assessment": [args.assessment_owner_name],
        "desenvolvedor": [args.assessment_owner_name],
    }
    api.cards.updateFields(
        card_id=card_id,
        fields=backlog_update_fields,
        expected_phase_id=current_phase.id,
        config=CardUpdateConfig(
            validate_field_existence=True,
            validate_field_options=True,
            validate_field_type=True,
            validate_field_format=True,
        ),
    )
    print(f"Filled phase: {current_phase.name} ({current_phase.id})")

    print_section("Move Safely")
    move_result = api.cards.moveSafely(
        card_id=card_id,
        destination_phase_id=args.destination_phase_id,
        expected_current_phase_id=current_phase.id,
        config=CardMoveConfig(validate_required_fields=True),
    )
    print(move_result)

    moved_card = api.cards.get(card_id)
    moved_phase = moved_card.current_phase
    if moved_phase is None:
        raise RuntimeError("Moved card has no current phase.")

    print_section("Fill Destination Phase")
    destination_update_fields = {
        "resumo_do_assessment": args.fill_text,
        "complexidade": args.complexity,
        "sistemas_envolvidos": args.fill_text,
        "tempo_de_desenvolvimento_para_cada_m_dulo": args.fill_text,
        "tempo_de_desenvolvimento_total": args.fill_number,
        "tempo_de_desenvolvimento_usando_vibe_coding": args.fill_number,
    }
    update_result = api.cards.updateFields(
        card_id=card_id,
        fields=destination_update_fields,
        expected_phase_id=moved_phase.id,
        config=CardUpdateConfig(
            validate_field_existence=True,
            validate_field_options=True,
            validate_field_type=True,
            validate_field_format=True,
        ),
    )
    print(update_result)

    print_section("Final State")
    final_card = api.cards.get(card_id)
    print(f"Card: {final_card.title} ({final_card.id})")
    print(
        f"Current phase: {final_card.current_phase.name} ({final_card.current_phase.id})"
    )


if __name__ == "__main__":
    main()
