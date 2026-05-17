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
    :param internal_id: str | None = Internal repo identifier when exposed
    :param uuid: str | None = Repo UUID when exposed
    :param name: str | None = Connected repo display name
    """

    def __init__(
        self,
        repo_type: Optional[str] = None,
        id: Optional[str] = None,
        internal_id: Optional[str] = None,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
    ) -> None:
        self.repo_type: Optional[str] = repo_type
        self.id: Optional[str] = id
        self.internal_id: Optional[str] = internal_id
        self.uuid: Optional[str] = uuid
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
            repo_internal_id = data.get("internal_id")
            repo_uuid = data.get("uuid")
            repo_name = data.get("name")

            return cls(
                repo_type=repo_type,
                id=str(repo_id) if repo_id is not None else None,
                internal_id=(
                    str(repo_internal_id) if repo_internal_id is not None else None
                ),
                uuid=str(repo_uuid) if repo_uuid is not None else None,
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

    def getDiscoveryRepoId(self) -> Optional[str]:
        """
        Resolve the repo identifier used by contextual connector discovery.

        Pipefy may require the public repo id for pipe-backed connectors and
        the internal numeric id for table-backed connectors. This helper
        centralizes that decision for connector discovery strategies.
        """
        return self.internal_id or self.id
