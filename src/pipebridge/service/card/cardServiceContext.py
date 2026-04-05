from __future__ import annotations

from pipebridge.client.httpClient import PipefyHttpClient
from pipebridge.exceptions import ValidationError, getExceptionContext
from pipebridge.service.phase.phaseService import PhaseService
from pipebridge.service.pipe.cache.pipeSchemaCache import PipeSchemaCache
from pipebridge.service.pipe.pipeService import PipeService
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pipebridge.service.card.cardService import CardService


class CardServiceContext:
    """
    Shared dependency container for card workflows.
    """

    def __init__(
        self,
        client: PipefyHttpClient,
        card_service: CardService,
        phase_service: PhaseService,
        pipe_service: PipeService,
        pipe_schema_cache: PipeSchemaCache,
    ) -> None:
        """
        Initialize the shared card workflow dependency container.

        :param client: PipefyHttpClient = HTTP client
        :param card_service: CardService = Card domain service
        :param phase_service: PhaseService = Phase domain service
        :param pipe_service: PipeService = Pipe domain service
        :param pipe_schema_cache: PipeSchemaCache = Cached pipe schema provider

        :raises ValidationError:
            When any dependency is ``None``
        """
        class_name, method_name = getExceptionContext(self)
        if client is None:
            raise ValidationError("client must not be None", class_name, method_name)
        if card_service is None:
            raise ValidationError(
                "card_service must not be None", class_name, method_name
            )
        if phase_service is None:
            raise ValidationError(
                "phase_service must not be None", class_name, method_name
            )
        if pipe_service is None:
            raise ValidationError(
                "pipe_service must not be None", class_name, method_name
            )
        if pipe_schema_cache is None:
            raise ValidationError(
                "pipe_schema_cache must not be None", class_name, method_name
            )

        self.client = client
        self.card_service = card_service
        self.phase_service = phase_service
        self.pipe_service = pipe_service
        self.pipe_schema_cache = pipe_schema_cache
