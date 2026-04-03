# ============================================================
# Dependencies
# ============================================================
import json
from typing import Any, Dict, List, Optional

from pipefy.client.httpClient import PipefyHttpClient
from pipefy.builders.queryBuilder import QueryBuilder
from pipefy.exceptions import (
    getExceptionContext, ValidationError,RequestError, UnexpectedResponseError, ParsingError,

)

from pipefy.models.card import Card
from pipefy.models.pagination import PaginatedResponse


class CardService:
    """
   Service responsible for card operations in Pipefy.

    This service provides a complete abstraction over Pipefy GraphQL
    for managing cards, including creation, retrieval, updates,
    and movement across phases.

    :param client: PipefyHttpClient = HTTP client instance

    :example:
        >>> service = CardService(PipefyHttpClient(auth_key="token", base_url="https://api.pipefy.com/graphql"))
        >>> isinstance(service, CardService)
        True
    """

    def __init__(self, client: PipefyHttpClient) -> None:
        """
        Initialize CardService instance.

        :param client: PipefyHttpClient = HTTP client instance

        :return: None

        :raises TypeError:
            When client is not an instance of PipefyHttpClient

        :example:
            >>> client = PipefyHttpClient(auth_key="token", base_url="https://api.pipefy.com/graphql")
            >>> service = CardService(client)
            >>> isinstance(service, CardService)
            True
        """
        self._client: PipefyHttpClient = client

    # ============================================================
    # Basic Operations
    # ============================================================
    def createCard(
        self,
        pipe_id: str,
        title: str,
        fields: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new card in a pipe.

        This method creates a card in the specified pipe and optionally
        sets initial field values.

        :param pipe_id: str = Pipe identifier
        :param title: str = Card title
        :param fields: dict[str, Any] | None = Field values mapped by field_id

        :return: dict = Raw API response containing created card metadata

        :raises ValidationError:
            When pipe_id or title is empty
        :raises ValidationError:
            When fields is not a dictionary
        :raises RequestError:
            When request execution fails

        :example:
            >>> service = CardService(PipefyHttpClient(auth_key="token", base_url="https://api.pipefy.com/graphql"))
            >>> callable(service.createCard)
            True
        """

        class_name, method_name = getExceptionContext(self)

        if not pipe_id:
            raise ValidationError(
                message="pipe_id cannot be empty",
                class_name=class_name,
                method_name=method_name
            )

        if not title:
            raise ValidationError(
                message="title cannot be empty",
                class_name=class_name,
                method_name=method_name
            )

        if fields is not None and not isinstance(fields, dict):
            raise ValidationError(
                message="fields must be a dictionary",
                class_name=class_name,
                method_name=method_name
            )

        fields = fields or {}

        fields_payload: List[Dict[str, Any]] = [
            {"field_id": k, "field_value": v}
            for k, v in fields.items()
            if v is not None
        ]

        query: str = f"""
            mutation {{
                createCard(input: {{
                    pipe_id: {pipe_id},
                    title: "{title}",
                    fields_attributes: {json.dumps(fields_payload)}
                }}) {{
                    card {{
                        id
                        title
                    }}
                }}
            }}
            """

        try:
            return self._client.sendRequest(query, timeout=60)

        except Exception as exc:
            raise RequestError(
                message=str(exc),
                class_name=class_name,
                method_name=method_name
            ) from exc

    def getRawCard(
            self,
            card_id: str,
            query_body: str
    ) -> Dict[str, Any]:
        """
        Execute a raw GraphQL query for a card.

        This method allows full control over the GraphQL query structure.

        :param card_id: str = Card identifier
        :param query_body: str = GraphQL body inside card query

        :return: dict = Raw API response

        :raises ValidationError:
            When card_id or query_body is empty
        :raises RequestError:
            When request execution fails

        :example:
            >>> service = CardService(PipefyHttpClient(auth_key="token", base_url="https://api.pipefy.com/graphql"))
            >>> callable(service.getRawCard)
            True
        """

        class_name, method_name = getExceptionContext(self)

        if not card_id:
            raise ValidationError(
                message="card_id cannot be empty",
                class_name=class_name,
                method_name=method_name
            )

        if not query_body:
            raise ValidationError(
                message="query_body cannot be empty",
                class_name=class_name,
                method_name=method_name
            )

        query: str = f"""
            {{
              card(id: {card_id}) {{
                {query_body}
              }}
            }}
            """

        try:
            return self._client.sendRequest(query, timeout=60)

        except Exception as exc:
            raise RequestError(
                message=str(exc),
                class_name=class_name,
                method_name=method_name
            ) from exc

    # ============================================================
    # Structured (High-Level)
    # ============================================================
    def getCardStructured(
            self,
            card_id: str,
            query_body: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve structured card data.

        This method abstracts GraphQL complexity by providing a default
        query that includes commonly used fields such as phases,
        fields, labels, assignees, and attachments.

        :param card_id: str = Card identifier
        :param query_body: str | None = Custom GraphQL body override

        :return: dict = Structured card data

        :raises ValidationError:
            When card_id is empty
        :raises RequestError:
            When request execution fails
        :raises UnexpectedResponseError:
            When API response is invalid or missing expected data

        :example:
            >>> service = CardService(PipefyHttpClient(auth_key="token", base_url="https://api.pipefy.com/graphql"))
            >>> callable(service.getCardStructured)
            True
        """

        class_name, method_name = getExceptionContext(self)

        if not card_id:
            raise ValidationError(
                message="card_id cannot be empty",
                class_name=class_name,
                method_name=method_name
            )

        dafault_query: str = """
            id
            title

            current_phase {
              id
              name
            }

            phases_history {
              phase {
                id
                name
              }
              firstTimeIn
              lastTimeIn
            }

            fields {
              field {
                id
                label
                type
              }
              value
              report_value
            }

            assignees {
              id
              name
            }

            labels {
              id
              name
            }
            
            attachments {
                url
            }
        """

        query_body = query_body or dafault_query

        try:
            response: Dict[str, Any] = self.getRawCard(card_id, query_body)

            data: Dict[str, Any] = response.get("data", {})
            card_data: Dict[str, Any] = data.get("card", {})

            if not card_data:
                raise UnexpectedResponseError(
                    message="Card not found in API response",
                    class_name=class_name,
                    method_name=method_name
                )

            return card_data

        except (ValidationError, UnexpectedResponseError):
            raise

        except Exception as exc:
            raise RequestError(
                message=str(exc),
                class_name=class_name,
                method_name=method_name
            ) from exc

    def moveCardToPhase(
            self,
            card_id: str,
            phase_id: str
    ) -> Dict[str, Any]:
        """
        Move a card to another phase in Pipefy.

        This method executes a GraphQL mutation to move a card
        from its current phase to a destination phase.

        :param card_id: str = Unique identifier of the card to be moved
        :param phase_id: str = Destination phase ID

        :return: dict = Raw API response containing updated card reference

        :raises ValidationError:
            When card_id or phase_id is empty
        :raises RequestError:
            When request execution fails

        :example:
            >>> service = CardService(PipefyHttpClient(auth_key="token", base_url="https://api.pipefy.com/graphql"))
            >>> callable(service.moveCardToPhase)
            True
        """

        class_name, method_name = getExceptionContext(self)

        if not card_id:
            raise ValidationError(
                message="card_id cannot be empty",
                class_name=class_name,
                method_name=method_name
            )

        if not phase_id:
            raise ValidationError(
                message="phase_id cannot be empty",
                class_name=class_name,
                method_name=method_name
            )

        query: str = f"""
            mutation {{
                moveCardToPhase(input: {{
                    card_id: {card_id},
                    destination_phase_id: {phase_id}
                }}) {{
                    card {{
                        id
                    }}
                }}
            }}
            """

        try:
            response: Dict[str, Any] = self._client.sendRequest(query, timeout=60)
            return response

        except ValidationError:
            raise

        except Exception as exc:
            raise RequestError(
                message=str(exc),
                class_name=class_name,
                method_name=method_name
            ) from exc


    # ============================================================
    # Search & Relations
    # ============================================================

    def searchCards(
            self,
            pipe_id: str,
            title: str
    ) -> List[Dict[str, Any]]:
        """
        Search for cards in a pipe by title.

        This method executes a GraphQL query to find cards whose titles
        match the provided search term.

        :param pipe_id: str = Pipe ID where the search will be performed
        :param title: str = Title or partial title used as search filter

        :return: list[dict] = List of card nodes containing basic information (id, title)

        :raises ValidationError:
            When pipe_id or title is empty
        :raises UnexpectedResponseError:
            When API response structure is invalid
        :raises RequestError:
            When request execution fails

        :example:
            >>> service = CardService(PipefyHttpClient(auth_key="token", base_url="https://api.pipefy.com/graphql"))
            >>> callable(service.searchCards)
            True
        """

        class_name, method_name = getExceptionContext(self)

        if not pipe_id:
            raise ValidationError(
                message="pipe_id cannot be empty",
                class_name=class_name,
                method_name=method_name
            )

        if not title:
            raise ValidationError(
                message="title cannot be empty",
                class_name=class_name,
                method_name=method_name
            )

        query: str = f"""
           {{
               cards(pipe_id: {pipe_id}, search: {{ title: "{title}" }}) {{
                   edges {{
                       node {{
                           id
                           title
                       }}
                   }}
               }}
           }}
           """

        try:
            response: Dict[str, Any] = self._client.sendRequest(query, timeout=60)

            data: Dict[str, Any] = response.get("data")
            if not isinstance(data, dict):
                raise UnexpectedResponseError(
                    message="'data' field missing or invalid in response",
                    class_name=class_name,
                    method_name=method_name
                )

            cards_data: Dict[str, Any] = data.get("cards")
            if not isinstance(cards_data, dict):
                raise UnexpectedResponseError(
                    message="'cards' field missing in response",
                    class_name=class_name,
                    method_name=method_name
                )

            edges: List[Dict[str, Any]] = cards_data.get("edges")
            if not isinstance(edges, list):
                raise UnexpectedResponseError(
                    message="'edges' field missing or invalid",
                    class_name=class_name,
                    method_name=method_name
                )

            return [
                edge.get("node", {})
                for edge in edges
                if isinstance(edge, dict) and edge.get("node")
            ]

        except (ValidationError, UnexpectedResponseError):
            raise

        except Exception as exc:
            raise RequestError(
                message=str(exc),
                class_name=class_name,
                method_name=method_name
            ) from exc

    def relateCards(
            self,
            parent_id: str,
            child_id: str,
            source_id: str
    ) -> Dict[str, Any]:
        """
        Create a relationship between two cards in Pipefy.

        This method executes a GraphQL mutation to establish a relationship
        between a parent card and a child card using a Pipe relation.

        :param parent_id: str = Parent card ID (source of the relationship)
        :param child_id: str = Child card ID (target of the relationship)
        :param source_id: str = Pipe relation ID used to define the relationship

        :return: dict = Raw API response containing the created relation ID

        :raises ValidationError:
            When parent_id, child_id or source_id is empty
        :raises RequestError:
            When request execution fails

        :example:
            >>> service = CardService(PipefyHttpClient(auth_key="token", base_url="https://api.pipefy.com/graphql"))
            >>> callable(service.relateCards)
            True
        """

        class_name, method_name = getExceptionContext(self)

        if not parent_id:
            raise ValidationError(
                message="parent_id cannot be empty",
                class_name=class_name,
                method_name=method_name
            )

        if not child_id:
            raise ValidationError(
                message="child_id cannot be empty",
                class_name=class_name,
                method_name=method_name
            )

        if not source_id:
            raise ValidationError(
                message="source_id cannot be empty",
                class_name=class_name,
                method_name=method_name
            )

        query: str = f"""
            mutation {{
                createCardRelation(input: {{
                    parentId: {parent_id},
                    childId: {child_id},
                    sourceId: {source_id},
                    sourceType: "PipeRelation"
                }}) {{
                    cardRelation {{
                        id
                    }}
                }}
            }}
            """

        try:
            response: Dict[str, Any] = self._client.sendRequest(query, timeout=60)
            return response

        except ValidationError:
            raise

        except Exception as exc:
            raise RequestError(
                message=str(exc),
                class_name=class_name,
                method_name=method_name
            ) from exc

    # ============================================================
    # Pagination Methods (CRÍTICOS)
    # ============================================================

    def listAllCards(
            self,
            pipe_id: str,
            attributes: Optional[List[str]] = None,
            filters: Optional[Dict[str, Any]] = None,
            only_phase_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve all cards from a pipe using cursor-based pagination.

        This method iteratively fetches all cards from a given pipe using GraphQL pagination.
        It supports optional filtering and phase-based restriction.

        :param pipe_id: str = Pipe ID from which cards will be retrieved
        :param attributes: list[str] | None = List of attributes to include in the query.
            Defaults to ["id", "title"]
        :param filters: dict | None = GraphQL filter object to refine results
        :param only_phase_name: str | None = If provided, only cards belonging to this phase
            name will be returned

        :return: list[dict] = List of card nodes matching the query criteria

        :raises ValidationError:
            When pipe_id is empty
        :raises ValidationError:
            When attributes is not a list
        :raises UnexpectedResponseError:
            When API response structure is invalid
        :raises RequestError:
            When request execution fails

        :example:
            >>> service = CardService(PipefyHttpClient(auth_key="token", base_url="https://api.pipefy.com/graphql"))
            >>> callable(service.listAllCards)
            True
        """

        class_name, method_name = getExceptionContext(self)

        if not pipe_id:
            raise ValidationError(
                message="pipe_id cannot be empty",
                class_name=class_name,
                method_name=method_name
            )

        if attributes is not None and not isinstance(attributes, list):
            raise ValidationError(
                message="attributes must be a list",
                class_name=class_name,
                method_name=method_name
            )

        attributes = attributes or ["id", "title"]

        try:
            query_attributes: str = QueryBuilder.buildCardAttributes(attributes)
        except Exception as exc:
            raise RequestError(
                message=f"Failed to build query attributes: {str(exc)}",
                class_name=class_name,
                method_name=method_name
            ) from exc

        all_cards: List[Dict[str, Any]] = []
        after: Optional[str] = None

        try:
            while True:
                after_param: str = f', after: "{after}"' if after else ''
                filter_param: str = f', filter: {json.dumps(filters)}' if filters else ''

                query: str = f"""
                    {{
                        allCards(pipeId: {pipe_id}{after_param}{filter_param}) {{
                            pageInfo {{
                                hasNextPage
                                endCursor
                            }}
                            edges {{
                                node {query_attributes}
                            }}
                        }}
                    }}
                    """

                response: Dict[str, Any] = self._client.sendRequest(query, timeout=60)

                data = response.get("data")
                if not isinstance(data, dict):
                    raise UnexpectedResponseError(
                        message="'data' field missing or invalid",
                        class_name=class_name,
                        method_name=method_name
                    )

                all_cards_data = data.get("allCards")
                if not isinstance(all_cards_data, dict):
                    raise UnexpectedResponseError(
                        message="'allCards' field missing",
                        class_name=class_name,
                        method_name=method_name
                    )

                edges = all_cards_data.get("edges")
                page_info = all_cards_data.get("pageInfo")

                if not isinstance(edges, list) or not isinstance(page_info, dict):
                    raise UnexpectedResponseError(
                        message="'edges' or 'pageInfo' invalid",
                        class_name=class_name,
                        method_name=method_name
                    )

                for edge in edges:
                    if not isinstance(edge, dict):
                        continue

                    node: Dict[str, Any] = edge.get("node", {})

                    if only_phase_name:
                        phase_name = (
                            node.get("current_phase", {})
                            .get("name")
                        )
                        if phase_name != only_phase_name:
                            continue

                    all_cards.append(node)

                has_next = page_info.get("hasNextPage")
                after = page_info.get("endCursor")

                if not has_next:
                    break

            return all_cards

        except (ValidationError, UnexpectedResponseError):
            raise

        except Exception as exc:
            raise RequestError(
                message=str(exc),
                class_name=class_name,
                method_name=method_name
            ) from exc

    def listCardsFromPhase(
            self,
            phase_id: str,
            limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Retrieve all cards from a specific phase using cursor-based pagination.

        This method iteratively fetches cards from a given phase, handling pagination
        internally until all cards are retrieved.

        :param phase_id: str = Phase ID from which cards will be retrieved
        :param limit: int = Number of cards per request (page size)

        :return: list[dict] = List of card nodes containing basic information (id, title)

        :raises ValidationError:
            When phase_id is empty
        :raises ValidationError:
            When limit is not a positive integer
        :raises UnexpectedResponseError:
            When API response structure is invalid
        :raises RequestError:
            When request execution fails

        :example:
            >>> service = CardService(PipefyHttpClient(auth_key="token", base_url="https://api.pipefy.com/graphql"))
            >>> callable(service.listCardsFromPhase)
            True
        """

        class_name, method_name = getExceptionContext(self)

        if not phase_id:
            raise ValidationError(
                message="phase_id cannot be empty",
                class_name=class_name,
                method_name=method_name
            )

        if not isinstance(limit, int) or limit <= 0:
            raise ValidationError(
                message="limit must be a positive integer",
                class_name=class_name,
                method_name=method_name
            )

        all_cards: List[Dict[str, Any]] = []
        after: Optional[str] = None

        try:
            while True:
                after_param: str = f', after: "{after}"' if after else ''

                query: str = f"""
                    {{
                      phase(id: "{phase_id}") {{
                        cards(first: {limit}{after_param}) {{
                          pageInfo {{
                            hasNextPage
                            endCursor
                          }}
                          edges {{
                            node {{
                              id
                              title
                            }}
                          }}
                        }}
                      }}
                    }}
                    """

                response: Dict[str, Any] = self._client.sendRequest(query, timeout=60)

                data = response.get("data")
                if not isinstance(data, dict):
                    raise UnexpectedResponseError(
                        message="'data' field missing or invalid",
                        class_name=class_name,
                        method_name=method_name
                    )

                phase_data = data.get("phase")
                if not isinstance(phase_data, dict):
                    raise UnexpectedResponseError(
                        message="'phase' field missing",
                        class_name=class_name,
                        method_name=method_name
                    )

                cards_data = phase_data.get("cards")
                if not isinstance(cards_data, dict):
                    raise UnexpectedResponseError(
                        message="'cards' field missing",
                        class_name=class_name,
                        method_name=method_name
                    )

                edges = cards_data.get("edges")
                page_info = cards_data.get("pageInfo")

                if not isinstance(edges, list) or not isinstance(page_info, dict):
                    raise UnexpectedResponseError(
                        message="'edges' or 'pageInfo' invalid",
                        class_name=class_name,
                        method_name=method_name
                    )

                for edge in edges:
                    if not isinstance(edge, dict):
                        continue

                    node: Dict[str, Any] = edge.get("node", {})
                    if node:
                        all_cards.append(node)

                has_next = page_info.get("hasNextPage")
                after = page_info.get("endCursor")

                if not has_next:
                    break

            return all_cards

        except (ValidationError, UnexpectedResponseError):
            raise

        except Exception as exc:
            raise RequestError(
                message=str(exc),
                class_name=class_name,
                method_name=method_name
            ) from exc

    # ============================================================
    # Extended Operations (from pipfey.py)
    # ============================================================
    def deleteCard(self, card_id: str) -> Dict[str, Any]:
        """
        Delete a card from Pipefy.

        This method executes a GraphQL mutation to permanently remove
        a card identified by its ID.

        :param card_id: str = Unique identifier of the card to be deleted

        :return: dict = Raw API response indicating operation success

        :raises ValidationError:
            When card_id is empty
        :raises RequestError:
            When request execution fails

        :example:
            >>> service = CardService(PipefyHttpClient(auth_key="token", base_url="https://api.pipefy.com/graphql"))
            >>> callable(service.deleteCard)
            True
        """

        class_name, method_name = getExceptionContext(self)

        if not card_id:
            raise ValidationError(
                message="card_id cannot be empty",
                class_name=class_name,
                method_name=method_name
            )

        query: str = f"""
            mutation {{
                deleteCard(input: {{ id: {card_id} }}) {{
                    success
                }}
            }}
            """

        try:
            response: Dict[str, Any] = self._client.sendRequest(query, timeout=60)
            return response

        except ValidationError:
            raise

        except Exception as exc:
            raise RequestError(
                message=str(exc),
                class_name=class_name,
                method_name=method_name
            ) from exc

    def updateField(
            self,
            card_id: str,
            field_id: str,
            value: str
    ) -> Dict[str, Any]:
        """
        Update a single field of a card.

        This is a convenience wrapper over updateFields.

        :param card_id: str = Card identifier
        :param field_id: str = Field identifier
        :param value: str = Field value

        :return: dict = Raw API response

        :raises ValidationError:
            When card_id or field_id is empty
        :raises RequestError:
            When request execution fails (propagated from updateFields)

        :example:
            >>> service = CardService(PipefyHttpClient(auth_key="token", base_url="https://api.pipefy.com/graphql"))
            >>> callable(service.updateField)
            True
        """

        class_name, method_name = getExceptionContext(self)

        if not card_id:
            raise ValidationError(
                message="card_id cannot be empty",
                class_name=class_name,
                method_name=method_name
            )

        if not field_id:
            raise ValidationError(
                message="field_id cannot be empty",
                class_name=class_name,
                method_name=method_name
            )

        return self.updateFields(card_id, {field_id: value})

    def updateFields(
            self,
            card_id: str,
            fields: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update multiple fields of a card.

        This method updates multiple fields using a dictionary
        mapping field IDs to values.

        :param card_id: str = Card identifier
        :param fields: dict[str, Any] = Mapping of field_id to value

        :return: dict = Raw API response

        :raises ValidationError:
            When card_id is empty
        :raises ValidationError:
            When fields is not a dictionary
        :raises ValidationError:
            When no valid fields are provided
        :raises RequestError:
            When request execution fails

        :example:
            >>> service = CardService(PipefyHttpClient(auth_key="token", base_url="https://api.pipefy.com/graphql"))
            >>> callable(service.updateFields)
            True
        """

        class_name, method_name = getExceptionContext(self)

        if not card_id:
            raise ValidationError(
                message="card_id cannot be empty",
                class_name=class_name,
                method_name=method_name
            )

        if not isinstance(fields, dict):
            raise ValidationError(
                message="fields must be a dictionary",
                class_name=class_name,
                method_name=method_name
            )

        values: List[Dict[str, Any]] = [
            {"fieldId": field_id, "value": value}
            for field_id, value in fields.items()
            if value is not None
        ]

        if not values:
            raise ValidationError(
                message="No valid fields provided for update",
                class_name=class_name,
                method_name=method_name
            )

        # query: str = f"""
        #    mutation {{
        #        updateFieldsValues(input: {{
        #            nodeId: {card_id},
        #            values: {json.dumps(values)}
        #        }}) {{
        #            success
        #        }}
        #    }}
        #    """

        values_str: str = self._buildGraphQLValues(values)

        query: str = f"""
        mutation {{
            updateFieldsValues(input: {{
                nodeId: {card_id},
                values: {values_str}
            }}) {{
                success
            }}
        }}
        """

        try:
            response: Dict[str, Any] = self._client.sendRequest(query, timeout=60)
            return response

        except ValidationError:
            raise

        except Exception as exc:
            raise RequestError(
                message=str(exc),
                class_name=class_name,
                method_name=method_name
            ) from exc

    def updateAssigneeIds(
            self,
            card_id: str,
            assignee_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Update the assignees of a card.

        This method executes a GraphQL mutation to assign one or more users
        to a card.

        :param card_id: str = Card ID to be updated
        :param assignee_ids: list[str] = List of user IDs to assign to the card

        :return: dict = Raw API response containing updated card data

        :raises ValidationError:
            When card_id is empty
        :raises ValidationError:
            When assignee_ids is not a list of strings
        :raises RequestError:
            When request execution fails

        :example:
            >>> service = CardService(PipefyHttpClient(auth_key="token", base_url="https://api.pipefy.com/graphql"))
            >>> callable(service.updateAssigneeIds)
            True
        """

        class_name, method_name = getExceptionContext(self)

        if not card_id:
            raise ValidationError(
                message="card_id cannot be empty",
                class_name=class_name,
                method_name=method_name
            )

        if not isinstance(assignee_ids, list):
            raise ValidationError(
                message="assignee_ids must be a list",
                class_name=class_name,
                method_name=method_name
            )

        if not all(isinstance(i, str) for i in assignee_ids):
            raise ValidationError(
                message="assignee_ids must contain only strings",
                class_name=class_name,
                method_name=method_name
            )

        query: str = f"""
            mutation {{
                updateCard(input: {{
                    id: {card_id},
                    assignee_ids: {json.dumps(assignee_ids)}
                }}) {{
                    card {{
                        id
                        title
                    }}
                }}
            }}
            """

        try:
            response: Dict[str, Any] = self._client.sendRequest(query, timeout=60)
            return response

        except ValidationError:
            raise

        except Exception as exc:
            raise RequestError(
                message=str(exc),
                class_name=class_name,
                method_name=method_name
            ) from exc

    def updateLabelIds(
            self,
            card_id: str,
            label_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Update the labels of a card.

        This method executes a GraphQL mutation to assign one or more labels
        to a card.

        :param card_id: str = Card ID to be updated
        :param label_ids: list[str] = List of label IDs to assign to the card

        :return: dict = Raw API response containing updated card data

        :raises ValidationError:
            When card_id is empty
        :raises ValidationError:
            When label_ids is not a list of strings
        :raises RequestError:
            When request execution fails

        :example:
            >>> service = CardService(PipefyHttpClient(auth_key="token", base_url="https://api.pipefy.com/graphql"))
            >>> callable(service.updateLabelIds)
            True
        """

        class_name, method_name = getExceptionContext(self)

        if not card_id:
            raise ValidationError(
                message="card_id cannot be empty",
                class_name=class_name,
                method_name=method_name
            )

        if not isinstance(label_ids, list):
            raise ValidationError(
                message="label_ids must be a list",
                class_name=class_name,
                method_name=method_name
            )

        if not all(isinstance(i, str) for i in label_ids):
            raise ValidationError(
                message="label_ids must contain only strings",
                class_name=class_name,
                method_name=method_name
            )

        query: str = f"""
            mutation {{
                updateCard(input: {{
                    id: {card_id},
                    label_ids: {json.dumps(label_ids)}
                }}) {{
                    card {{
                        id
                        title
                    }}
                }}
            }}
            """

        try:
            response: Dict[str, Any] = self._client.sendRequest(query, timeout=60)
            return response

        except ValidationError:
            raise

        except Exception as exc:
            raise RequestError(
                message=str(exc),
                class_name=class_name,
                method_name=method_name
            ) from exc

    def getCardModel(
            self,
            card_id: str,
            query_body: Optional[str] = None
    ) -> Card:
        """
        Retrieve a card as a strongly-typed model.

        This method retrieves structured card data and converts it
        into a Card instance.

        :param card_id: str = Card identifier
        :param query_body: str | None = Optional GraphQL fields

        :return: Card = Parsed Card model instance

        :raises ValidationError:
            When card_id is empty
        :raises RequestError:
            When request execution fails
        :raises UnexpectedResponseError:
            When API response is invalid
        :raises ParsingError:
            When response cannot be converted into Card model

        :example:
            >>> service = CardService(PipefyHttpClient(auth_key="token", base_url="https://api.pipefy.com/graphql"))
            >>> callable(service.getCardModel)
            True
        """

        class_name, method_name = getExceptionContext(self)

        if not card_id:
            raise ValidationError(
                message="card_id cannot be empty",
                class_name=class_name,
                method_name=method_name
            )

        try:
            data: Dict[str, Any] = self.getCardStructured(
                card_id,
                query_body
            )

            return Card.fromDict(data)

        except (ValidationError, ParsingError):
            raise

        except Exception as exc:
            raise ParsingError(
                message=str(exc),
                class_name=class_name,
                method_name=method_name
            ) from exc

    def listAllCardsPaginated(
            self,
            pipe_id: str,
            attributes: Optional[List[str]] = None
    ) -> List[Card]:
        """
        Retrieve all cards from a pipe as typed Card models using pagination.

        This method performs cursor-based pagination and converts each card node
        into a Card model instance.

        :param pipe_id: str = Pipe ID from which cards will be retrieved
        :param attributes: list[str] | None = List of attributes to include in the query.
            Defaults to ["id", "title"]

        :return: list[Card] = List of Card model instances

        :raises ValidationError:
            When pipe_id is empty
        :raises ValidationError:
            When attributes is not a list
        :raises UnexpectedResponseError:
            When API response structure is invalid
        :raises ParsingError:
            When response cannot be converted into Card model
        :raises RequestError:
            When request execution fails

        :example:
            >>> service = CardService(PipefyHttpClient(auth_key="token", base_url="https://api.pipefy.com/graphql"))
            >>> callable(service.listAllCardsPaginated)
            True
        """

        class_name, method_name = getExceptionContext(self)

        if not pipe_id:
            raise ValidationError(
                message="pipe_id cannot be empty",
                class_name=class_name,
                method_name=method_name
            )

        if attributes is not None and not isinstance(attributes, list):
            raise ValidationError(
                message="attributes must be a list",
                class_name=class_name,
                method_name=method_name
            )

        attributes = attributes or ["id", "title"]

        try:
            query_attributes: str = QueryBuilder.buildCardAttributes(attributes)
        except Exception as exc:
            raise RequestError(
                message=f"Failed to build query attributes: {str(exc)}",
                class_name=class_name,
                method_name=method_name
            ) from exc

        all_cards: List[Card] = []
        after: Optional[str] = None

        try:
            while True:
                after_param: str = f', after: "{after}"' if after else ''

                query: str = f"""
                   {{
                       allCards(pipeId: {pipe_id}{after_param}) {{
                           pageInfo {{
                               hasNextPage
                               endCursor
                           }}
                           edges {{
                               node {query_attributes}
                           }}
                       }}
                   }}
                   """

                response: Dict[str, Any] = self._client.sendRequest(query, timeout=60)

                data = response.get("data")
                if not isinstance(data, dict):
                    raise UnexpectedResponseError(
                        message="'data' field missing or invalid",
                        class_name=class_name,
                        method_name=method_name
                    )

                all_cards_data = data.get("allCards")
                if not isinstance(all_cards_data, dict):
                    raise UnexpectedResponseError(
                        message="'allCards' field missing",
                        class_name=class_name,
                        method_name=method_name
                    )

                edges = all_cards_data.get("edges")
                page_info = all_cards_data.get("pageInfo")

                if not isinstance(edges, list) or not isinstance(page_info, dict):
                    raise UnexpectedResponseError(
                        message="'edges' or 'pageInfo' invalid",
                        class_name=class_name,
                        method_name=method_name
                    )

                try:
                    parsed_cards: List[Card] = [
                        Card.fromDict(edge.get("node", {}))
                        for edge in edges
                        if isinstance(edge, dict)
                    ]
                except Exception as exc:
                    raise ParsingError(
                        message=f"Failed to parse Card model: {str(exc)}",
                        class_name=class_name,
                        method_name=method_name
                    ) from exc

                all_cards.extend(parsed_cards)

                has_next = page_info.get("hasNextPage")
                after = page_info.get("endCursor")

                if not has_next:
                    break

            return all_cards

        except (ValidationError, UnexpectedResponseError, ParsingError):
            raise

        except Exception as exc:
            raise RequestError(
                message=str(exc),
                class_name=class_name,
                method_name=method_name
            ) from exc

    def listCardsFromPhasePaginated(
            self,
            phase_id: str,
            limit: int = 50
    ) -> List[Card]:
        """
        Retrieve all cards from a specific phase as typed Card models using pagination.

        This method performs cursor-based pagination within a phase and converts
        each card node into a Card model instance.

        :param phase_id: str = Phase ID from which cards will be retrieved
        :param limit: int = Number of items per page (page size)

        :return: list[Card] = List of Card model instances

        :raises ValidationError:
            When phase_id is empty
        :raises ValidationError:
            When limit is not a positive integer
        :raises UnexpectedResponseError:
            When API response structure is invalid
        :raises ParsingError:
            When response cannot be converted into Card model
        :raises RequestError:
            When request execution fails

        :example:
            >>> service = CardService(PipefyHttpClient(auth_key="token", base_url="https://api.pipefy.com/graphql"))
            >>> callable(service.listCardsFromPhasePaginated)
            True
        """

        class_name, method_name = getExceptionContext(self)

        if not phase_id:
            raise ValidationError(
                message="phase_id cannot be empty",
                class_name=class_name,
                method_name=method_name
            )

        if not isinstance(limit, int) or limit <= 0:
            raise ValidationError(
                message="limit must be a positive integer",
                class_name=class_name,
                method_name=method_name
            )

        all_cards: List[Card] = []
        after: Optional[str] = None

        try:
            while True:
                after_param: str = f', after: "{after}"' if after else ''

                query: str = f"""
                {{
                  phase(id: "{phase_id}") {{
                    cards(first: {limit}{after_param}) {{
                      pageInfo {{
                        hasNextPage
                        endCursor
                      }}
                      edges {{
                        node {{
                          id
                          title
                        }}
                      }}
                    }}
                  }}
                }}
                """

                response: Dict[str, Any] = self._client.sendRequest(query, timeout=60)

                data = response.get("data")
                if not isinstance(data, dict):
                    raise UnexpectedResponseError(
                        message="'data' field missing or invalid",
                        class_name=class_name,
                        method_name=method_name
                    )

                phase_data = data.get("phase")
                if not isinstance(phase_data, dict):
                    raise UnexpectedResponseError(
                        message="'phase' field missing",
                        class_name=class_name,
                        method_name=method_name
                    )

                cards_data = phase_data.get("cards")
                if not isinstance(cards_data, dict):
                    raise UnexpectedResponseError(
                        message="'cards' field missing",
                        class_name=class_name,
                        method_name=method_name
                    )

                # 🔥 AQUI ESTÁ A MUDANÇA PRINCIPAL
                paginated = PaginatedResponse.fromDict(
                    cards_data,
                    Card.fromDict
                )

                all_cards.extend(paginated.nodes())

                if not paginated.page_info.hasNextPage:
                    break

                after = paginated.page_info.endCursor

            return all_cards

        except (ValidationError, UnexpectedResponseError, ParsingError):
            raise

        except Exception as exc:
            raise RequestError(
                message=str(exc),
                class_name=class_name,
                method_name=method_name
            ) from exc

    # ============================================================
    # Helper Methods
    # ============================================================

    def _buildGraphQLValues(self, values: List[Dict[str, Any]]) -> str:
        """
        Build GraphQL-compliant values payload.

        Converts Python structures into GraphQL input syntax.

        :param values: list[dict] = Values payload
        :return: str = GraphQL formatted string

        :raises ParsingError:
            When value cannot be serialized

        :example:
            >>> service = CardService(PipefyHttpClient("token", "url"))
            >>> service._buildGraphQLValues([{"fieldId": "x", "value": "y"}])
        """
        try:
            def formatValue(value: Any) -> str:
                if isinstance(value, str):
                    return f'"{value}"'

                if isinstance(value, dict):
                    inner = ", ".join(
                        f'{k}: {formatValue(v)}'
                        for k, v in value.items()
                    )
                    return f'{{{inner}}}'

                if isinstance(value, list):
                    return "[" + ", ".join(formatValue(v) for v in value) + "]"

                return str(value)

            items = []

            for item in values:
                field_id = item["fieldId"]
                value = item["value"]

                items.append(
                    f'{{fieldId: "{field_id}", value: {formatValue(value)}}}'
                )

            return "[" + ", ".join(items) + "]"

        except Exception as exc:
            raise ParsingError(
                message=f"Failed to serialize GraphQL values: {str(exc)}",
                class_name=self.__class__.__name__,
                method_name="_buildGraphQLValues"
            ) from exc

# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    # from pipefy_model import MyPipefyCredentials
    # from infra_core import CredentialsLoader, FernetEncryption
    #
    # TOKEN = CredentialsLoader.load(MyPipefyCredentials, FernetEncryption, name="sharepoint")
    #
    # client = PipefyHttpClient(TOKEN)
    # service = CardService(client)

    pass