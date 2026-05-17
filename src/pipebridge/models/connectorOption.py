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
    :param internal_id: str | None = Internal numeric id for pipe-backed cards
    :param path: str | None = Relative Pipefy path when available
    :param url: str | None = Absolute Pipefy URL when available
    :param uuid: str | None = GraphQL/global id when available
    :param summary_attributes: list[dict] = Summary attributes for pipe-backed
        options
    :param summary_fields: list[dict] = Summary fields for pipe-backed options
    :param pipe_icon: str | None = Pipe icon for pipe-backed options
    :param pipe_color: str | None = Pipe color for pipe-backed options
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
        internal_id: Optional[str] = None,
        path: Optional[str] = None,
        url: Optional[str] = None,
        uuid: Optional[str] = None,
        summary_attributes: Optional[List[Dict[str, Optional[str]]]] = None,
        summary_fields: Optional[List[Dict[str, Optional[str]]]] = None,
        pipe_icon: Optional[str] = None,
        pipe_color: Optional[str] = None,
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
        self.internal_id: Optional[str] = internal_id
        self.path: Optional[str] = path
        self.url: Optional[str] = url
        self.uuid: Optional[str] = uuid
        self.summary_attributes: List[Dict[str, Optional[str]]] = (
            list(summary_attributes) if summary_attributes else []
        )
        self.summary_fields: List[Dict[str, Optional[str]]] = (
            list(summary_fields) if summary_fields else []
        )
        self.pipe_icon: Optional[str] = pipe_icon
        self.pipe_color: Optional[str] = pipe_color
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
        """
        try:
            if not isinstance(data, dict):
                raise ValueError("Invalid pipe connector option data")

            current_phase = data.get("currentPhase") or data.get("current_phase") or {}
            if not isinstance(current_phase, dict):
                current_phase = {}

            graph_id = (
                data.get("uuid") if data.get("uuid") is not None else data.get("id")
            )
            internal_id = data.get("internalId")
            item_id = internal_id if internal_id is not None else data.get("id")
            if item_id is None and graph_id is None:
                raise ValueError("Connector option is missing id")

            summary_attributes = cls._normalizeSummaryAttributes(
                data.get("summary_attributes") or []
            )
            summary_fields = cls._normalizeSummaryFields(
                data.get("summary_fields") or []
            )

            pipe_data = data.get("pipe") or {}
            if not isinstance(pipe_data, dict):
                pipe_data = {}

            return cls.fromContextualNode(
                data=data,
                repo_type="Pipe",
                repo_id=repo_id,
                repo_name=repo_name,
                default_item_type="Card",
            )

        except Exception as exc:
            raise RequestError(
                f"Class: {cls.__name__}\n"
                f"Method: fromPipeCardNode\n"
                f"Error: {str(exc)}"
            ) from exc

    @classmethod
    def fromContextualNode(
        cls,
        data: Dict[str, Any],
        repo_type: str,
        repo_id: str,
        repo_name: Optional[str] = None,
        default_item_type: Optional[str] = None,
    ) -> "ConnectorOption":
        """
        Parse a contextual connector option returned by the `cards(...)`
        resolver with `throughConnectors`.
        """
        try:
            if not isinstance(data, dict):
                raise ValueError("Invalid contextual connector option data")

            current_phase = data.get("currentPhase") or data.get("current_phase") or {}
            if not isinstance(current_phase, dict):
                current_phase = {}

            graph_id = (
                data.get("uuid") if data.get("uuid") is not None else data.get("id")
            )
            internal_id = data.get("internalId")
            item_id = internal_id if internal_id is not None else data.get("id")
            if item_id is None and graph_id is None:
                raise ValueError("Connector option is missing id")

            summary_attributes = cls._normalizeSummaryAttributes(
                data.get("summary_attributes") or []
            )
            summary_fields = cls._normalizeSummaryFields(
                data.get("summary_fields") or []
            )

            pipe_data = data.get("pipe") or {}
            if not isinstance(pipe_data, dict):
                pipe_data = {}

            return cls(
                id=str(item_id if item_id is not None else graph_id),
                title=(
                    str(data.get("title")) if data.get("title") is not None else None
                ),
                repo_type=repo_type,
                repo_id=repo_id,
                repo_name=repo_name,
                item_type=str(data.get("__typename") or default_item_type or "Record"),
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
                internal_id=str(internal_id) if internal_id is not None else None,
                path=str(data.get("path")) if data.get("path") is not None else None,
                url=str(data.get("url")) if data.get("url") is not None else None,
                uuid=str(graph_id) if graph_id is not None else None,
                summary_attributes=summary_attributes,
                summary_fields=summary_fields,
                pipe_icon=(
                    str(pipe_data.get("icon"))
                    if pipe_data.get("icon") is not None
                    else None
                ),
                pipe_color=(
                    str(pipe_data.get("color"))
                    if pipe_data.get("color") is not None
                    else None
                ),
            )

        except Exception as exc:
            raise RequestError(
                f"Class: {cls.__name__}\n"
                f"Method: fromContextualNode\n"
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
        """
        desired = str(title or "").strip().casefold()
        candidate = str(self.title or "").strip().casefold()
        return bool(desired) and candidate == desired

    def getRecordField(self, name: str) -> Optional[str]:
        """
        Retrieve a connected table record field value by display name.
        """
        lookup_name = str(name or "").strip()
        if not lookup_name:
            return None
        return self.record_fields_map.get(lookup_name)

    def hasRecordField(self, name: str) -> bool:
        """
        Check whether a connected table record exposes a named field.
        """
        return self.getRecordField(name) is not None

    @staticmethod
    def _normalizeSummaryAttributes(
        items: List[Any],
    ) -> List[Dict[str, Optional[str]]]:
        normalized: List[Dict[str, Optional[str]]] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            normalized.append(
                {
                    "title": (
                        str(item.get("title"))
                        if item.get("title") is not None
                        else None
                    ),
                    "value": (
                        str(item.get("value"))
                        if item.get("value") is not None
                        else None
                    ),
                }
            )
        return normalized

    @staticmethod
    def _normalizeSummaryFields(
        items: List[Any],
    ) -> List[Dict[str, Optional[str]]]:
        normalized: List[Dict[str, Optional[str]]] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            normalized.append(
                {
                    "title": (
                        str(item.get("title"))
                        if item.get("title") is not None
                        else None
                    ),
                    "value": (
                        str(item.get("value"))
                        if item.get("value") is not None
                        else None
                    ),
                    "type": (
                        str(item.get("type")) if item.get("type") is not None else None
                    ),
                    "settings": (
                        str(item.get("settings"))
                        if item.get("settings") is not None
                        else None
                    ),
                }
            )
        return normalized
