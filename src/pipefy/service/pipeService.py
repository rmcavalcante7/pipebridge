# ============================================================
# Dependencies
# ============================================================
from typing import Dict, Any, Optional

from pipefy.client.httpClient import PipefyHttpClient
from pipefy.exceptions import (
    RequestError,
    ValidationError,
    ParsingError,
    UnexpectedResponseError,
    getExceptionContext
)
from pipefy.models.pipe import Pipe


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
        self._client: PipefyHttpClient = client

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
            When request execution fails

        :example:
            >>> callable(PipeService.getPipeRaw)
            True
        """
        class_name, method_name = getExceptionContext(self)

        if not pipe_id or not isinstance(pipe_id, str):
            raise ValidationError(
                message="pipe_id must be a non-empty string",
                class_name=class_name,
                method_name=method_name
            )

        if not query_body or not isinstance(query_body, str):
            raise ValidationError(
                message="query_body must be a non-empty string",
                class_name=class_name,
                method_name=method_name
            )

        try:
            query: str = f"""
            {{
                pipe(id: "{pipe_id}") {{
                    {query_body}
                }}
            }}
            """

            return self._client.sendRequest(query, timeout=60)

        except Exception as exc:
            raise RequestError(
                message=str(exc),
                class_name=class_name,
                method_name=method_name
            ) from exc

    # ============================================================
    # STRUCTURED
    # ============================================================

    def getPipeStructured(
        self,
        pipe_id: str,
        query_body: Optional[str] = None
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
            When request execution fails

        :example:
            >>> callable(PipeService.getPipeStructured)
            True
        """
        class_name, method_name = getExceptionContext(self)

        if not pipe_id or not isinstance(pipe_id, str):
            raise ValidationError(
                message="pipe_id must be a non-empty string",
                class_name=class_name,
                method_name=method_name
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
                    method_name=method_name
                )

            pipe_data = data.get("pipe")
            if not isinstance(pipe_data, dict):
                raise UnexpectedResponseError(
                    message="'pipe' field missing",
                    class_name=class_name,
                    method_name=method_name
                )

            return pipe_data

        except (ValidationError, UnexpectedResponseError):
            raise

        except Exception as exc:
            raise RequestError(
                message=str(exc),
                class_name=class_name,
                method_name=method_name
            ) from exc

    # ============================================================
    # MODEL
    # ============================================================

    def getPipeModel(
        self,
        pipe_id: str,
        query_body: Optional[str] = None
    ) -> Pipe:
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
            When request execution fails

        :example:
            >>> callable(PipeService.getPipeModel)
            True
        """
        class_name, method_name = getExceptionContext(self)

        try:
            pipe_data: Dict[str, Any] = self.getPipeStructured(
                pipe_id,
                query_body
            )

            try:
                return Pipe.fromDict(pipe_data)
            except Exception as exc:
                raise ParsingError(
                    message=str(exc),
                    class_name=class_name,
                    method_name=method_name
                ) from exc

        except (ValidationError, ParsingError):
            raise

        except Exception as exc:
            raise RequestError(
                message=str(exc),
                class_name=class_name,
                method_name=method_name
            ) from exc