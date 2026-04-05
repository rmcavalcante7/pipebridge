from __future__ import annotations

# ============================================================
# Dependencies
# ============================================================
from pathlib import Path
from typing import Any, Dict, Optional, List, Sequence

from pipebridge.client.httpClient import PipefyHttpClient
from pipebridge.exceptions import getExceptionContext
from pipebridge.models.file.fileUploadRequest import FileUploadRequest
from pipebridge.models.pipe import Pipe
from pipebridge.service.card.cardService import CardService
from pipebridge.service.card.flows.update.cardUpdateConfig import CardUpdateConfig
from pipebridge.service.card.flows.update.dispatcher.baseCardFieldUpdateHandler import (
    BaseCardFieldUpdateHandler,
)
from pipebridge.service.card.flows.move.cardMoveConfig import CardMoveConfig
from pipebridge.service.file.flows.upload.config.uploadConfig import UploadConfig
from pipebridge.workflow.rules.baseRule import BaseRule
from pipebridge.workflow.steps.baseStep import BaseStep
from pipebridge.service.pipe.pipeService import PipeService
from pipebridge.service.phase.phaseService import PhaseService
from pipebridge.service.file.fileService import FileService
from pipebridge.models.card import Card
from pipebridge.models.phase import Phase
from pipebridge.exceptions import PipefyInitializationError
from pipebridge.integrations.file.fileUploadResult import FileUploadResult
from pipebridge.models.file.fileDownloadRequest import FileDownloadRequest

# ============================================================
# Domain: Cards
# ============================================================


