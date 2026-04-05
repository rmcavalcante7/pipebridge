from pipebridge.service.card.flows.move.context.cardMoveContext import CardMoveContext
from pipebridge.workflow.steps.baseStep import BaseStep


class LoadDestinationPhaseStep(BaseStep):
    """
    Load destination phase schema metadata for safe phase transitions.
    """

    execution_profile = "network-read"

    def execute(self, context: CardMoveContext) -> None:
        """
        Load destination phase metadata, preferring the shared schema cache.

        The step first attempts to reuse a cached phase schema by destination
        phase identifier. If the cache misses and the card pipe is known, it
        falls back to the pipe field catalog so the flow benefits from a
        single consistent schema source.

        :param context: CardMoveContext = Shared move-flow execution context

        :return: None
        """
        if not context.config.requiresTargetPhaseSchema():
            return

        destination_phase_id = context.request.destination_phase_id
        cached_phase = context.pipe_schema_cache.getPhaseSchema(destination_phase_id)
        if cached_phase is not None:
            context.destination_phase = cached_phase
            return

        phase = context.phase_service.getPhaseModel(destination_phase_id)
        context.destination_phase = phase

        if context.pipe_id is None:
            return

        pipe_id = context.pipe_id
        pipe = context.pipe_schema_cache.getOrLoad(
            pipe_id,
            loader=lambda: context.pipe_service.getPipeFieldCatalog(pipe_id),
        )
        context.destination_phase = pipe.getPhase(destination_phase_id) or phase
