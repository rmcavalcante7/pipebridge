from pipebridge.exceptions import (
    RequiredFieldError,
    ValidationError,
    getExceptionContext,
)
from pipebridge.service.card.flows.move.context.cardMoveContext import CardMoveContext
from pipebridge.workflow.rules.baseRule import BaseRule


class ValidateCardRequiredFieldsForPhaseRule(BaseRule):
    """
    Validate whether the card can enter the destination phase.

    The rule checks all destination phase fields marked as required and raises
    a semantic exception when one or more of them is still empty in the card.
    """

    priority = 20

    def execute(self, context: CardMoveContext) -> None:
        """
        Validate pending required fields for the destination phase.

        :param context: CardMoveContext = Shared move-flow execution context

        :return: None

        :raises ValidationError:
            When card or destination phase metadata is unavailable
        :raises RequiredFieldError:
            When one or more required destination fields are still empty
        """
        if not context.config.validate_required_fields:
            return

        class_name, method_name = getExceptionContext(self)

        if context.card is None:
            raise ValidationError(
                message="card must be loaded before required-field validation",
                class_name=class_name,
                method_name=method_name,
            )

        if context.destination_phase is None:
            raise ValidationError(
                message="destination_phase must be loaded before required-field validation",
                class_name=class_name,
                method_name=method_name,
            )

        pending_fields: list[dict[str, str]] = []
        for phase_field in context.destination_phase.iterFields():
            if not phase_field.required:
                continue

            if context.card.isFieldFilled(phase_field.id):
                continue

            pending_fields.append(
                {
                    "field_id": phase_field.id,
                    "field_label": phase_field.label or phase_field.id,
                    "field_type": phase_field.type or "",
                }
            )

        context.pending_required_fields = pending_fields

        if pending_fields:
            raise RequiredFieldError(
                message=(
                    "Card cannot be moved because required fields from the "
                    "destination phase are still empty"
                ),
                class_name=class_name,
                method_name=method_name,
                context={
                    "card_id": context.request.card_id,
                    "destination_phase_id": context.request.destination_phase_id,
                    "destination_phase_name": context.destination_phase.name,
                    "pending_required_fields": pending_fields,
                },
            )