class CardsFacade:
    """
    Public facade for card operations exposed by the SDK.

    This facade keeps the public API stable while delegating business logic
    to :class:`pipebridge.service.card.cardService.CardService`.
    """

    def __init__(self, service: CardService) -> None:
        """
        Initialize CardsFacade.

        :param service: CardService = Card service instance
        """
        self._service: CardService = service
        self.raw: CardsRawFacade
        self.structured: CardsStructuredFacade

    def get(self, card_id: str) -> Card:
        """
        Retrieve a card as a model.

        :param card_id: str = Card identifier

        :return: Card = Card model instance

        :raises ValidationError:
            When input validation fails
        :raises ParsingError:
            When model parsing fails
        :raises RequestError:
            When request execution fails

        :example:
            >>> callable(CardsFacade.get)
            True
        """
        return self._service.getCardModel(card_id)

    def create(
        self, pipe_id: str, title: str, fields: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new card.

        :param pipe_id: str = Pipe identifier
        :param title: str = Card title
        :param fields: dict[str, Any] | None = Field values

        :return: dict = Raw API response

        :raises ValidationError:
            When input validation fails
        :raises RequestError:
            When a transport or API request fails

        :example:
            >>> callable(CardsFacade.create)
            True
        """
        return self._service.createCard(pipe_id, title, fields)

    def move(self, card_id: str, phase_id: str) -> Dict[str, Any]:
        """
        Move a card to another phase.

        :param card_id: str = Card identifier
        :param phase_id: str = Destination phase ID

        :return: dict = Raw API response

        :raises ValidationError:
            When input validation fails
        :raises RequestError:
            When a transport or API request fails

        :example:
            >>> callable(CardsFacade.move)
            True
        """
        return self._service.moveCardToPhase(card_id, phase_id)

    def moveSafely(
        self,
        card_id: str,
        destination_phase_id: str,
        expected_current_phase_id: Optional[str] = None,
        config: Optional[CardMoveConfig] = None,
        extra_rules: Optional[List[BaseRule]] = None,
    ) -> Dict[str, Any]:
        """
        Move a card to another phase after validating transition readiness.

        This is the recommended public entry point when the caller wants the
        SDK to validate destination required fields before moving the card.

        :param card_id: str = Card identifier
        :param destination_phase_id: str = Destination phase identifier
        :param expected_current_phase_id: str | None = Optional expected source
            phase identifier
        :param config: CardMoveConfig | None = Optional move flow configuration
        :param extra_rules: list[BaseRule] | None = Optional extra rules

        :return: dict = Raw move API response
        """
        return self._service.moveCardToPhaseSafely(
            card_id=card_id,
            destination_phase_id=destination_phase_id,
            expected_current_phase_id=expected_current_phase_id,
            config=config,
            extra_rules=extra_rules,
        )

    def delete(self, card_id: str) -> Dict[str, Any]:
        """
        Delete a card.

        :param card_id: str = Card identifier

        :return: dict = Raw API response

        :raises ValidationError:
            When input validation fails
        :raises RequestError:
            When a transport or API request fails

        :example:
            >>> callable(CardsFacade.delete)
            True
        """
        return self._service.deleteCard(card_id)

    def list(self, pipe_id: str) -> List[Card]:
        """
        List all cards from a pipe.

        :param pipe_id: str = Pipe identifier

        :return: list[Card] = List of card models

        :raises ValidationError:
            When input validation fails
        :raises ParsingError:
            When a card model cannot be parsed
        :raises UnexpectedResponseError:
            When the API response structure is invalid
        :raises RequestError:
            When a transport or API request fails

        :example:
            >>> callable(CardsFacade.list)
            True
        """
        return self._service.listAllCardsPaginated(pipe_id)

    def search(self, pipe_id: str, title: str) -> List[Dict[str, Any]]:
        """
        Search cards by title.

        :param pipe_id: str = Pipe identifier
        :param title: str = Search term

        :return: list[dict] = Matching cards

        :raises ValidationError:
            When input validation fails
        :raises UnexpectedResponseError:
            When the API response structure is invalid
        :raises RequestError:
            When a transport or API request fails

        :example:
            >>> callable(CardsFacade.search)
            True
        """
        return self._service.searchCards(pipe_id, title)

    def updateField(
        self,
        card_id: str,
        field_id: str,
        value: Any,
        config: Optional[CardUpdateConfig] = None,
        extra_rules: Optional[List[BaseRule]] = None,
        extra_handlers: Optional[Dict[str, BaseCardFieldUpdateHandler]] = None,
    ) -> Dict[str, Any]:
        """
        Update a single card field through the public facade.

        :param card_id: str = Card identifier
        :param field_id: str = Logical field identifier
        :param value: Any = New field value
        :param config: CardUpdateConfig | None = Optional update flow configuration
        :param extra_rules: list[BaseRule] | None = Optional custom validation rules

        :return: dict = Raw API response keyed by updated field

        :raises ValidationError:
            When input validation fails
        :raises WorkflowError:
            When update workflow execution fails
        :raises RequestError:
            When a transport or API request fails
        """
        return self._service.updateFields(
            card_id=card_id,
            fields={field_id: value},
            config=config,
            extra_rules=extra_rules,
            extra_handlers=extra_handlers,
        )

    def updateFields(
        self,
        card_id: str,
        fields: Dict[str, Any],
        expected_phase_id: Optional[str] = None,
        config: Optional[CardUpdateConfig] = None,
        extra_rules: Optional[List[BaseRule]] = None,
        extra_handlers: Optional[Dict[str, BaseCardFieldUpdateHandler]] = None,
    ) -> Dict[str, Any]:
        """
        Update multiple card fields through the public facade.

        :param card_id: str = Card identifier
        :param fields: dict[str, Any] = Field values mapped by field ID
        :param expected_phase_id: str | None = Optional expected phase ID
        :param config: CardUpdateConfig | None = Optional update flow configuration
        :param extra_rules: list[BaseRule] | None = Optional custom validation rules

        :return: dict = Raw API responses keyed by updated field

        :raises ValidationError:
            When input validation fails
        :raises WorkflowError:
            When update workflow execution fails
        :raises RequestError:
            When a transport or API request fails
        """
        return self._service.updateFields(
            card_id=card_id,
            fields=fields,
            expected_phase_id=expected_phase_id,
            config=config,
            extra_rules=extra_rules,
            extra_handlers=extra_handlers,
        )

    def invalidateSchemaCache(self, pipe_id: Optional[str] = None) -> None:
        """
        Invalidate the in-memory pipe schema cache used by card update flows.

        :param pipe_id: str | None = Specific pipe identifier. When omitted,
            the whole schema cache is invalidated.

        :return: None
        """
        self._service.invalidatePipeSchemaCache(pipe_id)

    def getSchemaCacheStats(self) -> Dict[str, Any]:
        """
        Retrieve aggregate statistics about the card schema cache.

        :return: dict = Cache statistics
        """
        return self._service.getPipeSchemaCacheStats()

    def getSchemaCacheEntryInfo(self, pipe_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve metadata about a specific cached schema entry.

        :param pipe_id: str = Pipe identifier

        :return: dict | None = Cache entry metadata
        """
        return self._service.getPipeSchemaCacheEntryInfo(pipe_id)


# ============================================================
# Domain: Cards (Raw)
# ============================================================


class CardsRawFacade:
    """
    Low-level card operations (raw GraphQL access).

    :param service: CardService = Card service instance

    :example:
        >>> callable(CardsRawFacade.get)
        True
    """

    def __init__(self, service: CardService) -> None:
        """
        Initialize CardsRawFacade.

        :param service: CardService = Card service instance
        """
        self._service: CardService = service

    def get(self, card_id: str, query: str) -> Dict[str, Any]:
        """
        Retrieve raw card data using custom GraphQL query.

        :param card_id: str = Card identifier
        :param query: str = GraphQL query

        :return: dict = Raw API response

        :raises ValidationError:
            When input validation fails
        :raises RequestError:
            When a transport or API request fails

        :example:
            >>> callable(CardsRawFacade.get)
            True
        """
        return self._service.getRawCard(card_id, query)


# ============================================================
# Domain: Cards (Structured)
# ============================================================


class CardsStructuredFacade:
    """
    Intermediate-level card operations (structured response).

    :param service: CardService = Card service instance

    :example:
        >>> callable(CardsStructuredFacade.get)
        True
    """

    def __init__(self, service: CardService) -> None:
        """
        Initialize CardsStructuredFacade.

        :param service: CardService = Card service instance
        """
        self._service: CardService = service

    def get(self, card_id: str, query_body: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve structured card data.

        :param card_id: str = Card identifier
        :param query_body: str | None = Custom query body

        :return: dict = Structured response

        :raises ValidationError:
            When input validation fails
        :raises UnexpectedResponseError:
            When the API response structure is invalid
        :raises RequestError:
            When a transport or API request fails

        :example:
            >>> callable(CardsStructuredFacade.get)
            True
        """
        return self._service.getCardStructured(card_id, query_body)


# ============================================================
# Domain: Phases
# ============================================================


class PhasesFacade:
    """
    Public facade for phase retrieval operations.

    This facade exposes high-level access to phase data while keeping the
    underlying service layer internal to the SDK.
    """

    def __init__(self, service: PhaseService, card_service: CardService) -> None:
        """
        Initialize PhasesFacade.

        :param service: PhaseService = Phase service
        :param card_service: CardService = Card service
        """
        self._service: PhaseService = service
        self._card_service: CardService = card_service
        self.raw: PhasesRawFacade
        self.structured: PhasesStructuredFacade

    def get(self, phase_id: str, query_body: Optional[str] = None) -> Phase:
        """
        Retrieve a phase model.

        :param phase_id: str = Phase identifier
        :param query_body: str | None = Optional GraphQL query body

        :return: Phase = Phase model instance

        :raises ValidationError:
            When phase_id is invalid
        :raises ParsingError:
            When model parsing fails
        :raises RequestError:
            When request execution fails

        :example:
            >>> callable(PhasesFacade.get)
            True
        """
        return self._service.getPhaseModel(phase_id, query_body)

    def listCards(self, phase_id: str) -> List[Card]:
        """
        List all cards from a phase.

        :param phase_id: str = Phase identifier

        :return: list[Card] = Cards in phase

        :raises Exception:
            Propagates service exceptions

        :example:
            >>> callable(PhasesFacade.listCards)
            True
        """
        return self._card_service.listCardsFromPhasePaginated(phase_id)


# ============================================================
# Domain: Phases (Raw)
# ============================================================


class PhasesRawFacade:
    """
    Low-level phase operations (raw GraphQL access).

    :param service: PhaseService = Phase service instance

    :example:
        >>> callable(PhasesRawFacade.get)
        True
    """

    def __init__(self, service: PhaseService) -> None:
        """
        Initialize PhasesRawFacade.

        :param service: PhaseService = Phase service instance
        """
        self._service: PhaseService = service
        self.raw: PhasesRawFacade
        self.structured: PhasesStructuredFacade

    def get(self, phase_id: str, query: str) -> Dict[str, Any]:
        """
        Retrieve raw phase data.

        :param phase_id: str = Phase identifier
        :param query: str = GraphQL query body

        :return: dict = Raw API response

        :raises ValidationError:
            When ``phase_id`` or ``query`` is invalid
        :raises RequestError:
            When a transport or API request fails

        :example:
            >>> callable(PhasesRawFacade.get)
            True
        """
        return self._service.getPhaseRaw(phase_id, query)


# ============================================================
# Domain: Phases (Structured)
# ============================================================


class PhasesStructuredFacade:
    """
    Intermediate-level phase operations (structured response).

    :param service: PhaseService = Phase service instance

    :example:
        >>> callable(PhasesStructuredFacade.get)
        True
    """

    def __init__(self, service: PhaseService) -> None:
        """
        Initialize PhasesStructuredFacade.

        :param service: PhaseService = Phase service instance
        """
        self._service: PhaseService = service

    def get(self, phase_id: str, query_body: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve structured phase data.

        :param phase_id: str = Phase identifier
        :param query_body: str | None = Custom query body

        :return: dict = Structured response

        :raises ValidationError:
            When ``phase_id`` is invalid
        :raises UnexpectedResponseError:
            When the API response structure is invalid
        :raises RequestError:
            When a transport or API request fails

        :example:
            >>> callable(PhasesStructuredFacade.get)
            True
        """
        return self._service.getPhaseStructured(phase_id, query_body)


# ============================================================
# Domain: Pipes
# ============================================================


class PipesFacade:
    """
    Public facade for pipe retrieval and schema discovery operations.

    This facade is the recommended entry point for consumers that need pipe
    models, raw responses, or field catalog discovery.
    """

    def __init__(self, service: PipeService) -> None:
        """
        Initialize PipesFacade.

        :param service: PipeService = Pipe service
        """
        self._service: PipeService = service
        self.raw: PipesRawFacade
        self.structured: PipesStructuredFacade

    def get(self, pipe_id: str, query_body: Optional[str] = None) -> Pipe:
        """
        Retrieve a pipe model.

        :param pipe_id: str = Pipe identifier
        :param query_body: str | None = Optional GraphQL query body

        :return: Pipe = PipeService model instance

        :raises ValidationError:
            When pipe_id is invalid
        :raises ParsingError:
            When model parsing fails
        :raises RequestError:
            When request execution fails

        :example:
            >>> callable(PipesFacade.get)
            True
        """
        return self._service.getPipeModel(pipe_id, query_body)

    def getFieldCatalog(self, pipe_id: str) -> Pipe:
        """
        Retrieve all phases and configured fields for a pipe.

        This is the discovery-oriented variant of ``get()``, useful for
        building update coverage and inspecting the schema available in a pipe.

        :param pipe_id: str = Pipe identifier

        :return: Pipe = Pipe model with phase fields populated

        :raises ValidationError:
            When pipe_id is invalid
        :raises ParsingError:
            When model parsing fails
        :raises RequestError:
            When request execution fails

        :example:
            >>> callable(PipesFacade.getFieldCatalog)
            True
        """
        return self._service.getPipeFieldCatalog(pipe_id)


# ============================================================
# Domain: Pipes (Raw)
# ============================================================


class PipesRawFacade:
    """
    Low-level pipe operations (raw GraphQL access).

    :param service: PipeService = Pipe service instance

    :example:
        >>> callable(PipesRawFacade.get)
        True
    """

    def __init__(self, service: PipeService) -> None:
        """
        Initialize PipesRawFacade.

        :param service: PipeService = Pipe service instance
        """
        self._service: PipeService = service

    def get(self, pipe_id: str, query: str) -> Dict[str, Any]:
        """
        Retrieve raw pipe data.

        :param pipe_id: str = Pipe identifier
        :param query: str = GraphQL query body

        :return: dict = Raw API response

        :raises ValidationError:
            When ``pipe_id`` or ``query`` is invalid
        :raises RequestError:
            When a transport or API request fails

        :example:
            >>> callable(PipesRawFacade.get)
            True
        """
        return self._service.getPipeRaw(pipe_id, query)


# ============================================================
# Domain: Pipes (Structured)
# ============================================================


class PipesStructuredFacade:
    """
    Intermediate-level pipe operations (structured response).

    :param service: PipeService = Pipe service instance

    :example:
        >>> callable(PipesStructuredFacade.get)
        True
    """

    def __init__(self, service: PipeService) -> None:
        """
        Initialize PipesStructuredFacade.

        :param service: PipeService = Pipe service instance
        """
        self._service: PipeService = service

    def get(self, pipe_id: str, query_body: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve structured pipe data.

        :param pipe_id: str = Pipe identifier
        :param query_body: str | None = Optional GraphQL fields

        :return: dict = Structured response

        :raises ValidationError:
            When ``pipe_id`` is invalid
        :raises UnexpectedResponseError:
            When the API response structure is invalid
        :raises RequestError:
            When a transport or API request fails

        :example:
            >>> callable(PipesStructuredFacade.get)
            True
        """
        return self._service.getPipeStructured(pipe_id, query_body)


# ============================================================
# Domain: Files
# ============================================================


class FilesFacade:
    """
    Facade for file operations in Pipefy.

    This class provides a unified and simplified interface for file
    upload and download operations.

    DESIGN PRINCIPLES:
        - Uses request objects (no primitive parameter explosion)
        - Delegates all logic to FileService
        - Maintains a stable API boundary

    :param service: FileService

    :example:
        >>> callable(FilesFacade.uploadFile)
        True
    """

    def __init__(self, service: FileService) -> None:
        """
        Initializes FilesFacade.

        :param service: FileService
        """
        self._service = service

    # ============================================================
    # Upload
    # ============================================================

    def uploadFile(
        self,
        request: FileUploadRequest,
        extra_rules: Optional[list[BaseRule]] = None,
        config: Optional[UploadConfig] = None,
        extra_steps_before: Optional[Sequence[BaseStep]] = None,
        extra_steps_after: Optional[Sequence[BaseStep]] = None,
    ) -> FileUploadResult:
        """
        Uploads a file using a structured request object.

        :param request: FileUploadRequest
        :param extra_rules: Optional[list[BaseRule]] = Set of custom rules constructed by te user.
            The rules will be applied before the upload flow.
        :param config: Optional[UploadConfig] = Configuration for upload process
        :param extra_steps_before: Optional[Sequence[BaseStep]] = Additional
            custom steps executed before the built-in upload pipeline
        :param extra_steps_after: Optional[Sequence[BaseStep]] = Additional
            custom steps executed after the built-in upload pipeline

        :return: FileUploadResult

        :raises ValidationError:
            When ``request`` is invalid
        :raises FileFlowError:
            When the upload flow fails semantically
        :raises WorkflowError:
            When a workflow rule or step fails technically
        :raises RequestError:
            When a transport or API request fails

        :example:
            >>> callable(FilesFacade.uploadFile)
            True
        """
        return self._service.uploadFile(
            request=request,
            extra_rules=extra_rules,
            config=config,
            extra_steps_before=extra_steps_before,
            extra_steps_after=extra_steps_after,
        )

    # ============================================================
    # Download
    # ============================================================

    def downloadAllAttachments(self, request: FileDownloadRequest) -> List[Path]:
        """
        Downloads all attachments from a card field.

        This method delegates execution to FileService using a
        structured request object.

        :param request: FileDownloadRequest

        :return: list[Path] = List of saved file paths

        :raises ValidationError:
            When ``request`` is invalid
        :raises FileDownloadError:
            When attachment parsing or download fails
        :raises RequestError:
            When a transport or API request fails

        :example:
            >>> callable(FilesFacade.downloadAllAttachments)
            True
        """
        return self._service.downloadAllAttachments(request)


# ============================================================
# Root Facade
# ============================================================


class PipeBridge:
    """
    Root public facade of the Pipefy SDK.

    This class wires the HTTP client and all domain facades, exposing a
    cohesive and stable API surface for cards, phases, pipes, and files.
    """

    def __init__(
        self,
        token: str,
        base_url: str,
        pipe_schema_cache_ttl_seconds: int = 300,
    ) -> None:
        """
        Initialize Pipefy facade.

        :param token: str = API authentication token
        :param base_url: str = Pipefy GraphQL endpoint

        :raises PipefyInitializationError:
            When token or base_url is invalid, or when SDK composition fails

        :example:
            >>> callable(PipeBridge)
            True
        """

        class_name, method_name = getExceptionContext(self)

        if not isinstance(token, str) or not token.strip():
            raise PipefyInitializationError(
                message="Invalid token", class_name=class_name, method_name=method_name
            )

        if (
            not isinstance(base_url, str)
            or not base_url.strip()
            or not base_url.strip().startswith("https://")
        ):
            raise PipefyInitializationError(
                message="Invalid base_url",
                class_name=class_name,
                method_name=method_name,
            )

        try:
            client = PipefyHttpClient(auth_key=token, base_url=base_url)

            card_service = CardService(
                client,
                pipe_schema_cache_ttl_seconds=pipe_schema_cache_ttl_seconds,
            )
            pipe_service = PipeService(client)
            phase_service = PhaseService(client)
            file_service = FileService(client, card_service)

            self.cards = CardsFacade(card_service)
            # sub-dominios
            self.cards.raw = CardsRawFacade(card_service)
            self.cards.structured = CardsStructuredFacade(card_service)

            self.phases = PhasesFacade(phase_service, card_service)
            # 🔥 sub-domínios
            self.phases.raw = PhasesRawFacade(phase_service)
            self.phases.structured = PhasesStructuredFacade(phase_service)

            self.pipes = PipesFacade(pipe_service)
            # 🔥 sub-domínios
            self.pipes.raw = PipesRawFacade(pipe_service)
            self.pipes.structured = PipesStructuredFacade(pipe_service)

            self.files = FilesFacade(file_service)

        except Exception as exc:
            raise PipefyInitializationError(str(exc)) from exc
