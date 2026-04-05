from pipebridge.exceptions import ValidationError, getExceptionContext
from pipebridge.service.card.flows.move.context.cardMoveContext import CardMoveContext
from pipebridge.workflow.rules.baseRule import BaseRule


class ValidateCardAllowedTransitionRule(BaseRule):
    """
    Validate whether the destination phase is an allowed transition target.

    The source of truth is the ``current_phase`` metadata already loaded in the
    card model. When the destination phase is not part of the configured move
    targets, the rule raises a validation error before any low-level mutation
    is attempted.
    """

    priority = 15

    def execute(self, context: CardMoveContext) -> None:
        """
        Validate the current-phase transition graph for the requested move.

        :param context: CardMoveContext = Shared move-flow execution context

        :return: None

        :raises ValidationError:
            When the card current phase is unavailable
        :raises ValidationError:
            When the destination phase is not configured as an allowed target
        """
        class_name, method_name = getExceptionContext(self)

        if context.card is None or context.card.current_phase is None:
            raise ValidationError(
                message="card current_phase must be available before transition validation",
                class_name=class_name,
                method_name=method_name,
            )

        source_phase = context.card.current_phase
        destination_phase_id = context.request.destination_phase_id
        if source_phase.canMoveToPhase(destination_phase_id):
            return

        allowed_transitions = [
            {
                "phase_id": phase.id,
                "phase_name": phase.name,
            }
            for phase in source_phase.iterMoveTargetPhases()
        ]

        raise ValidationError(
            message=(
                f"Card cannot be moved from phase '{source_phase.name}' "
                f"({source_phase.id}) to phase '{destination_phase_id}' because "
                "the destination is not configured as an allowed transition"
            ),
            class_name=class_name,
            method_name=method_name,
            context={
                "card_id": context.request.card_id,
                "source_phase_id": source_phase.id,
                "source_phase_name": source_phase.name,
                "destination_phase_id": destination_phase_id,
                "destination_phase_name": (
                    context.destination_phase.name
                    if context.destination_phase is not None
                    else None
                ),
                "allowed_transitions": allowed_transitions,
            },
        )
