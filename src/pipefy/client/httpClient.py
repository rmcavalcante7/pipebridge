# ============================================================
# Dependencies
# ============================================================
import inspect
from typing import Any, Dict, Optional

import requests

from pipefy.exceptions import (
    RequestError,
    ValidationError,
    AuthenticationError,
    InvalidTokenError,
    UnexpectedResponseError,
    MissingBaseUrlError, UnauthorizedError

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
        >>> client = PipefyHttpClient("valid_token")
        >>> isinstance(client, PipefyHttpClient)
        True
    """

    def __init__(self, auth_key: str, base_url: str) -> None:
        class_name, method_name = self._getContext()

        if not auth_key or not isinstance(auth_key, str):
            raise ValidationError(
                message="auth_key must be a non-empty string",
                class_name=class_name,
                method_name=method_name
            )

        if not base_url or not isinstance(base_url, str):

            raise MissingBaseUrlError(
                message="base_url must be a non-empty string",
                class_name=class_name,
                method_name=method_name
            )

        self._base_url: str = base_url

        self._headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {auth_key}"
        }

    # ============================================================
    # Public Methods
    # ============================================================
    def sendRequest(
        self,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
        timeout: int = 30
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

        :raises RequestError:
            If HTTP request fails

        :raises AuthenticationError:
            If authentication fails

        :raises UnexpectedResponseError:
            If response format is invalid

        :example:
            >>> client = PipefyHttpClient("valid_token")
            >>> query = "{ me { id } }"
            >>> isinstance(query, str)
            True
        """
        class_name, method_name = self._getContext()

        if not query or not isinstance(query, str):
            raise ValidationError(
                message="query must be a non-empty string",
                class_name=class_name,
                method_name=method_name
            )

        payload: Dict[str, Any] = {"query": query}

        if variables:
            payload["variables"] = variables

        try:
            response = requests.post(
                self._base_url,
                json=payload,
                headers=self._headers,
                timeout=timeout
            )
        except requests.RequestException as exc:
            raise RequestError(
                message=str(exc),
                class_name=class_name,
                method_name=method_name
            ) from exc

        json_response: Dict[str, Any] = self._parseResponse(response)

        self._validateResponseStructure(json_response)

        self._handleErrors(json_response)

        return json_response

    # ============================================================
    # Helper Methods
    # ============================================================
    def _parseResponse(self, response: requests.Response) -> Dict[str, Any]:
        """
        Parses HTTP response to JSON.

        :param response: requests.Response = HTTP response object
        :return: dict = Parsed JSON response

        :raises UnexpectedResponseError:
            If response is not valid JSON
        """
        class_name, method_name = self._getContext()

        try:
            return response.json()
        except ValueError as exc:
            raise UnexpectedResponseError(
                message="Response is not valid JSON",
                class_name=class_name,
                method_name=method_name
            ) from exc

    def _validateResponseStructure(self, response: Dict[str, Any]) -> None:
        """
        Validates minimal GraphQL response structure.

        :param response: dict = Parsed JSON response

        :raises UnexpectedResponseError:
            If response structure is invalid
        """
        class_name, method_name = self._getContext()

        if not isinstance(response, dict):
            raise UnexpectedResponseError(
                message="Response must be a dictionary",
                class_name=class_name,
                method_name=method_name
            )

        if "data" not in response and "error" not in response and "errors" not in response:
            raise UnexpectedResponseError(
                message="Response must contain 'data' or 'errors'",
                class_name=class_name,
                method_name=method_name
            )

    def _handleErrors(self, response: Dict[str, Any]) -> None:
        """
        Handles GraphQL and HTTP-level errors.

        :param response: dict = Parsed JSON response

        :raises AuthenticationError:
            When authentication fails

        :raises RequestError:
            For generic API errors
        """
        class_name, method_name = self._getContext()

        if "error" not in response and "errors" not in response:
            return

        error_content = ''
        if "error" in response:
            error_content = response["error"]
        elif "errors" in response:
            error_content = response["errors"]

        message = str(error_content)

        lowered = message.lower()

        if "invalid token" in lowered or "invalid_token" in lowered:
            raise InvalidTokenError(
                message=message,
                class_name=class_name,
                method_name=method_name
            )

        if "unauthorized" in lowered:
            raise AuthenticationError(
                message=message,
                class_name=class_name,
                method_name=method_name
            )

        if "permission_denied" in lowered:
            raise UnauthorizedError(
                message=message,
                class_name=class_name,
                method_name=method_name
            )

        raise RequestError(
            message=message,
            class_name=class_name,
            method_name=method_name
        )

    def _getContext(self) -> tuple[str, str]:
        """
        Retrieves class and method context for exception messages.

        :return: tuple[str, str] = (class_name, method_name)
        """
        return (
            self.__class__.__name__,
            inspect.currentframe().f_back.f_code.co_name  # type: ignore
        )


# ============================================================
# Main (Usage Example)
# ============================================================
if __name__ == "__main__":
    TOKEN = ""

    try:
        client = PipefyHttpClient(TOKEN, base_url="https://accenture.pipefy.com/queries")

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