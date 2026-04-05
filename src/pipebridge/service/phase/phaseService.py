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
from pipebridge.models.phase import Phase
from pipebridge.service.phase.queries.phaseQueries import PhaseQueries


class PhaseService:
    """
    Service responsible for handling Phase operations.

    This service provides methods to retrieve raw, structured,
    and model-based representations of Pipefy Phases.

    It follows a layered architecture:
        RAW → STRUCTURED → MODEL

    :param client: PipefyHttpClient = HTTP client instance
    """

    def __init__(self, client: PipefyHttpClient) -> None:
        """
        Initialize PhaseService.

        :param client: PipefyHttpClient = HTTP client instance
        """
        self._client: PipefyHttpClient = client

    # ============================================================
    # RAW
    # ============================================================

    def getPhaseRaw(self, phase_id: str, query_body: str) -> Dict[str, Any]:
        """
        Retrieve raw phase data using a custom GraphQL query body.

        This method provides full flexibility for defining which fields
        should be retrieved from the Pipefy API.

        :param phase_id: str = Phase identifier
        :param query_body: str = GraphQL fields to retrieve

        :return: dict = Raw API response

        :raises ValidationError:
            When phase_id or query_body is invalid
        :raises RequestError:
            When an unexpected request-layer failure occurs

        :example:
            >>> callable(PhaseService.getPhaseRaw)
            True
        """
        class_name, method_name = getExceptionContext(self)

        if not phase_id or not isinstance(phase_id, str):
            raise ValidationError(
                message="phase_id must be a non-empty string",
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
            query: str = PhaseQueries.getById(phase_id=phase_id, query_body=query_body)

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

    # ============================================================
    # STRUCTURED
    # ============================================================

    def getPhaseStructured(
        self, phase_id: str, query_body: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve structured phase data.

        This method abstracts GraphQL complexity and returns a cleaned,
        consistent dictionary containing the requested phase data.

        If no query_body is provided, a default structure including
        fields metadata is used.

        :param phase_id: str = Phase identifier
        :param query_body: str | None = Optional GraphQL fields

        :return: dict = Structured phase data

        :raises ValidationError:
            When phase_id is invalid
        :raises UnexpectedResponseError:
            When response structure is invalid
        :raises RequestError:
            When an unexpected request-layer failure occurs

        :example:
            >>> callable(PhaseService.getPhaseStructured)
            True
        """
        class_name, method_name = getExceptionContext(self)

        if not phase_id or not isinstance(phase_id, str):
            raise ValidationError(
                message="phase_id must be a non-empty string",
                class_name=class_name,
                method_name=method_name,
            )

        if not query_body:
            query_body = """
                id
                name

                fields {
                    id
                    label
                    type
                    required
                    description
                    options
                    uuid
                }
            """

        try:
            response: Dict[str, Any] = self.getPhaseRaw(phase_id, query_body)

            data = response.get("data")
            if not isinstance(data, dict):
                raise UnexpectedResponseError(
                    message="'data' field missing or invalid",
                    class_name=class_name,
                    method_name=method_name,
                )

            phase_data = data.get("phase")
            if not isinstance(phase_data, dict):
                raise UnexpectedResponseError(
                    message="'phase' field missing",
                    class_name=class_name,
                    method_name=method_name,
                )

            return phase_data

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

    def getPhaseModel(self, phase_id: str, query_body: Optional[str] = None) -> Phase:
        """
        Retrieve a Phase as a strongly-typed model.

        This method converts structured phase data into a Phase object,
        enabling advanced access patterns such as O(1) field lookup.

        :param phase_id: str = Phase identifier
        :param query_body: str | None = Optional GraphQL fields

        :return: Phase = Parsed Phase model

        :raises ValidationError:
            When phase_id is invalid
        :raises ParsingError:
            When model parsing fails
        :raises RequestError:
            When an unexpected request-layer failure occurs

        :example:
            >>> callable(PhaseService.getPhaseModel)
            True
        """
        class_name, method_name = getExceptionContext(self)

        try:
            phase_data: Dict[str, Any] = self.getPhaseStructured(phase_id, query_body)

            try:
                return Phase.fromDict(phase_data)
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


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    client = PipefyHttpClient(
        auth_key="your_token_here",
        base_url="https://app.pipefy.com/queries",
    )
    service = PhaseService(client)

    try:
        phase = service.getPhaseModel("123456")

        print("ID:", phase.id)
        print("Name:", phase.name)

        print("Fields count:", len(phase.fields))

        if phase.fields:
            first_field = phase.fields[0]
            print("First field:", first_field.id)

        print("✔ PhaseService OK")

    except Exception as e:
        print("❌ Error:", e)
