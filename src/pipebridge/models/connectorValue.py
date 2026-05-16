# ============================================================
# Dependencies
# ============================================================
from typing import Any, List, Optional

from pipebridge.models.connectedRepoItem import ConnectedRepoItem


class ConnectorValue:
    """
    Represents the structured value of a connector field materialized in a card.

    :param field_id: str = Connector field identifier
    :param item_ids: list[str] = Connected repo item identifiers
    :param items: list[ConnectedRepoItem] = Connected repo item metadata
    :param raw_value: Any = Raw `value` returned by Pipefy
    :param report_value: Any = `report_value` returned by Pipefy
    :param native_value: Any = `native_value` returned by Pipefy
    """

    def __init__(
        self,
        field_id: str,
        item_ids: Optional[List[str]] = None,
        items: Optional[List[ConnectedRepoItem]] = None,
        raw_value: Any = None,
        report_value: Any = None,
        native_value: Any = None,
    ) -> None:
        self.field_id: str = field_id
        self.item_ids: List[str] = list(item_ids or [])
        self.items: List[ConnectedRepoItem] = list(items or [])
        self.raw_value: Any = raw_value
        self.report_value: Any = report_value
        self.native_value: Any = native_value
