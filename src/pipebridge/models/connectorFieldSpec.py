from __future__ import annotations

# ============================================================
# Dependencies
# ============================================================
from typing import Optional, List

from pipebridge.models.connectedRepoRef import ConnectedRepoRef
from pipebridge.models.phaseField import PhaseField


class ConnectorFieldSpec:
    """
    Represents a connector field with its schema origin inside a pipe.

    This model is discovery-oriented. It keeps the connector schema flattened
    and explicit, while preserving where the field is configured.

    :param field_id: str = Connector field identifier
    :param label: str | None = Connector field label
    :param type: str | None = Field type, expected to be ``connector``
    :param required: bool = Whether the field is required
    :param description: str | None = Field description
    :param options: list[str] = Raw options payload when present
    :param uuid: str | None = Field UUID
    :param internal_id: str | None = Field internal identifier
    :param connected_repo: ConnectedRepoRef | None = Connected repo metadata
    :param can_connect_existing: bool | None = Connector capability flag
    :param can_connect_multiples: bool | None = Connector multiplicity flag
    :param can_create_new_connected: bool | None = Connector creation flag
    :param help_text: str | None = Optional help text
    :param settings: str | None = Raw field settings payload
    :param origin_type: str = ``start_form`` or ``phase``
    :param phase_id: str | None = Parent phase identifier when origin is phase
    :param phase_name: str | None = Parent phase name when origin is phase
    """

    def __init__(
        self,
        field_id: str,
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
        settings: Optional[str] = None,
        origin_type: str = "start_form",
        phase_id: Optional[str] = None,
        phase_name: Optional[str] = None,
    ) -> None:
        self.field_id: str = field_id
        self.label: Optional[str] = label
        self.type: Optional[str] = type
        self.required: bool = required
        self.description: Optional[str] = description
        self.options: List[str] = list(options or [])
        self.uuid: Optional[str] = uuid
        self.internal_id: Optional[str] = internal_id
        self.connected_repo: Optional[ConnectedRepoRef] = connected_repo
        self.can_connect_existing: Optional[bool] = can_connect_existing
        self.can_connect_multiples: Optional[bool] = can_connect_multiples
        self.can_create_new_connected: Optional[bool] = can_create_new_connected
        self.help_text: Optional[str] = help_text
        self.settings: Optional[str] = settings
        self.origin_type: str = origin_type
        self.phase_id: Optional[str] = phase_id
        self.phase_name: Optional[str] = phase_name

    @classmethod
    def fromPhaseField(
        cls,
        field: PhaseField,
        origin_type: str,
        phase_id: Optional[str] = None,
        phase_name: Optional[str] = None,
    ) -> "ConnectorFieldSpec":
        """
        Build a discovery spec from an existing phase/start-form field.

        :param field: PhaseField = Connector field schema
        :param origin_type: str = ``start_form`` or ``phase``
        :param phase_id: str | None = Parent phase identifier
        :param phase_name: str | None = Parent phase name

        :return: ConnectorFieldSpec = Discovery-oriented connector schema
        """
        return cls(
            field_id=field.id,
            label=field.label,
            type=field.type,
            required=field.required,
            description=field.description,
            options=list(field.options or []),
            uuid=field.uuid,
            internal_id=field.internal_id,
            connected_repo=field.connected_repo,
            can_connect_existing=field.can_connect_existing,
            can_connect_multiples=field.can_connect_multiples,
            can_create_new_connected=field.can_create_new_connected,
            help_text=field.help_text,
            settings=field.settings,
            origin_type=origin_type,
            phase_id=phase_id,
            phase_name=phase_name,
        )

    def isStartForm(self) -> bool:
        """
        Check whether the connector belongs to the start form.

        :return: bool = Whether the origin is start form
        """
        return self.origin_type == "start_form"

    def isPhaseField(self) -> bool:
        """
        Check whether the connector belongs to a phase schema.

        :return: bool = Whether the origin is phase
        """
        return self.origin_type == "phase"
