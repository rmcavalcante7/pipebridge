from __future__ import annotations

from typing import Any, Dict, List, Optional

from pipebridge.client.httpClient import PipefyHttpClient
from pipebridge.exceptions import UnexpectedResponseError, ValidationError
from pipebridge.models.connectedRepoRef import ConnectedRepoRef
from pipebridge.models.connectorFieldSpec import ConnectorFieldSpec
from pipebridge.models.connectorOption import ConnectorOption
from pipebridge.service.connector.discovery.baseConnectorOptionDiscoveryStrategy import (
    BaseConnectorOptionDiscoveryStrategy,
)


class TableConnectorOptionDiscoveryStrategy(BaseConnectorOptionDiscoveryStrategy):
    """
    Discovery strategy for table-backed connectors.

    The Pipefy UI resolves valid connector options contextually through the
    `cards(...)` resolver with `throughConnectors.fieldUuid`. For tables, we
    still attempt a secondary `table_records(...)` fetch to enrich results
    with `record_fields` when that endpoint is available for the connected repo.
    """

    DEFAULT_PAGE_SIZE = 50

    def __init__(self, client: PipefyHttpClient) -> None:
        self._client = client

    def supports(self, spec: ConnectorFieldSpec) -> bool:
        repo = spec.connected_repo
        return repo is not None and repo.isTable()

    def listOptions(
        self,
        spec: ConnectorFieldSpec,
        search: Optional[str],
        limit: Optional[int],
    ) -> List[ConnectorOption]:
        repo = spec.connected_repo
        if repo is None or not repo.id:
            raise ValidationError(
                message=(
                    f"Connector field '{spec.field_id}' does not expose connected repo metadata"
                ),
                class_name=self.__class__.__name__,
                method_name="listOptions",
            )

        discovery_repo_id = repo.getDiscoveryRepoId()
        if not discovery_repo_id:
            raise ValidationError(
                message=(
                    f"Connector field '{spec.field_id}' does not expose a discovery repo id"
                ),
                class_name=self.__class__.__name__,
                method_name="listOptions",
            )
        options: List[ConnectorOption] = []
        if spec.uuid and repo.internal_id:
            try:
                options = self._listContextualCardsOptions(
                    repo_id=str(discovery_repo_id),
                    repo_name=repo.name,
                    field_uuid=spec.uuid,
                    search=search,
                    limit=limit,
                )
            except Exception:
                options = []

        if options:
            self._tryEnrichWithTableRecords(options=options, repo=repo)
        else:
            options = self._listTableRecordOptions(
                repo=repo,
                search=search,
                limit=limit,
            )

        filtered = self._filterOptionsBySearch(options=options, search=search)
        return filtered[:limit] if limit is not None else filtered

    def _listContextualCardsOptions(
        self,
        repo_id: str,
        repo_name: Optional[str],
        field_uuid: str,
        search: Optional[str],
        limit: Optional[int],
    ) -> List[ConnectorOption]:
        normalized_search = str(search or "").strip()
        options: List[ConnectorOption] = []
        after: Optional[str] = None
        page_size = limit if limit is not None else self.DEFAULT_PAGE_SIZE

        while True:
            response = self._client.sendRequest(
                self._buildContextualCardsConnectorQuery(),
                variables={
                    "repoId": repo_id,
                    "endCursor": after,
                    "resultLimit": page_size,
                    "search": {
                        "ignore_ids": [],
                        "title": normalized_search,
                        "include_done": False,
                    },
                    "throughConnectors": {
                        "fieldUuid": field_uuid,
                    },
                },
                timeout=60,
            )
            cards_payload = self._extractCardsPayload(response)

            for edge in cards_payload.get("edges", []):
                if not isinstance(edge, dict):
                    continue
                node = edge.get("node")
                if not isinstance(node, dict):
                    continue

                option = ConnectorOption.fromContextualNode(
                    node,
                    repo_type="Table",
                    repo_id=repo_id,
                    repo_name=repo_name,
                    default_item_type="TableRecord",
                )
                options.append(option)
                if limit is not None and len(options) >= limit:
                    return options[:limit]

            page_info = cards_payload.get("pageInfo") or {}
            has_next_page = bool(page_info.get("hasNextPage"))
            after = page_info.get("endCursor")
            if not has_next_page or not after:
                break

        return options

    def _tryEnrichWithTableRecords(
        self,
        options: List[ConnectorOption],
        repo: ConnectedRepoRef,
    ) -> None:
        candidate_ids: List[str] = []
        for candidate in [repo.id, repo.internal_id]:
            normalized = str(candidate).strip() if candidate is not None else ""
            if normalized and normalized not in candidate_ids:
                candidate_ids.append(normalized)

        for table_id in candidate_ids:
            try:
                query = self._buildTableRecordsConnectorQuery(table_id=table_id)
                response = self._client.sendRequest(query, timeout=60)
                records = self._extractTableRecordsPayload(response)

                record_map: Dict[str, ConnectorOption] = {}
                for edge in records.get("edges", []):
                    if not isinstance(edge, dict):
                        continue
                    node = edge.get("node")
                    if not isinstance(node, dict):
                        continue
                    option = ConnectorOption.fromTableRecordNode(
                        node,
                        repo_id=table_id,
                        repo_name=repo.name,
                    )
                    record_map[option.id] = option

                if not record_map:
                    continue

                for option in options:
                    enriched = record_map.get(option.id)
                    if enriched is None:
                        continue
                    option.record_fields = list(enriched.record_fields)
                    option.record_fields_map = dict(enriched.record_fields_map)
                    option.path = enriched.path or option.path
                    option.url = enriched.url or option.url
                    option.uuid = enriched.uuid or option.uuid
                return
            except Exception:
                continue

    def _listTableRecordOptions(
        self,
        repo: ConnectedRepoRef,
        search: Optional[str],
        limit: Optional[int],
    ) -> List[ConnectorOption]:
        candidate_ids: List[str] = []
        for candidate in [repo.id, repo.internal_id]:
            normalized = str(candidate).strip() if candidate is not None else ""
            if normalized and normalized not in candidate_ids:
                candidate_ids.append(normalized)

        for table_id in candidate_ids:
            try:
                query = self._buildTableRecordsConnectorQuery(table_id=table_id)
                response = self._client.sendRequest(query, timeout=60)
                records = self._extractTableRecordsPayload(response)

                options: List[ConnectorOption] = []
                for edge in records.get("edges", []):
                    if not isinstance(edge, dict):
                        continue
                    node = edge.get("node")
                    if not isinstance(node, dict):
                        continue
                    options.append(
                        ConnectorOption.fromTableRecordNode(
                            node,
                            repo_id=table_id,
                            repo_name=repo.name,
                        )
                    )

                if options:
                    filtered = self._filterOptionsBySearch(
                        options=options,
                        search=search,
                    )
                    return filtered[:limit] if limit is not None else filtered
            except Exception:
                continue

        return []

    @staticmethod
    def _filterOptionsBySearch(
        options: List[ConnectorOption],
        search: Optional[str],
    ) -> List[ConnectorOption]:
        normalized_search = str(search or "").strip().casefold()
        if not normalized_search:
            return list(options)

        return [
            option
            for option in options
            if normalized_search in str(option.title or "").strip().casefold()
        ]

    @staticmethod
    def _buildContextualCardsConnectorQuery() -> str:
        return """
        query getCardConnection(
          $repoId: ID!,
          $endCursor: String,
          $resultLimit: Int,
          $search: CardSearch,
          $throughConnectors: ReferenceConnectorFieldInput
        ) {
          cards(
            pipe_id: $repoId
            first: $resultLimit
            after: $endCursor
            search: $search
            throughConnectors: $throughConnectors
          ) {
            edges {
              node {
                id
                uuid
                title
                current_phase {
                  id
                  name
                }
                url
                summary_attributes {
                  title
                  value
                }
                summary_fields {
                  title
                  value
                  type
                  settings
                }
              }
            }
            pageInfo {
              hasNextPage
              endCursor
            }
          }
        }
        """

    @staticmethod
    def _buildTableRecordsConnectorQuery(table_id: str) -> str:
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

    def _extractCardsPayload(self, response: Dict[str, Any]) -> Dict[str, Any]:
        data = response.get("data")
        if not isinstance(data, dict):
            raise UnexpectedResponseError(
                message="'data' field missing or invalid",
                class_name=self.__class__.__name__,
                method_name="_extractCardsPayload",
            )

        payload = data.get("cards")
        if not isinstance(payload, dict):
            raise UnexpectedResponseError(
                message="'cards' field missing or invalid",
                class_name=self.__class__.__name__,
                method_name="_extractCardsPayload",
            )
        return payload

    def _extractTableRecordsPayload(self, response: Dict[str, Any]) -> Dict[str, Any]:
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
