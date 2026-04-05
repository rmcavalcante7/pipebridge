from pipebridge.exceptions import ValidationError, getExceptionContext
from pipebridge.models.phase import Phase
from pipebridge.service.card.flows.update.context.cardUpdateContext import (
    CardUpdateContext,
)
from pipebridge.workflow.steps.baseStep import BaseStep


class LoadPhaseSchemaStep(BaseStep):
    """
    Load phase schema metadata when optional validations require it.
    """

    execution_profile = "network-read"

    def execute(self, context: CardUpdateContext) -> None:
        """
        Load current phase schema metadata, preferring the shared cache.

        :param context: CardUpdateContext = Shared update-flow execution context

        :return: None

        :raises ValidationError:
            When card current phase is unavailable before schema loading
        """
        if not context.config.requiresPhaseSchema():
            return

        class_name, method_name = getExceptionContext(self)

        if context.card is None or context.card.current_phase is None:
            raise ValidationError(
                message="card current_phase must be available before phase loading",
                class_name=class_name,
                method_name=method_name,
            )

        current_phase_id = context.card.current_phase.id

        cached_phase = context.pipe_schema_cache.getPhaseSchema(current_phase_id)
        if cached_phase is not None:
            context.phase = cached_phase
            return

        phase = context.phase_service.getPhaseModel(current_phase_id)
        context.phase = phase

        if context.pipe_id is None:
            return

        pipe_id = context.pipe_id
        pipe = context.pipe_schema_cache.getOrLoad(
            pipe_id,
            loader=lambda: context.pipe_service.getPipeFieldCatalog(pipe_id),
        )
        context.phase = pipe.getPhase(current_phase_id) or phase
