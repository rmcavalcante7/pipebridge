# ============================================================
# Dependencies
# ============================================================
from typing import Any, Dict, Optional

from pipebridge.exceptions import RequestError


class ConnectedRepoRef:
    """
    Represents the repo targeted by a connector field.

    A connector field can point to either a Pipe or a Table. This model keeps
    the public metadata small and normalized for SDK consumers.

    :param repo_type: str | None = Normalized repo type (`Pipe` or `Table`)
    :param id: str | None = Connected repo identifier
    :param name: str | None = Connected repo display name
    """

    def __init__(
        self,
        repo_type: Optional[str] = None,
        id: Optional[str] = None,
        name: Optional[str] = None,
    ) -> None:
        self.repo_type: Optional[str] = repo_type
        self.id: Optional[str] = id
        self.name: Optional[str] = name

    @staticmethod
    def _normalizeRepoType(value: Any) -> Optional[str]:
        """
        Normalize Pipefy repo union names into a stable SDK value.

        :param value: Any = Raw typename or repo type

        :return: str | None = Normalized repo type
        """
        if value is None:
            return None

        raw = str(value).strip()
        if raw in {"PublicPipe", "Pipe"}:
            return "Pipe"
        if raw in {"PublicTable", "Table"}:
            return "Table"
        return raw or None

    @classmethod
    def fromDict(cls, data: Dict[str, Any]) -> "ConnectedRepoRef":
        """
        Safely parse connected repo metadata from API data.

        :param data: dict = Raw connected repo payload

        :return: ConnectedRepoRef = Parsed connected repo metadata

        :raises RequestError:
            When parsing fails
        """
        try:
            if not isinstance(data, dict):
                raise ValueError("Invalid connected repo data")

            repo_type = cls._normalizeRepoType(
                data.get("repo_type") or data.get("__typename")
            )
            repo_id = data.get("id")
            repo_name = data.get("name")

            return cls(
                repo_type=repo_type,
                id=str(repo_id) if repo_id is not None else None,
                name=str(repo_name) if repo_name is not None else None,
            )

        except Exception as exc:
            raise RequestError(
                f"Class: {cls.__name__}\n" f"Method: fromDict\n" f"Error: {str(exc)}"
            ) from exc

    def isPipe(self) -> bool:
        """
        Check whether the connected repo is a Pipe.

        :return: bool = Whether the repo type is Pipe
        """
        return self.repo_type == "Pipe"

    def isTable(self) -> bool:
        """
        Check whether the connected repo is a Table.

        :return: bool = Whether the repo type is Table
        """
        return self.repo_type == "Table"
