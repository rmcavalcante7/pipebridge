# ============================================================
# Dependencies
# ============================================================
from typing import Optional, Dict, Any, List

from pipebridge.exceptions import RequestError
from pipebridge.models.connectedRepoRef import ConnectedRepoRef


class PhaseField:
    """
    Represents a Phase field schema.

    This model encapsulates metadata about a field within a Phase,
    including validation rules and descriptive attributes.

    :param id: str = Field identifier
    :param label: str | None = Field label
    :param type: str | None = Field type
    :param required: bool = Whether field is required
    :param description: str | None = Field description
    :param uuid: str | None = Field UUID exposed by the API
    :param internal_id: str | None = Field internal identifier exposed by the API
    :param connected_repo: ConnectedRepoRef | None = Target repo metadata for connector fields
    :param can_connect_existing: bool | None = Whether existing items can be connected
    :param can_connect_multiples: bool | None = Whether multiple items can be connected
    :param can_create_new_connected: bool | None = Whether new connected items can be created
    :param help_text: str | None = Optional help text exposed by the API
    """

    def __init__(
        self,
        id: str,
        label: Optional[str] = None,
        type: Optional[str] = None,
        required: bool = False,
        description: Optional[str] = None,
        options: Optional[List[str]] = None,
        uuid: Optional[str] = None,
        internal_id: Optional[str] = None,
        connected_repo: Optional[ConnectedRepoRef] = None,
        can_connect_existing: Optional[bool] = None,
        can_connect_multiples: Optional[bool] = None,
        can_create_new_connected: Optional[bool] = None,
        help_text: Optional[str] = None,
    ) -> None:
        """
        Initialize phase field schema metadata.

        :param id: str = Field identifier
        :param label: str | None = Field label
        :param type: str | None = Pipefy field type
        :param required: bool = Whether the field is required in the phase
        :param description: str | None = Field description
        :param options: list[str] | None = Configured field options
        :param uuid: str | None = Field UUID exposed by the API
        :param internal_id: str | None = Field internal identifier exposed by the API
        :param connected_repo: ConnectedRepoRef | None = Target repo metadata
        :param can_connect_existing: bool | None = Connector capability flag
        :param can_connect_multiples: bool | None = Connector multiplicity flag
        :param can_create_new_connected: bool | None = Connector creation flag
        :param help_text: str | None = API help text
        """
        self.id: str = id
        self.label: Optional[str] = label
        self.type: Optional[str] = type
        self.required: bool = required
        self.description: Optional[str] = description
        self.options: List[str] = options or []
        self.uuid: Optional[str] = uuid
        self.internal_id: Optional[str] = internal_id
        self.connected_repo: Optional[ConnectedRepoRef] = connected_repo
        self.can_connect_existing: Optional[bool] = can_connect_existing
        self.can_connect_multiples: Optional[bool] = can_connect_multiples
        self.can_create_new_connected: Optional[bool] = can_create_new_connected
        self.help_text: Optional[str] = help_text

    # ============================================================
    # Factory Methods
    # ============================================================

    @classmethod
    def fromDict(cls, data: Dict[str, Any]) -> "PhaseField":
        """
        Safely parse a PhaseField from a dictionary.

        :param data: dict = Raw field data from API

        :return: PhaseField = Parsed PhaseField instance

        :raises RequestError:
            When parsing fails due to invalid structure or types

        :example:
            >>> field = PhaseField.fromDict({"id": "1"})
            >>> isinstance(field, PhaseField)
            True
        """
        try:
            if not isinstance(data, dict):
                raise ValueError("Invalid field data")

            raw_connected_repo = data.get("connected_repo") or data.get("connectedRepo")
            connected_repo = None
            if isinstance(raw_connected_repo, dict) and raw_connected_repo:
                connected_repo = ConnectedRepoRef.fromDict(raw_connected_repo)

            return cls(
                id=str(data.get("id", "")),
                label=data.get("label"),
                type=data.get("type"),
                required=bool(data.get("required", False)),
                description=data.get("description"),
                options=data.get("options", []),
                uuid=data.get("uuid"),
                internal_id=data.get("internal_id"),
                connected_repo=connected_repo,
                can_connect_existing=cls._getOptionalBool(
                    data, "can_connect_existing", "canConnectExisting"
                ),
                can_connect_multiples=cls._getOptionalBool(
                    data, "can_connect_multiples", "canConnectMultiples"
                ),
                can_create_new_connected=cls._getOptionalBool(
                    data,
                    "can_create_new_connected",
                    "canCreateNewConnected",
                ),
                help_text=(
                    data.get("help_text") or data.get("help") or data.get("helpText")
                ),
            )

        except Exception as exc:
            raise RequestError(
                f"Class: {cls.__name__}\n" f"Method: fromDict\n" f"Error: {str(exc)}"
            ) from exc

    @staticmethod
    def _getOptionalBool(data: Dict[str, Any], *keys: str) -> Optional[bool]:
        """
        Retrieve an optional boolean value from multiple compatible keys.

        :param data: dict = Raw field data
        :param keys: str = Candidate keys

        :return: bool | None = Parsed optional boolean
        """
        for key in keys:
            if key in data:
                value = data.get(key)
                if value is None:
                    return None
                return bool(value)
        return None

    def isConnector(self) -> bool:
        """
        Check whether this field is a connector field.

        :return: bool = Whether the field type is connector
        """
        return self.type == "connector"
