# ============================================================
# Dependencies
# ============================================================
from pathlib import Path
from typing import Any, Dict, Optional, List

from pipefy.client.httpClient import PipefyHttpClient
from pipefy.exceptions import getExceptionContext
from pipefy.models.file.fileUploadRequest import FileUploadRequest
from pipefy.models.pipe import Pipe
from pipefy.service.cardService import CardService
from pipefy.service.pipeService import PipeService
from pipefy.service.phaseService import PhaseService
from pipefy.service.fileService import FileService
from pipefy.models.card import Card
from pipefy.models.phase import Phase
from pipefy.exceptions import PipefyInitializationError
from pipefy.integrations.file.fileUploadResult import FileUploadResult
from pipefy.models.file.fileDownloadRequest import FileDownloadRequest


# ============================================================
# Domain: Cards
# ============================================================

class CardsFacade:

    def __init__(self, service: CardService) -> None:
        """
        Initialize CardsFacade.

        :param service: CardService = Card service instance
        """
        self._service: CardService = service

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
        self,
        pipe_id: str,
        title: str,
        fields: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new card.

        :param pipe_id: str = Pipe identifier
        :param title: str = Card title
        :param fields: dict[str, Any] | None = Field values

        :return: dict = Raw API response

        :raises Exception:
            Propagates service exceptions

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

        :raises Exception:
            Propagates service exceptions

        :example:
            >>> callable(CardsFacade.move)
            True
        """
        return self._service.moveCardToPhase(card_id, phase_id)

    def delete(self, card_id: str) -> Dict[str, Any]:
        """
        Delete a card.

        :param card_id: str = Card identifier

        :return: dict = Raw API response

        :raises Exception:
            Propagates service exceptions

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

        :raises Exception:
            Propagates service exceptions

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

        :raises Exception:
            Propagates service exceptions

        :example:
            >>> callable(CardsFacade.search)
            True
        """
        return self._service.searchCards(pipe_id, title)


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

        :raises Exception:
            Propagates service exceptions

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

        :raises Exception:
            Propagates service exceptions

        :example:
            >>> callable(CardsStructuredFacade.get)
            True
        """
        return self._service.getCardStructured(card_id, query_body)

# ============================================================
# Domain: Phases
# ============================================================

class PhasesFacade:

    def __init__(self, service: PhaseService, card_service: CardService) -> None:
        """
        Initialize PhasesFacade.

        :param service: PhaseService = Phase service
        :param card_service: CardService = Card service
        """
        self._service = service
        self._card_service = card_service

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

    def get(self, phase_id: str, query: str) -> Dict[str, Any]:
        """
        Retrieve raw phase data.

        :param phase_id: str = Phase identifier
        :param query: str = GraphQL query body

        :return: dict = Raw API response

        :raises ValidationError:
        :raises RequestError:

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

    def get(
        self,
        phase_id: str,
        query_body: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve structured phase data.

        :param phase_id: str = Phase identifier
        :param query_body: str | None = Custom query body

        :return: dict = Structured response

        :raises ValidationError:
        :raises UnexpectedResponseError:
        :raises RequestError:

        :example:
            >>> callable(PhasesStructuredFacade.get)
            True
        """
        return self._service.getPhaseStructured(phase_id, query_body)

# ============================================================
# Domain: Pipes
# ============================================================

class PipesFacade:

    def __init__(self, service: PipeService) -> None:
        """
        Initialize PipesFacade.

        :param service: PipeService = Pipe service
        """
        self._service: PipeService = service

    def get(
        self,
        pipe_id: str,
        query_body: Optional[str] = None
    ) -> Pipe:
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
        :raises RequestError:

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

    def get(
        self,
        pipe_id: str,
        query_body: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve structured pipe data.

        :param pipe_id: str = Pipe identifier
        :param query_body: str | None = Optional GraphQL fields

        :return: dict = Structured response

        :raises ValidationError:
        :raises UnexpectedResponseError:
        :raises RequestError:

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

    def uploadFile(self, request: FileUploadRequest) -> FileUploadResult:
        """
        Uploads a file using a structured request object.

        :param request: FileUploadRequest

        :return: FileUploadResult

        :example:
            >>> callable(FilesFacade.uploadFile)
            True
        """
        return self._service.uploadFile(request)

    # ============================================================
    # Download
    # ============================================================

    def downloadAllAttachments(
        self,
        request: FileDownloadRequest
    ) -> List[Path]:
        """
        Downloads all attachments from a card field.

        This method delegates execution to FileService using a
        structured request object.

        :param request: FileDownloadRequest

        :return: list[Path] = List of saved file paths

        :example:
            >>> callable(FilesFacade.downloadAllAttachments)
            True
        """
        return self._service.downloadAllAttachments(request)



# ============================================================
# Root Facade
# ============================================================

class Pipefy:

    def __init__(self, token: str, base_url: str) -> None:
        """
        Initialize Pipefy facade.

        :param token: str = API authentication token
        :param base_url: str = Pipefy GraphQL endpoint

        :raises PipefyInitializationError:
            When token or base_url is invalid
        :raises ConfigurationError:
            When client initialization fails

        :example:
            >>> callable(Pipefy)
            True
        """

        class_name, method_name = getExceptionContext(self)

        if not isinstance(token, str) or not token.strip():
            raise PipefyInitializationError(
                message="Invalid token",
                class_name=class_name,
                method_name=method_name
            )

        if not isinstance(base_url, str) or not base_url.strip() or not base_url.strip().startswith('https://'):
            raise PipefyInitializationError(
                message="Invalid base_url",
                class_name=class_name,
                method_name=method_name
            )

        try:
            client = PipefyHttpClient(auth_key=token, base_url=base_url)

            card_service = CardService(client)
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


