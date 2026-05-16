from __future__ import annotations

# ============================================================
# Dependencies
# ============================================================
from typing import Any, Dict, List, Optional

from pipebridge.exceptions import RequestError


class ConnectorOption:
    """
    Represents a dynamic option that can be connected by a connector field.

    :param id: str = Connected item identifier
    :param title: str | None = Connected item title
    :param repo_type: str = ``Pipe`` or ``Table``
    :param repo_id: str = Connected repo identifier
    :param repo_name: str | None = Connected repo display name
    :param item_type: str | None = Connected item typename or normalized type
    :param current_phase_id: str | None = Current phase identifier for pipe items
    :param current_phase_name: str | None = Current phase name for pipe items
    :param path: str | None = Relative Pipefy path when available
    :param url: str | None = Absolute Pipefy URL when available
    :param uuid: str | None = Item UUID when available
    :param record_fields: list[dict] = Table record fields when the option is
        backed by a connected table
    """

    def __init__(
        self,
        id: str,
        title: Optional[str],
        repo_type: str,
        repo_id: str,
        repo_name: Optional[str] = None,
        item_type: Optional[str] = None,
        current_phase_id: Optional[str] = None,
        current_phase_name: Optional[str] = None,
        path: Optional[str] = None,
        url: Optional[str] = None,
        uuid: Optional[str] = None,
        record_fields: Optional[List[Dict[str, Optional[str]]]] = None,
    ) -> None:
        self.id: str = id
        self.title: Optional[str] = title
        self.repo_type: str = repo_type
        self.repo_id: str = repo_id
        self.repo_name: Optional[str] = repo_name
        self.item_type: Optional[str] = item_type
        self.current_phase_id: Optional[str] = current_phase_id
        self.current_phase_name: Optional[str] = current_phase_name
        self.path: Optional[str] = path
        self.url: Optional[str] = url
        self.uuid: Optional[str] = uuid
        self.record_fields: List[Dict[str, Optional[str]]] = (
            list(record_fields) if record_fields else []
        )
        self.record_fields_map: Dict[str, Optional[str]] = {
            str(field.get("name")): field.get("value")
            for field in self.record_fields
            if field.get("name") is not None
        }

    @classmethod
    def fromPipeCardNode(
        cls,
        data: Dict[str, Any],
        repo_id: str,
        repo_name: Optional[str] = None,
    ) -> "ConnectorOption":
        """
        Parse a pipe-backed connector option from a card node payload.

        :param data: dict = Card node payload
        :param repo_id: str = Connected pipe identifier
        :param repo_name: str | None = Connected pipe name

        :return: ConnectorOption = Parsed connector option
        """
        try:
            if not isinstance(data, dict):
                raise ValueError("Invalid pipe connector option data")

            current_phase = data.get("current_phase") or {}
            if not isinstance(current_phase, dict):
                current_phase = {}

            item_id = data.get("id")
            if item_id is None:
                raise ValueError("Connector option is missing id")

            return cls(
                id=str(item_id),
                title=(
                    str(data.get("title")) if data.get("title") is not None else None
                ),
                repo_type="Pipe",
                repo_id=repo_id,
                repo_name=repo_name,
                item_type=str(data.get("__typename") or "Card"),
                current_phase_id=(
                    str(current_phase.get("id"))
                    if current_phase.get("id") is not None
                    else None
                ),
                current_phase_name=(
                    str(current_phase.get("name"))
                    if current_phase.get("name") is not None
                    else None
                ),
                path=str(data.get("path")) if data.get("path") is not None else None,
                url=str(data.get("url")) if data.get("url") is not None else None,
                uuid=str(data.get("uuid")) if data.get("uuid") is not None else None,
            )

        except Exception as exc:
            raise RequestError(
                f"Class: {cls.__name__}\n"
                f"Method: fromPipeCardNode\n"
                f"Error: {str(exc)}"
            ) from exc

    @classmethod
    def fromTableRecordNode(
        cls,
        data: Dict[str, Any],
        repo_id: str,
        repo_name: Optional[str] = None,
    ) -> "ConnectorOption":
        """
        Parse a table-backed connector option from a table record node payload.

        :param data: dict = Table record node payload
        :param repo_id: str = Connected table identifier
        :param repo_name: str | None = Connected table name

        :return: ConnectorOption = Parsed connector option
        """
        try:
            if not isinstance(data, dict):
                raise ValueError("Invalid table connector option data")

            item_id = data.get("id")
            if item_id is None:
                raise ValueError("Connector option is missing id")

            record_fields_data = data.get("record_fields") or []
            if not isinstance(record_fields_data, list):
                record_fields_data = []

            record_fields: List[Dict[str, Optional[str]]] = []
            for field in record_fields_data:
                if not isinstance(field, dict):
                    continue
                record_fields.append(
                    {
                        "index_name": (
                            str(field.get("indexName"))
                            if field.get("indexName") is not None
                            else None
                        ),
                        "name": (
                            str(field.get("name"))
                            if field.get("name") is not None
                            else None
                        ),
                        "value": (
                            str(field.get("value"))
                            if field.get("value") is not None
                            else None
                        ),
                    }
                )

            return cls(
                id=str(item_id),
                title=(
                    str(data.get("title")) if data.get("title") is not None else None
                ),
                repo_type="Table",
                repo_id=repo_id,
                repo_name=repo_name,
                item_type=str(data.get("__typename") or "TableRecord"),
                path=str(data.get("path")) if data.get("path") is not None else None,
                url=str(data.get("url")) if data.get("url") is not None else None,
                uuid=str(data.get("uuid")) if data.get("uuid") is not None else None,
                record_fields=record_fields,
            )

        except Exception as exc:
            raise RequestError(
                f"Class: {cls.__name__}\n"
                f"Method: fromTableRecordNode\n"
                f"Error: {str(exc)}"
            ) from exc

    def matchesTitle(self, title: str) -> bool:
        """
        Check whether the option title matches a desired title exactly,
        ignoring case and surrounding whitespace.

        :param title: str = Desired title

        :return: bool = Whether the titles match
        """
        desired = str(title or "").strip().casefold()
        candidate = str(self.title or "").strip().casefold()
        return bool(desired) and candidate == desired

    def getRecordField(self, name: str) -> Optional[str]:
        """
        Retrieve a connected table record field value by display name.

        :param name: str = Record field display name

        :return: str | None = Matching field value when available
        """
        lookup_name = str(name or "").strip()
        if not lookup_name:
            return None
        return self.record_fields_map.get(lookup_name)

    def hasRecordField(self, name: str) -> bool:
        """
        Check whether a connected table record exposes a named field.

        :param name: str = Record field display name

        :return: bool = Whether the field exists in the loaded option payload
        """
        return self.getRecordField(name) is not None
