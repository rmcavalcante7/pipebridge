from __future__ import annotations

# ============================================================
# Dependencies
# ============================================================
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from pipebridge.client.httpClient import PipefyHttpClient
from pipebridge.exceptions import (
    PipefyError,
    RequestError,
    UnexpectedResponseError,
    ValidationError,
    getExceptionContext,
)
from pipebridge.models.connectorValue import ConnectorValue
from pipebridge.models.connectedRepoRef import ConnectedRepoRef
from pipebridge.models.connectorFieldSpec import ConnectorFieldSpec
from pipebridge.models.connectorOption import ConnectorOption
from pipebridge.models.phaseField import PhaseField
from pipebridge.service.card.flows.update.cardUpdateConfig import CardUpdateConfig
from pipebridge.service.pipe.pipeService import PipeService

if TYPE_CHECKING:
    from pipebridge.service.card.cardService import CardService


class ConnectorService:
    """
    Service responsible for semantic connector discovery.

    This service exposes connector-aware schema inspection and dynamic option
    discovery without requiring consumers to write raw GraphQL.
    """

    def __init__(
        self,
        client: PipefyHttpClient,
        pipe_service: Optional[PipeService] = None,
        card_service: Optional["CardService"] = None,
    ) -> None:
        self._client: PipefyHttpClient = client
        self._pipe_service: PipeService = pipe_service or PipeService(client)
        self._card_service: Optional["CardService"] = card_service

    def listFields(self, pipe_id: str) -> List[ConnectorFieldSpec]:
        """
        Retrieve all connector fields configured in a pipe.

        :param pipe_id: str = Pipe identifier

        :return: list[ConnectorFieldSpec] = Connector fields with origin metadata
        """
        class_name, method_name = getExceptionContext(self)
        self._validatePipeId(pipe_id, class_name, method_name)

        pipe = self._pipe_service.getPipeFieldCatalog(pipe_id)

        fields: List[ConnectorFieldSpec] = [
            ConnectorFieldSpec.fromPhaseField(field, origin_type="start_form")
            for field in pipe.iterStartFormConnectorFields()
        ]

        for phase in pipe.iterPhases():
            fields.extend(
                [
                    ConnectorFieldSpec.fromPhaseField(
                        field,
                        origin_type="phase",
                        phase_id=phase.id,
                        phase_name=phase.name,
                    )
                    for field in phase.getConnectorFields()
                ]
            )

        return fields

    def getField(
        self,
        pipe_id: str,
        field_id: str,
        phase_id: Optional[str] = None,
    ) -> Optional[ConnectorFieldSpec]:
        """
        Retrieve a connector field specification from a pipe.

        :param pipe_id: str = Pipe identifier
        :param field_id: str = Connector field identifier
        :param phase_id: str | None = Optional parent phase identifier

        :return: ConnectorFieldSpec | None = Matching connector field when found
        """
        matches = self._findConnectorFieldMatches(pipe_id, field_id, phase_id)
        if not matches:
            return None
        if len(matches) > 1:
            self._raiseAmbiguousConnectorField(pipe_id, field_id, matches)
        return matches[0]

    def requireField(
        self,
        pipe_id: str,
        field_id: str,
        phase_id: Optional[str] = None,
    ) -> ConnectorFieldSpec:
        """
        Retrieve a connector field specification and fail when it is missing.

        :param pipe_id: str = Pipe identifier
        :param field_id: str = Connector field identifier
        :param phase_id: str | None = Optional parent phase identifier

        :return: ConnectorFieldSpec = Requested connector field
        """
        class_name, method_name = getExceptionContext(self)
        spec = self.getField(pipe_id=pipe_id, field_id=field_id, phase_id=phase_id)
        if spec is None:
            raise RequestError(
                message=(
                    f"Connector field '{field_id}' does not exist in pipe '{pipe_id}'"
                ),
                class_name=class_name,
                method_name=method_name,
            )
        return spec

    def listOptions(
        self,
        pipe_id: str,
        field_id: str,
        phase_id: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 20,
    ) -> List[ConnectorOption]:
        """
        List dynamic options exposed by a connector field.

        :param pipe_id: str = Pipe identifier
        :param field_id: str = Connector field identifier
        :param phase_id: str | None = Optional phase identifier
        :param search: str | None = Optional title filter
        :param limit: int = Maximum number of options to return

        :return: list[ConnectorOption] = Connector options
        """
        class_name, method_name = getExceptionContext(self)
        self._validatePipeId(pipe_id, class_name, method_name)
        self._validateFieldId(field_id, class_name, method_name)
        self._validateLimit(limit, class_name, method_name)

        spec = self.requireField(pipe_id=pipe_id, field_id=field_id, phase_id=phase_id)
        repo = self._requireConnectedRepo(spec, class_name, method_name)

        if repo.isPipe():
            return self._listPipeOptions(repo, search=search, limit=limit)
        if repo.isTable():
            return self._listTableOptions(repo, search=search, limit=limit)

        raise ValidationError(
            message=(
                f"Unsupported connected repo type '{repo.repo_type}' "
                f"for connector field '{field_id}'"
            ),
            class_name=class_name,
            method_name=method_name,
        )

    def resolveOption(
        self,
        pipe_id: str,
        field_id: str,
        title: str,
        phase_id: Optional[str] = None,
    ) -> ConnectorOption:
        """
        Resolve a connector option by exact title.

        Resolution is case-insensitive but exact after trimming. If zero
        matches are found, or more than one exact match exists, a validation
        error is raised.

        :param pipe_id: str = Pipe identifier
        :param field_id: str = Connector field identifier
        :param title: str = Desired connected item title
        :param phase_id: str | None = Optional phase identifier

        :return: ConnectorOption = Unique resolved connector option
        """
        class_name, method_name = getExceptionContext(self)
        self._validatePipeId(pipe_id, class_name, method_name)
        self._validateFieldId(field_id, class_name, method_name)

        normalized_title = str(title or "").strip()
        if not normalized_title:
            raise ValidationError(
                message="title cannot be empty",
                class_name=class_name,
                method_name=method_name,
            )

        spec = self.requireField(pipe_id=pipe_id, field_id=field_id, phase_id=phase_id)
        repo = self._requireConnectedRepo(spec, class_name, method_name)

        if repo.isPipe():
            options = self._listPipeOptionsForResolution(repo, normalized_title)
        elif repo.isTable():
            options = self._listTableOptions(repo, search=None, limit=None)
        else:
            raise ValidationError(
                message=(
                    f"Unsupported connected repo type '{repo.repo_type}' "
                    f"for connector field '{field_id}'"
                ),
                class_name=class_name,
                method_name=method_name,
            )

        exact_matches = [
            option for option in options if option.matchesTitle(normalized_title)
        ]
        if not exact_matches:
            raise ValidationError(
                message=(
                    f"No connector option with title '{normalized_title}' was found "
                    f"for field '{field_id}'"
                ),
                class_name=class_name,
                method_name=method_name,
            )

        if len(exact_matches) > 1:
            raise ValidationError(
                message=(
                    f"Connector title '{normalized_title}' is ambiguous for field "
                    f"'{field_id}'. Matching ids: {[option.id for option in exact_matches]}"
                ),
                class_name=class_name,
                method_name=method_name,
            )

        return exact_matches[0]

    def validateConnectorSelection(
        self,
        field: PhaseField,
        value: Any,
    ) -> List[str]:
        """
        Validate a connector payload against the connector field schema.

        First-phase safe creation semantics require connector values to be
        passed as a list of connected item ids.

        Validation performed:

        - field must be a connector
        - payload must be a list of non-empty ids
        - existing-item connection must be allowed
        - multiplicity must be respected
        - each id must exist in the connected repo referenced by the field

        :param field: PhaseField = Connector field schema
        :param value: Any = Proposed connector payload

        :return: list[str] = Normalized connected item ids
        """
        class_name, method_name = getExceptionContext(self)

        if not isinstance(field, PhaseField):
            raise ValidationError(
                message="field must be a PhaseField instance",
                class_name=class_name,
                method_name=method_name,
            )

        if not field.isConnector():
            raise ValidationError(
                message=f"Field '{field.id}' is not a connector field",
                class_name=class_name,
                method_name=method_name,
            )

        normalized_ids = self._normalizeConnectorIds(
            field_id=field.id,
            value=value,
            class_name=class_name,
            method_name=method_name,
        )

        if not normalized_ids:
            return []

        if field.can_connect_existing is False:
            raise ValidationError(
                message=(
                    f"Connector field '{field.id}' does not allow connecting existing items"
                ),
                class_name=class_name,
                method_name=method_name,
            )

        if field.can_connect_multiples is False and len(normalized_ids) > 1:
            raise ValidationError(
                message=(
                    f"Connector field '{field.id}' does not allow multiple connected ids"
                ),
                class_name=class_name,
                method_name=method_name,
            )

        repo = field.connected_repo
        if repo is None or not repo.id:
            raise ValidationError(
                message=(
                    f"Connector field '{field.id}' does not expose connected repo metadata"
                ),
                class_name=class_name,
                method_name=method_name,
            )

        if repo.isPipe():
            available_ids = {
                option.id
                for option in self._listPipeOptions(repo, search=None, limit=None)
                if option.id
            }
        elif repo.isTable():
            available_ids = {
                option.id
                for option in self._listTableOptions(repo, search=None, limit=None)
                if option.id
            }
        else:
            raise ValidationError(
                message=(
                    f"Unsupported connected repo type '{repo.repo_type}' "
                    f"for connector field '{field.id}'"
                ),
                class_name=class_name,
                method_name=method_name,
            )

        invalid_ids = [
            item_id for item_id in normalized_ids if item_id not in available_ids
        ]
        if invalid_ids:
            raise ValidationError(
                message=(
                    f"Connector field '{field.id}' contains ids not found in connected repo "
                    f"'{repo.name or repo.id}': {invalid_ids}"
                ),
                class_name=class_name,
                method_name=method_name,
            )

        return normalized_ids

    def getCardValue(self, card_id: str, field_id: str) -> ConnectorValue:
        """
        Retrieve a structured connector value for a card field.

        This helper is schema-aware. If the connector exists in the card pipe
        but is absent from ``card.fields``, an empty ``ConnectorValue`` is
        returned instead of treating the field as missing.

        :param card_id: str = Card identifier
        :param field_id: str = Connector field identifier

        :return: ConnectorValue = Structured connector value
        """
        class_name, method_name = getExceptionContext(self)
        self._validateCardId(card_id, class_name, method_name)
        self._validateFieldId(field_id, class_name, method_name)

        card_service = self._requireCardService(class_name, method_name)
        phase_field = card_service.getCardPipeField(card_id, field_id)
        if phase_field is None or not phase_field.isConnector():
            raise ValidationError(
                message=f"Field '{field_id}' is not a connector field for card '{card_id}'",
                class_name=class_name,
                method_name=method_name,
            )

        card = card_service.getCardModel(card_id)
        value = card.getConnectorValue(field_id)
        if value is not None:
            return value

        return ConnectorValue(field_id=field_id)

    def setCardValue(
        self,
        card_id: str,
        field_id: str,
        item_ids: List[str],
    ) -> Dict[str, Any]:
        """
        Replace the connected ids of a connector field.

        :param card_id: str = Card identifier
        :param field_id: str = Connector field identifier
        :param item_ids: list[str] = Replacement connected item ids

        :return: dict = Raw update response keyed by updated field
        """
        class_name, method_name = getExceptionContext(self)
        self._validateCardId(card_id, class_name, method_name)
        self._validateFieldId(field_id, class_name, method_name)

        card_service = self._requireCardService(class_name, method_name)
        phase_field = card_service.getCardPipeField(card_id, field_id)
        if phase_field is None or not phase_field.isConnector():
            raise ValidationError(
                message=f"Field '{field_id}' is not a connector field for card '{card_id}'",
                class_name=class_name,
                method_name=method_name,
            )

        normalized_ids = self.validateConnectorSelection(phase_field, item_ids)
        return self._updateCardConnectorIds(
            card_service=card_service,
            card_id=card_id,
            field_id=field_id,
            item_ids=normalized_ids,
        )

    def _updateCardConnectorIds(
        self,
        card_service: "CardService",
        card_id: str,
        field_id: str,
        item_ids: List[str],
    ) -> Dict[str, Any]:
        """
        Apply a validated connector id list to a card field.

        :param card_service: CardService = Card service used for updates
        :param card_id: str = Card identifier
        :param field_id: str = Connector field identifier
        :param item_ids: list[str] = Already validated connected ids

        :return: dict = Raw update response keyed by updated field
        """
        return card_service.updateFields(
            card_id=card_id,
            fields={field_id: list(item_ids)},
            config=CardUpdateConfig(validate_field_existence=False),
        )

    def addCardValue(
        self,
        card_id: str,
        field_id: str,
        item_ids: List[str],
    ) -> Dict[str, Any]:
        """
        Add connected ids to a connector field using read-modify-write.

        :param card_id: str = Card identifier
        :param field_id: str = Connector field identifier
        :param item_ids: list[str] = Connected item ids to add

        :return: dict = Raw update response keyed by updated field
        """
        current = self.getCardValue(card_id, field_id)
        merged_ids = list(current.item_ids)
        for item_id in item_ids:
            normalized = str(item_id).strip()
            if normalized and normalized not in merged_ids:
                merged_ids.append(normalized)
        class_name, method_name = getExceptionContext(self)
        card_service = self._requireCardService(class_name, method_name)
        phase_field = card_service.getCardPipeField(card_id, field_id)
        if phase_field is None or not phase_field.isConnector():
            raise ValidationError(
                message=f"Field '{field_id}' is not a connector field for card '{card_id}'",
                class_name=class_name,
                method_name=method_name,
            )
        normalized_ids = self.validateConnectorSelection(phase_field, merged_ids)
        return self._updateCardConnectorIds(
            card_service=card_service,
            card_id=card_id,
            field_id=field_id,
            item_ids=normalized_ids,
        )

    def removeCardValue(
        self,
        card_id: str,
        field_id: str,
        item_ids: List[str],
    ) -> Dict[str, Any]:
        """
        Remove connected ids from a connector field using read-modify-write.

        :param card_id: str = Card identifier
        :param field_id: str = Connector field identifier
        :param item_ids: list[str] = Connected item ids to remove

        :return: dict = Raw update response keyed by updated field
        """
        class_name, method_name = getExceptionContext(self)
        self._validateCardId(card_id, class_name, method_name)
        self._validateFieldId(field_id, class_name, method_name)

        card_service = self._requireCardService(class_name, method_name)
        phase_field = card_service.getCardPipeField(card_id, field_id)
        if phase_field is None or not phase_field.isConnector():
            raise ValidationError(
                message=f"Field '{field_id}' is not a connector field for card '{card_id}'",
                class_name=class_name,
                method_name=method_name,
            )

        normalized_to_remove = set(
            self.validateConnectorSelection(phase_field, item_ids)
        )
        current = self.getCardValue(card_id, field_id)
        remaining_ids = [
            current_id
            for current_id in current.item_ids
            if current_id not in normalized_to_remove
        ]
        return self._updateCardConnectorIds(
            card_service=card_service,
            card_id=card_id,
            field_id=field_id,
            item_ids=remaining_ids,
        )

    def _findConnectorFieldMatches(
        self,
        pipe_id: str,
        field_id: str,
        phase_id: Optional[str],
    ) -> List[ConnectorFieldSpec]:
        """
        Retrieve all connector field matches for a pipe and optional phase.

        :param pipe_id: str = Pipe identifier
        :param field_id: str = Connector field identifier
        :param phase_id: str | None = Optional phase identifier

        :return: list[ConnectorFieldSpec] = Matching connector field specs
        """
        class_name, method_name = getExceptionContext(self)
        self._validatePipeId(pipe_id, class_name, method_name)
        self._validateFieldId(field_id, class_name, method_name)

        matches = [
            spec
            for spec in self.listFields(pipe_id)
            if spec.field_id == field_id
            and (phase_id is None or spec.phase_id == phase_id)
        ]
        return matches

    def _raiseAmbiguousConnectorField(
        self,
        pipe_id: str,
        field_id: str,
        matches: List[ConnectorFieldSpec],
    ) -> None:
        """
        Raise a validation error for an ambiguous connector selection.

        :param pipe_id: str = Pipe identifier
        :param field_id: str = Connector field identifier
        :param matches: list[ConnectorFieldSpec] = Candidate specs
        """
        origins = [
            (
                f"phase:{match.phase_id}:{match.phase_name}"
                if match.isPhaseField()
                else "start_form"
            )
            for match in matches
        ]
        raise ValidationError(
            message=(
                f"Connector field '{field_id}' is ambiguous in pipe '{pipe_id}'. "
                f"Matches: {origins}"
            ),
            class_name=self.__class__.__name__,
            method_name="_raiseAmbiguousConnectorField",
        )

    def _requireConnectedRepo(
        self,
        spec: ConnectorFieldSpec,
        class_name: str,
        method_name: str,
    ) -> ConnectedRepoRef:
        """
        Retrieve connected repo metadata from a connector spec and fail if absent.

        :param spec: ConnectorFieldSpec = Connector field specification
        :param class_name: str = Calling class name
        :param method_name: str = Calling method name

        :return: ConnectedRepoRef = Connected repo metadata
        """
        repo = spec.connected_repo
        if repo is None or not repo.id:
            raise ValidationError(
                message=(
                    f"Connector field '{spec.field_id}' does not expose connected repo metadata"
                ),
                class_name=class_name,
                method_name=method_name,
            )
        return repo

    @staticmethod
    def _normalizeConnectorIds(
        field_id: str,
        value: Any,
        class_name: str,
        method_name: str,
    ) -> List[str]:
        """
        Normalize connector payload into a list of connected item ids.

        :param field_id: str = Connector field identifier
        :param value: Any = Proposed connector payload
        :param class_name: str = Calling class name
        :param method_name: str = Calling method name

        :return: list[str] = Normalized ids
        """
        if not isinstance(value, list):
            raise ValidationError(
                message=(
                    f"Connector field '{field_id}' expects a list of connected item ids"
                ),
                class_name=class_name,
                method_name=method_name,
            )

        normalized_ids: List[str] = []
        for item in value:
            if item is None:
                raise ValidationError(
                    message=(
                        f"Connector field '{field_id}' contains a null connected item id"
                    ),
                    class_name=class_name,
                    method_name=method_name,
                )
            item_id = str(item).strip()
            if not item_id:
                raise ValidationError(
                    message=(
                        f"Connector field '{field_id}' contains an empty connected item id"
                    ),
                    class_name=class_name,
                    method_name=method_name,
                )
            normalized_ids.append(item_id)

        return normalized_ids

    def _listPipeOptions(
        self,
        repo: ConnectedRepoRef,
        search: Optional[str],
        limit: Optional[int],
    ) -> List[ConnectorOption]:
        """
        List connector options backed by a connected pipe.

        :param repo: ConnectedRepoRef = Connected pipe metadata
        :param search: str | None = Optional title filter
        :param limit: int | None = Maximum number of results

        :return: list[ConnectorOption] = Pipe-backed connector options
        """
        repo_id = str(repo.id)
        normalized_search = str(search or "").strip().casefold()
        options: List[ConnectorOption] = []
        after: Optional[str] = None

        while True:
            query = self._buildAllCardsConnectorQuery(pipe_id=repo_id, after=after)
            response = self._client.sendRequest(query, timeout=60)
            all_cards = self._extractAllCardsPayload(response)

            for edge in all_cards.get("edges", []):
                if not isinstance(edge, dict):
                    continue
                node = edge.get("node")
                if not isinstance(node, dict):
                    continue

                option = ConnectorOption.fromPipeCardNode(
                    node,
                    repo_id=repo_id,
                    repo_name=repo.name,
                )
                if (
                    normalized_search
                    and normalized_search not in str(option.title or "").casefold()
                ):
                    continue
                options.append(option)

                if limit is not None and len(options) >= limit:
                    return options[:limit]

            page_info = all_cards.get("pageInfo") or {}
            has_next_page = bool(page_info.get("hasNextPage"))
            after = page_info.get("endCursor")
            if not has_next_page or not after:
                break

        return options[:limit] if limit is not None else options

    def _listPipeOptionsForResolution(
        self,
        repo: ConnectedRepoRef,
        desired_title: str,
    ) -> List[ConnectorOption]:
        """
        List pipe-backed connector options until exact title resolution is possible.

        :param repo: ConnectedRepoRef = Connected pipe metadata
        :param desired_title: str = Desired exact title

        :return: list[ConnectorOption] = Candidate options inspected for resolution
        """
        normalized_title = desired_title.strip().casefold()
        repo_id = str(repo.id)
        options: List[ConnectorOption] = []
        after: Optional[str] = None
        exact_match_count = 0

        while True:
            query = self._buildAllCardsConnectorQuery(pipe_id=repo_id, after=after)
            response = self._client.sendRequest(query, timeout=60)
            all_cards = self._extractAllCardsPayload(response)

            for edge in all_cards.get("edges", []):
                if not isinstance(edge, dict):
                    continue
                node = edge.get("node")
                if not isinstance(node, dict):
                    continue

                option = ConnectorOption.fromPipeCardNode(
                    node,
                    repo_id=repo_id,
                    repo_name=repo.name,
                )
                options.append(option)
                if str(option.title or "").strip().casefold() == normalized_title:
                    exact_match_count += 1
                    if exact_match_count > 1:
                        return options

            page_info = all_cards.get("pageInfo") or {}
            has_next_page = bool(page_info.get("hasNextPage"))
            after = page_info.get("endCursor")
            if not has_next_page or not after:
                break

        return options

    def _listTableOptions(
        self,
        repo: ConnectedRepoRef,
        search: Optional[str],
        limit: Optional[int],
    ) -> List[ConnectorOption]:
        """
        List connector options backed by a connected table.

        :param repo: ConnectedRepoRef = Connected table metadata
        :param search: str | None = Optional title filter
        :param limit: int | None = Maximum number of results

        :return: list[ConnectorOption] = Table-backed connector options
        """
        repo_id = str(repo.id)
        normalized_search = str(search or "").strip().casefold()
        query = self._buildTableRecordsConnectorQuery(table_id=repo_id)
        response = self._client.sendRequest(query, timeout=60)
        records = self._extractTableRecordsPayload(response)

        options: List[ConnectorOption] = []
        for edge in records.get("edges", []):
            if not isinstance(edge, dict):
                continue
            node = edge.get("node")
            if not isinstance(node, dict):
                continue

            option = ConnectorOption.fromTableRecordNode(
                node,
                repo_id=repo_id,
                repo_name=repo.name,
            )
            if (
                normalized_search
                and normalized_search not in str(option.title or "").casefold()
            ):
                continue
            options.append(option)
            if limit is not None and len(options) >= limit:
                return options[:limit]

        return options[:limit] if limit is not None else options

    @staticmethod
    def _buildAllCardsConnectorQuery(
        pipe_id: str,
        after: Optional[str] = None,
    ) -> str:
        """
        Build a paginated card listing query for pipe-backed connectors.

        :param pipe_id: str = Connected pipe identifier
        :param after: str | None = Optional cursor

        :return: str = GraphQL query
        """
        after_param = f', after: "{after}"' if after else ""
        return f"""
        {{
          allCards(pipeId: {pipe_id}{after_param}) {{
            pageInfo {{
              hasNextPage
              endCursor
            }}
            edges {{
              node {{
                id
                title
                current_phase {{
                  id
                  name
                }}
              }}
            }}
          }}
        }}
        """

    @staticmethod
    def _buildTableRecordsConnectorQuery(table_id: str) -> str:
        """
        Build a table records listing query for table-backed connectors.

        :param table_id: str = Connected table identifier

        :return: str = GraphQL query
        """
        return f"""
        {{
          table_records(table_id: "{table_id}") {{
            edges {{
              node {{
                id
                title
                path
                url
                uuid
                record_fields {{
                  indexName
                  name
                  value
                }}
              }}
            }}
          }}
        }}
        """

    def _extractAllCardsPayload(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and validate the ``allCards`` payload from a GraphQL response.

        :param response: dict = Raw GraphQL response

        :return: dict = ``allCards`` payload
        """
        data = response.get("data")
        if not isinstance(data, dict):
            raise UnexpectedResponseError(
                message="'data' field missing or invalid",
                class_name=self.__class__.__name__,
                method_name="_extractAllCardsPayload",
            )

        payload = data.get("allCards")
        if not isinstance(payload, dict):
            raise UnexpectedResponseError(
                message="'allCards' field missing or invalid",
                class_name=self.__class__.__name__,
                method_name="_extractAllCardsPayload",
            )
        return payload

    def _requireCardService(self, class_name: str, method_name: str) -> "CardService":
        """
        Retrieve the injected card service required by semantic card helpers.

        :param class_name: str = Calling class name
        :param method_name: str = Calling method name

        :return: CardService = Injected card service
        """
        if self._card_service is None:
            raise RequestError(
                message="ConnectorService card operations require a CardService instance",
                class_name=class_name,
                method_name=method_name,
            )
        return self._card_service

    def _extractTableRecordsPayload(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and validate the ``table_records`` payload from a GraphQL response.

        :param response: dict = Raw GraphQL response

        :return: dict = ``table_records`` payload
        """
        data = response.get("data")
        if not isinstance(data, dict):
            raise UnexpectedResponseError(
                message="'data' field missing or invalid",
                class_name=self.__class__.__name__,
                method_name="_extractTableRecordsPayload",
            )

        payload = data.get("table_records")
        if not isinstance(payload, dict):
            raise UnexpectedResponseError(
                message="'table_records' field missing or invalid",
                class_name=self.__class__.__name__,
                method_name="_extractTableRecordsPayload",
            )
        return payload

    @staticmethod
    def _validatePipeId(pipe_id: str, class_name: str, method_name: str) -> None:
        if not pipe_id or not isinstance(pipe_id, str):
            raise ValidationError(
                message="pipe_id must be a non-empty string",
                class_name=class_name,
                method_name=method_name,
            )

    @staticmethod
    def _validateCardId(card_id: str, class_name: str, method_name: str) -> None:
        if not card_id or not isinstance(card_id, str):
            raise ValidationError(
                message="card_id must be a non-empty string",
                class_name=class_name,
                method_name=method_name,
            )

    @staticmethod
    def _validateFieldId(field_id: str, class_name: str, method_name: str) -> None:
        if not field_id or not isinstance(field_id, str):
            raise ValidationError(
                message="field_id must be a non-empty string",
                class_name=class_name,
                method_name=method_name,
            )

    @staticmethod
    def _validateLimit(limit: int, class_name: str, method_name: str) -> None:
        if not isinstance(limit, int) or limit <= 0:
            raise ValidationError(
                message="limit must be a positive integer",
                class_name=class_name,
                method_name=method_name,
            )
