"""
Execution context for card move flows.
"""

from typing import TYPE_CHECKING, Any, Dict, Optional

from pipebridge.client.httpClient import PipefyHttpClient
from pipebridge.models.card import Card
from pipebridge.models.phase import Phase
from pipebridge.service.card.flows.move.cardMoveConfig import CardMoveConfig
from pipebridge.service.card.flows.move.cardMoveRequest import CardMoveRequest
from pipebridge.workflow.context.executionContext import ExecutionContext

if TYPE_CHECKING:
    from pipebridge.service.card.cardService import CardService
    from pipebridge.service.phase.phaseService import PhaseService
    from pipebridge.service.pipe.cache.pipeSchemaCache import PipeSchemaCache
    from pipebridge.service.pipe.pipeService import PipeService


class CardMoveContext(ExecutionContext):
    """
    Strongly typed mutable context shared across card move flow execution.

    This context centralizes both immutable dependencies and mutable runtime
    state used by the safe phase transition workflow. It keeps the flow steps
    simple and explicit while preserving type-aware access to loaded models,
    cache instances, and validation artifacts.
    """

    def __init__(
        self,
        request: CardMoveRequest,
        client: PipefyHttpClient,
        card_service: "CardService",
        phase_service: "PhaseService",
        pipe_service: "PipeService",
        pipe_schema_cache: "PipeSchemaCache",
        config: CardMoveConfig,
    ) -> None:
        """
        Initialize card move execution context.

        :param request: CardMoveRequest = Structured move request
        :param client: PipefyHttpClient = HTTP client used by the flow
        :param card_service: CardService = Card domain service
        :param phase_service: PhaseService = Phase domain service
        :param pipe_service: PipeService = Pipe domain service
        :param pipe_schema_cache: PipeSchemaCache = Shared schema cache
        :param config: CardMoveConfig = Move flow configuration

        :return: None
        """
        super().__init__(metadata={"flow": "card_move"})
        self.request = request
        self.client = client
        self.card_service = card_service
        self.phase_service = phase_service
        self.pipe_service = pipe_service
        self.pipe_schema_cache = pipe_schema_cache
        self.config = config
        self.pipe_id: Optional[str] = None
        self.card: Optional[Card] = None
        self.destination_phase: Optional[Phase] = None
        self.response: Dict[str, Any] = {}
        self.pending_required_fields: list[dict[str, Any]] = []
