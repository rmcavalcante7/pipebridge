"""
Execution context for card update flows.
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from pipebridge.client.httpClient import PipefyHttpClient
from pipebridge.models.card import Card
from pipebridge.models.phase import Phase
from pipebridge.service.card.flows.update.cardUpdateConfig import CardUpdateConfig
from pipebridge.service.card.flows.update.cardUpdateRequest import CardUpdateRequest
from pipebridge.workflow.context.executionContext import ExecutionContext

if TYPE_CHECKING:
    from pipebridge.service.card.cardService import CardService
    from pipebridge.service.phase.phaseService import PhaseService
    from pipebridge.service.pipe.cache.pipeSchemaCache import PipeSchemaCache
    from pipebridge.service.pipe.pipeService import PipeService


class CardUpdateContext(ExecutionContext):
    """
    Strongly typed mutable context shared across card update flow execution.

    The context stores loaded domain models, shared services, cache access and
    mutable workflow artifacts produced while resolving and applying field
    updates.
    """

    def __init__(
        self,
        request: CardUpdateRequest,
        client: PipefyHttpClient,
        card_service: "CardService",
        phase_service: "PhaseService",
        pipe_service: "PipeService",
        pipe_schema_cache: "PipeSchemaCache",
        config: CardUpdateConfig,
    ) -> None:
        """
        Initialize card update execution context.

        :param request: CardUpdateRequest = Structured update request
        :param client: PipefyHttpClient = HTTP client used by the flow
        :param card_service: CardService = Card domain service
        :param phase_service: PhaseService = Phase domain service
        :param pipe_service: PipeService = Pipe domain service
        :param pipe_schema_cache: PipeSchemaCache = Shared schema cache
        :param config: CardUpdateConfig = Update flow configuration
        """
        super().__init__(metadata={"flow": "card_update"})
        self.request = request
        self.client = client
        self.card_service = card_service
        self.phase_service = phase_service
        self.pipe_service = pipe_service
        self.pipe_schema_cache = pipe_schema_cache
        self.config = config
        self.pipe_id: Optional[str] = None
        self.card: Optional[Card] = None
        self.phase: Optional[Phase] = None
        self.resolved_operations: List[Any] = []
        self.responses: Dict[str, Any] = {}
