# ============================================================
# Dependencies
# ============================================================
from typing import Any, Dict, Optional

from pipebridge.exceptions import RequestError


class ConnectedRepoItem:
    """
    Represents a connected card or table record materialized in a connector field.

    :param item_type: str | None = Raw GraphQL typename of the connected item
    :param id: str | None = Connected item identifier
    :param title: str | None = Connected item title
    :param path: str | None = Relative Pipefy path
    :param url: str | None = Absolute Pipefy URL
    :param uuid: str | None = Connected item UUID
    """

    def __init__(
        self,
        item_type: Optional[str] = None,
        id: Optional[str] = None,
        title: Optional[str] = None,
        path: Optional[str] = None,
        url: Optional[str] = None,
        uuid: Optional[str] = None,
    ) -> None:
        self.item_type: Optional[str] = item_type
        self.id: Optional[str] = id
        self.title: Optional[str] = title
        self.path: Optional[str] = path
        self.url: Optional[str] = url
        self.uuid: Optional[str] = uuid

    @classmethod
    def fromDict(cls, data: Dict[str, Any]) -> "ConnectedRepoItem":
        """
        Safely parse a connected repo item from API data.

        :param data: dict = Raw connected item payload

        :return: ConnectedRepoItem = Parsed connected item

        :raises RequestError:
            When parsing fails
        """
        try:
            if not isinstance(data, dict):
                raise ValueError("Invalid connected repo item data")

            item_id = data.get("id")
            title = data.get("title")
            path = data.get("path")
            url = data.get("url")
            uuid = data.get("uuid")

            return cls(
                item_type=(
                    str(data.get("__typename")) if data.get("__typename") else None
                ),
                id=str(item_id) if item_id is not None else None,
                title=str(title) if title is not None else None,
                path=str(path) if path is not None else None,
                url=str(url) if url is not None else None,
                uuid=str(uuid) if uuid is not None else None,
            )

        except Exception as exc:
            raise RequestError(
                f"Class: {cls.__name__}\n" f"Method: fromDict\n" f"Error: {str(exc)}"
            ) from exc
