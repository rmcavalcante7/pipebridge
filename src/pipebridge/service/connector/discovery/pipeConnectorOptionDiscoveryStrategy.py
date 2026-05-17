from __future__ import annotations

from typing import Any, Dict, List, Optional

from pipebridge.client.httpClient import PipefyHttpClient
from pipebridge.exceptions import UnexpectedResponseError, ValidationError
from pipebridge.models.connectorFieldSpec import ConnectorFieldSpec
from pipebridge.models.connectorOption import ConnectorOption
from pipebridge.service.connector.discovery.baseConnectorOptionDiscoveryStrategy import (
    BaseConnectorOptionDiscoveryStrategy,
)


class PipeConnectorOptionDiscoveryStrategy(BaseConnectorOptionDiscoveryStrategy):
    """
    Discovery strategy for pipe-backed connectors.

    Pipefy resolves these options through ``cards(...)`` with
    ``throughConnectors.fieldUuid``. This preserves the same contextual
    resolver used by the Pipefy UI and keeps space for future connector cases.
    """

    DEFAULT_PAGE_SIZE = 50

    def __init__(self, client: PipefyHttpClient) -> None:
        self._client = client

    def supports(self, spec: ConnectorFieldSpec) -> bool:
        repo = spec.connected_repo
        return repo is not None and repo.isPipe()

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
        if not spec.uuid:
            raise ValidationError(
                message=(
                    f"Connector field '{spec.field_id}' does not expose a field UUID "
                    f"required for pipe-backed discovery"
                ),
                class_name=self.__class__.__name__,
                method_name="listOptions",
            )

        repo_id = str(repo.id)
        normalized_search = str(search or "").strip()
        options: List[ConnectorOption] = []
        after: Optional[str] = None
        page_size = limit if limit is not None else self.DEFAULT_PAGE_SIZE

        while True:
            response = self._client.sendRequest(
                self._buildPipeConnectorCardsQuery(),
                variables=self._buildCardsVariables(
                    repo_id=repo_id,
                    field_uuid=spec.uuid,
                    end_cursor=after,
                    result_limit=page_size,
                    title=normalized_search,
                ),
                timeout=60,
            )
            payload = self._extractCardsPayload(response)

            for edge in payload.get("edges", []):
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
                if limit is not None and len(options) >= limit:
                    return options[:limit]

            page_info = payload.get("pageInfo") or {}
            has_next_page = bool(page_info.get("hasNextPage"))
            after = page_info.get("endCursor")
            if not has_next_page or not after:
                break

        return options[:limit] if limit is not None else options

    @staticmethod
    def _buildPipeConnectorCardsQuery() -> str:
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
                created_at
                url
                current_phase {
                  id
                  name
                }
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
                pipe {
                  id
                  name
                  icon
                  color
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
    def _buildCardsVariables(
        repo_id: str,
        field_uuid: str,
        end_cursor: Optional[str],
        result_limit: int,
        title: str,
    ) -> Dict[str, Any]:
        return {
            "repoId": repo_id,
            "endCursor": end_cursor,
            "resultLimit": result_limit,
            "search": {
                "ignore_ids": [],
                "title": title,
                "include_done": False,
            },
            "throughConnectors": {
                "fieldUuid": field_uuid,
            },
        }

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
