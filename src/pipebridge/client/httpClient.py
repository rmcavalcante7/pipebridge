# ============================================================
# Dependencies
# ============================================================
import inspect
import time
from typing import Any, Dict, Optional

import requests  # type: ignore[import-untyped]

from pipebridge.client.transportConfig import TransportConfig
from pipebridge.exceptions import (
    ValidationError,
    MissingBaseUrlError,
    RequestError,
    TransportAuthenticationError,
    TransportInvalidTokenError,
    TransportUnauthorizedError,
    TransportUnexpectedResponseError,
    TimeoutRequestError,
    ConnectionRequestError,
    RateLimitRequestError,
)


# ============================================================
# Http Client
# ============================================================
class PipefyHttpClient:
    """
    Handles HTTP communication with Pipefy GraphQL API.

    This class is responsible for:
    - Sending HTTP requests to Pipefy
    - Handling transport-level errors
    - Validating response structure
    - Mapping API errors to domain exceptions

    It does NOT:
    - Apply business rules
    - Transform domain data

    :param auth_key: str = API authentication token
    :param base_url: str = Pipefy GraphQL endpoint

    :raises ValidationError:
        When auth_key is invalid or empty
    :raises MissingBaseUrlError:
        When base_url is not provided

    :example:
        >>> client = PipefyHttpClient(auth_key="valid_token", base_url="www.pipebridge.example.com.br")
        >>> isinstance(client, PipefyHttpClient)
        True
    """

    def __init__(
        self,
        auth_key: str,
        base_url: str,
        transport_config: Optional[TransportConfig] = None,
    ) -> None:
        """
        Initialize the HTTP client with authentication and endpoint settings.

        :param auth_key: str = API authentication token
        :param base_url: str = Pipefy GraphQL endpoint

        :raises ValidationError:
            When ``auth_key`` is empty or invalid
        :raises MissingBaseUrlError:
            When ``base_url`` is empty or invalid
        """
        class_name, method_name = self._getContext()

        if not auth_key or not isinstance(auth_key, str):
            raise ValidationError(
                message="auth_key must be a non-empty string",
                class_name=class_name,
                method_name=method_name,
            )

        if not base_url or not isinstance(base_url, str):

            raise MissingBaseUrlError(
                message="base_url must be a non-empty string",
                class_name=class_name,
                method_name=method_name,
            )

        self._base_url: str = base_url
        self._transport_config: TransportConfig = transport_config or TransportConfig()

        self._headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {auth_key}",
        }

    # ============================================================
    # Public Methods
    # ============================================================
    def sendRequest(
        self, query: str, variables: Optional[Dict[str, Any]] = None, timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Sends a GraphQL request to Pipefy API.

        Handles:
        - Payload construction
        - HTTP request execution
        - JSON parsing
        - Response validation
        - Error mapping

        :param timeout:
        :param query: str = GraphQL query string
        :param variables: dict | None = Optional GraphQL variables

        :return: dict = Raw API response

        :raises ValidationError:
            If query is invalid

        :raises TimeoutRequestError:
            If the request exceeds the configured timeout
        :raises ConnectionRequestError:
            If the client cannot establish or maintain a connection
        :raises RateLimitRequestError:
            If Pipefy rejects the request due to rate limiting
        :raises TransportAuthenticationError:
            If the request fails due to authentication issues
        :raises TransportInvalidTokenError:
            If the provided API token is invalid
        :raises TransportUnauthorizedError:
            If the authenticated principal lacks permission
        :raises RequestError:
            If a generic transport or API failure occurs
        :raises TransportUnexpectedResponseError:
            If the response format is invalid

        :example:
            >>> client = PipefyHttpClient(auth_key="valid_token", base_url="www.pipebridge.example.com.br")
            >>> query = "{ me { id } }"
            >>> isinstance(query, str)
            True
        """
        class_name, method_name = self._getContext()

        if not query or not isinstance(query, str):
            raise ValidationError(
                message="query must be a non-empty string",
                class_name=class_name,
                method_name=method_name,
            )

        payload: Dict[str, Any] = {"query": query}

        if variables:
            payload["variables"] = variables

        # A custom transport timeout is expected to override SDK-level defaults
        # such as the legacy 60-second service timeouts.
        request_timeout = (
            self._transport_config.timeout
            if self._transport_config.timeout != 30
            else timeout
        )
        verify = self._transport_config.resolveVerifyValue()

        response = self._postWithRetry(
            payload=payload,
            request_timeout=request_timeout,
            verify=verify,
            class_name=class_name,
            method_name=method_name,
        )

        json_response: Dict[str, Any] = self._parseResponse(response)

        self._validateResponseStructure(json_response)

        self._handleErrors(json_response)

        return json_response

    @property
    def transport_config(self) -> TransportConfig:
        """
        Expose the effective transport configuration bound to this client.
        """
        return self._transport_config

    def _postWithRetry(
        self,
        payload: Dict[str, Any],
        request_timeout: int,
        verify: bool | str,
        class_name: str,
        method_name: str,
    ) -> requests.Response:
        """
        Execute the transport request with conservative retry behavior.
        """
        max_attempts = 1 + max(0, self._transport_config.max_retries)
        delay_seconds = max(0.0, self._transport_config.retry_delay_seconds)
        backoff_multiplier = max(1.0, self._transport_config.retry_backoff_multiplier)

        last_exc: Exception | None = None

        for attempt_index in range(max_attempts):
            try:
                return requests.post(
                    self._base_url,
                    json=payload,
                    headers=self._headers,
                    timeout=request_timeout,
                    verify=verify,
                )
            except requests.Timeout as exc:
                last_exc = TimeoutRequestError(
                    message=str(exc),
                    class_name=class_name,
                    method_name=method_name,
                    cause=exc,
                )
            except requests.ConnectionError as exc:
                last_exc = ConnectionRequestError(
                    message=str(exc),
                    class_name=class_name,
                    method_name=method_name,
                    cause=exc,
                )
            except requests.RequestException as exc:
                raise RequestError(
                    message=str(exc),
                    class_name=class_name,
                    method_name=method_name,
                    cause=exc,
                ) from exc

            if attempt_index >= max_attempts - 1:
                assert last_exc is not None
                raise last_exc

            if delay_seconds > 0:
                time.sleep(delay_seconds)
                delay_seconds *= backoff_multiplier

        raise RequestError(
            message="Unexpected transport retry state",
            class_name=class_name,
            method_name=method_name,
        )

    # ============================================================
    # Helper Methods
    # ============================================================
    def _parseResponse(self, response: requests.Response) -> Dict[str, Any]:
        """
        Parses HTTP response to JSON.

        :param response: requests.Response = HTTP response object
        :return: dict = Parsed JSON response

        :raises TransportUnexpectedResponseError:
            If response is not valid JSON
        """
        class_name, method_name = self._getContext()

        try:
            parsed = response.json()
            if not isinstance(parsed, dict):
                raise TypeError("Response JSON must be a dictionary")
            return parsed
        except ValueError as exc:
            raise TransportUnexpectedResponseError(
                message="Response is not valid JSON",
                class_name=class_name,
                method_name=method_name,
                cause=exc,
            ) from exc
        except TypeError as exc:
            raise TransportUnexpectedResponseError(
                message=str(exc),
                class_name=class_name,
                method_name=method_name,
                cause=exc,
            ) from exc

    def _validateResponseStructure(self, response: Dict[str, Any]) -> None:
        """
        Validates minimal GraphQL response structure.

        :param response: dict = Parsed JSON response

        :raises TransportUnexpectedResponseError:
            If response structure is invalid
        """
        class_name, method_name = self._getContext()

        if not isinstance(response, dict):
            raise TransportUnexpectedResponseError(
                message="Response must be a dictionary",
                class_name=class_name,
                method_name=method_name,
            )

        if (
            "data" not in response
            and "error" not in response
            and "errors" not in response
        ):
            raise TransportUnexpectedResponseError(
                message="Response must contain 'data' or 'errors'",
                class_name=class_name,
                method_name=method_name,
            )

    def _handleErrors(self, response: Dict[str, Any]) -> None:
        """
        Handles GraphQL and HTTP-level errors.

        :param response: dict = Parsed JSON response

        :raises TransportInvalidTokenError:
            When the provided token is invalid
        :raises TransportAuthenticationError:
            When authentication fails
        :raises TransportUnauthorizedError:
            When the authenticated principal lacks permission
        :raises RateLimitRequestError:
            When the API rejects the request due to rate limiting
        :raises RequestError:
            For generic API errors
        """
        class_name, method_name = self._getContext()

        if "error" not in response and "errors" not in response:
            return

        error_content = ""
        if "error" in response:
            error_content = response["error"]
        elif "errors" in response:
            error_content = response["errors"]

        message = str(error_content)

        lowered = message.lower()

        if "invalid token" in lowered or "invalid_token" in lowered:
            raise TransportInvalidTokenError(
                message=message, class_name=class_name, method_name=method_name
            )

        if "unauthorized" in lowered:
            raise TransportAuthenticationError(
                message=message, class_name=class_name, method_name=method_name
            )

        if "permission_denied" in lowered:
            raise TransportUnauthorizedError(
                message=message, class_name=class_name, method_name=method_name
            )

        if "rate limit" in lowered or "too many requests" in lowered:
            raise RateLimitRequestError(
                message=message, class_name=class_name, method_name=method_name
            )

        raise RequestError(
            message=message, class_name=class_name, method_name=method_name
        )

    def _getContext(self) -> tuple[str, str]:
        """
        Retrieves class and method context for exception messages.

        :return: tuple[str, str] = (class_name, method_name)
        """
        return (
            self.__class__.__name__,
            inspect.currentframe().f_back.f_code.co_name,  # type: ignore
        )


# ============================================================
# Main (Usage Example)
# ============================================================
if __name__ == "__main__":
    TOKEN = ""

    try:
        client = PipefyHttpClient(
            TOKEN, base_url="https://accenture.pipefy.com/queries"
        )

        query = """
        {
            me {
                id
            }
        }
        """

        response = client.sendRequest(query, timeout=60)

        print("API Response:")
        print(response)

    except Exception as error:
        print("Error occurred:")
        print(error)
