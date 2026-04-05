# ============================================================
# Dependencies
# ============================================================
from typing import Dict, Any, Optional

from pipebridge.client.httpClient import PipefyHttpClient
from pipebridge.exceptions import (
    PipefyError,
    RequestError,
    ValidationError,
    ParsingError,
    UnexpectedResponseError,
    getExceptionContext,
)
from pipebridge.models.pipe import Pipe
from pipebridge.models.phase import Phase
from pipebridge.service.phase.phaseService import PhaseService
from pipebridge.service.pipe.queries.pipeQueries import PipeQueries


class PipeService:
    """
    Service responsible for Pipe operations.

    This service follows a layered architecture:

        RAW → STRUCTURED → MODEL

    It provides a unified and flexible interface to retrieve
    pipe data, including phases, labels, and users.

    :param client: PipefyHttpClient = HTTP client instance
    """

    def __init__(self, client: PipefyHttpClient) -> None:
        """
        Initialize the pipe service and its dependent phase service.

        :param client: PipefyHttpClient = Shared HTTP client
        """
        self._client: PipefyHttpClient = client
        self._phase_service: PhaseService = PhaseService(client)

    # ============================================================
    # RAW
    # ============================================================

    def getPipeRaw(self, pipe_id: str, query_body: str) -> Dict[str, Any]:
        """
        Retrieve raw pipe data using a custom GraphQL query.

        :param pipe_id: str = Pipe identifier
        :param query_body: str = GraphQL fields to retrieve

        :return: dict = Raw API response

        :raises ValidationError:
            When pipe_id or query_body is invalid
        :raises RequestError:
            When an unexpected request-layer failure occurs

        :example:
            >>> callable(PipeService.getPipeRaw)
            True
        """
        class_name, method_name = getExceptionContext(self)

        if not pipe_id or not isinstance(pipe_id, str):
            raise ValidationError(
                message="pipe_id must be a non-empty string",
                class_name=class_name,
                method_name=method_name,
            )

        if not query_body or not isinstance(query_body, str):
            raise ValidationError(
                message="query_body must be a non-empty string",
                class_name=class_name,
                method_name=method_name,
            )

        try:
            query: str = PipeQueries.getById(pipe_id=pipe_id, query_body=query_body)

            return self._client.sendRequest(query, timeout=60)

        except PipefyError:
            raise

        except Exception as exc:
            raise RequestError(
                message=str(exc),
                class_name=class_name,
                method_name=method_name,
                cause=exc,
                retryable=getattr(exc, "retryable", False),
            ) from exc

    def getPipeFieldCatalog(self, pipe_id: str) -> Pipe:
        """
        Retrieve all configured phases and fields for a pipe as a model.

        This method is intended for field discovery and schema inspection.
        It returns the canonical Pipe model, with each phase populated with
        its field metadata.

        :param pipe_id: str = Pipe identifier

        :return: Pipe = Pipe model with phase fields populated

        :raises ValidationError:
            When pipe_id is invalid
        :raises ParsingError:
            When model parsing fails
        :raises RequestError:
            When an unexpected request-layer failure occurs

        :example:
            >>> callable(PipeService.getPipeFieldCatalog)
            True
        """
        class_name, method_name = getExceptionContext(self)

        try:
            pipe: Pipe = self.getPipeModel(
                pipe_id=pipe_id,
                query_body="""
                    id
                    name
                    cards_count

                    organization {
                        id
                    }

                    users {
                        id
                        name
                        email
                    }

                    phases {
                        id
                        name
                    }
                """,
            )

            enriched_phases = [
                self._phase_service.getPhaseModel(phase.id)
                for phase in pipe.phases
                if isinstance(phase, Phase) and phase.id
            ]

            return Pipe(
                id=pipe.id,
                name=pipe.name,
                cards_count=pipe.cards_count,
                organization_id=pipe.organization_id,
                phases=enriched_phases,
                labels=pipe.labels,
                users=pipe.users,
            )

        except PipefyError:
            raise

        except Exception as exc:
            raise RequestError(
                message=str(exc),
                class_name=class_name,
                method_name=method_name,
                cause=exc,
                retryable=getattr(exc, "retryable", False),
            ) from exc

    # ============================================================
    # STRUCTURED
    # ============================================================

    def getPipeStructured(
        self, pipe_id: str, query_body: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve structured pipe data.

        This method abstracts GraphQL complexity and returns a cleaned,
        consistent dictionary representing a pipe.

        If no query_body is provided, a default query including
        phases, labels, users, and card count is used.

        :param pipe_id: str = Pipe identifier
        :param query_body: str | None = Optional GraphQL fields

        :return: dict = Structured pipe data

        :raises ValidationError:
            When pipe_id is invalid
        :raises UnexpectedResponseError:
            When response structure is invalid
        :raises RequestError:
            When an unexpected request-layer failure occurs

        :example:
            >>> callable(PipeService.getPipeStructured)
            True
        """
        class_name, method_name = getExceptionContext(self)

        if not pipe_id or not isinstance(pipe_id, str):
            raise ValidationError(
                message="pipe_id must be a non-empty string",
                class_name=class_name,
                method_name=method_name,
            )

        if not query_body:
            query_body = """
                id
                name
                cards_count
                
                organization {
                    id
                }
                
                labels {
                    id
                    name
                    color
                }

                users {
                    id
                    name
                    email
                }

                phases {
                    id
                    name
                }
            """

        try:
            response: Dict[str, Any] = self.getPipeRaw(pipe_id, query_body)

            data = response.get("data")
            if not isinstance(data, dict):
                raise UnexpectedResponseError(
                    message="'data' field missing or invalid",
                    class_name=class_name,
                    method_name=method_name,
                )

            pipe_data = data.get("pipe")
            if not isinstance(pipe_data, dict):
                raise UnexpectedResponseError(
                    message="'pipe' field missing",
                    class_name=class_name,
                    method_name=method_name,
                )

            return pipe_data

        except PipefyError, ValidationError, UnexpectedResponseError:
            raise

        except Exception as exc:
            raise RequestError(
                message=str(exc),
                class_name=class_name,
                method_name=method_name,
                cause=exc,
                retryable=getattr(exc, "retryable", False),
            ) from exc

    # ============================================================
    # MODEL
    # ============================================================

    def getPipeModel(self, pipe_id: str, query_body: Optional[str] = None) -> Pipe:
        """
        Retrieve a Pipe as a strongly-typed model.

        This method converts structured pipe data into a Pipe object,
        enabling direct access to phases, labels, and users without loops.

        :param pipe_id: str = Pipe identifier
        :param query_body: str | None = Optional GraphQL fields

        :return: Pipe = Parsed Pipe model

        :raises ValidationError:
            When pipe_id is invalid
        :raises ParsingError:
            When model parsing fails
        :raises RequestError:
            When an unexpected request-layer failure occurs

        :example:
            >>> callable(PipeService.getPipeModel)
            True
        """
        class_name, method_name = getExceptionContext(self)

        try:
            pipe_data: Dict[str, Any] = self.getPipeStructured(pipe_id, query_body)

            try:
                return Pipe.fromDict(pipe_data)
            except PipefyError:
                raise
            except Exception as exc:
                raise ParsingError(
                    message=str(exc),
                    class_name=class_name,
                    method_name=method_name,
                    cause=exc,
                ) from exc

        except PipefyError, ValidationError, ParsingError:
            raise

        except Exception as exc:
            raise RequestError(
                message=str(exc),
                class_name=class_name,
                method_name=method_name,
                cause=exc,
                retryable=getattr(exc, "retryable", False),
            ) from exc
