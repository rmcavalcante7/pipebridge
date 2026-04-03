# ============================================================
# Dependencies
# ============================================================
import inspect
from typing import Any, Dict

from pipefy.client.httpClient import PipefyHttpClient
from pipefy.exceptions import RequestError
from pipefy.models.pipe import Pipe


class PipeService:
    """
    Service responsible for pipe operations in Pipefy.

    This service provides access to:
    - Pipe metadata
    - Labels
    - Users
    - Phases

    It acts as a domain layer over the GraphQL API.

    :example:
        >>> client = PipefyHttpClient("token")
        >>> service = PipeService(client)
        >>> isinstance(service, PipeService)
        True
    """

    def __init__(self, client: PipefyHttpClient) -> None:
        """
        Initialize PipeService.

        :param client: PipefyHttpClient = HTTP client instance

        :example:
            >>> client = PipefyHttpClient("token")
            >>> service = PipeService(client)
        """
        self._client: PipefyHttpClient = client

    # ============================================================
    # Pipe Info
    # ============================================================

    def getPipeInfo(self, pipe_id: str) -> Dict[str, Any]:
        """
        Retrieve basic information about a pipe.

        :param pipe_id: str = Pipe ID

        :return: dict = Pipe data

        :raises RequestError:
            When request fails

        :example:
            >>> service = PipeService(PipefyHttpClient("token"))
            >>> isinstance(service.getPipeInfo("1"), dict)
            True
        """
        try:
            query = f"""
            {{
                pipe(id: {pipe_id}) {{
                    id
                    name
                    cards_count
                }}
            }}
            """
            return self._client.sendRequest(query, timeout=60)

        except Exception as exc:
            raise RequestError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: getPipeInfo\n"
                f"Error: {str(exc)}"
            ) from exc

    # ============================================================
    # Labels
    # ============================================================

    def getPipeLabels(self, pipe_id: str) -> Dict[str, Any]:
        """
        Retrieve labels associated with a pipe.

        :param pipe_id: str = Pipe ID

        :return: dict = Labels data

        :raises RequestError:
            When request fails

        :example:
            >>> service = PipeService(PipefyHttpClient("token"))
            >>> isinstance(service.getPipeLabels("1"), dict)
            True
        """
        try:
            query = f"""
            {{
                pipe(id: {pipe_id}) {{
                    labels {{
                        id
                        name
                        color
                    }}
                }}
            }}
            """
            return self._client.sendRequest(query, timeout=60)

        except Exception as exc:
            raise RequestError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: getPipeLabels\n"
                f"Error: {str(exc)}"
            ) from exc

    # ============================================================
    # Users
    # ============================================================

    def getPipeUsers(self, pipe_id: str) -> Dict[str, Any]:
        """
        Retrieve users associated with a pipe.

        :param pipe_id: str = Pipe ID

        :return: dict = Users data

        :raises RequestError:
            When request fails

        :example:
            >>> service = PipeService(PipefyHttpClient("token"))
            >>> isinstance(service.getPipeUsers("1"), dict)
            True
        """
        try:
            query = f"""
            {{
                pipe(id: {pipe_id}) {{
                    users {{
                        id
                        name
                        email
                    }}
                }}
            }}
            """
            return self._client.sendRequest(query, timeout=60)

        except Exception as exc:
            raise RequestError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: getPipeUsers\n"
                f"Error: {str(exc)}"
            ) from exc

    # ============================================================
    # Phases
    # ============================================================

    def getPipePhases(self, pipe_id: str) -> Dict[str, Any]:
        """
        Retrieve phases of a pipe.

        :param pipe_id: str = Pipe ID

        :return: dict = Phases data

        :raises RequestError:
            When request fails

        :example:
            >>> service = PipeService(PipefyHttpClient("token"))
            >>> isinstance(service.getPipePhases("1"), dict)
            True
        """
        try:
            query = f"""
            {{
                pipe(id: {pipe_id}) {{
                    phases {{
                        id
                        name
                    }}
                }}
            }}
            """
            return self._client.sendRequest(query, timeout=60)

        except Exception as exc:
            raise RequestError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: getPipePhases\n"
                f"Error: {str(exc)}"
            ) from exc

    def getPipeModel(self, pipe_id: str) -> Pipe:
        """
        Retrieve pipe as model.

        :return: Pipe
        """
        response = self.getPipeInfo(pipe_id)
        return Pipe.fromResponse(response)

# ============================================================
# Main (Usage Example)
# ============================================================

if __name__ == "__main__":
    """
    Simple execution example.
    """

    try:
        TOKEN = ""
        client = PipefyHttpClient(TOKEN)
        service = PipeService(client)

        result = service.getPipeInfo("11881")

        print("Pipe info:")
        print(result)

    except Exception as error:
        print("Error occurred:")
        print(error)