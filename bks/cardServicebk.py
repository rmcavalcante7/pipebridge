# ============================================================
# Dependencies
# ============================================================
import json
from typing import Any, Dict, List, Optional

from pipefy.client.httpClient import PipefyHttpClient
from pipefy.builders.queryBuilder import QueryBuilder
from pipefy.exceptions import RequestError
from pipefy.models.card import Card
from pipefy.models.pagination import PageInfo, Edge, PaginatedResponse


class CardService:
    """
    Service responsible for card operations in Pipefy.

    This class centralizes all card-related operations such as:
    - creation
    - retrieval
    - movement
    - search
    - pagination
    - relationships

    :example:
        >>> service = CardService(PipefyHttpClient("token"))
        >>> isinstance(service, CardService)
        True
    """

    def __init__(self, client: PipefyHttpClient) -> None:
        """
        Initialize CardService.

        :param client: PipefyHttpClient = HTTP client instance

        :example:
            >>> client = PipefyHttpClient("token")
            >>> service = CardService(client)
        """
        self._client: PipefyHttpClient = client

    # ============================================================
    # Basic Operations
    # ============================================================

    def createCard(
            self,
            pipe_id: str,
            title: str,
            fields: List[List[str]]
    ) -> Dict[str, Any]:
        """
        Create a new card in a Pipefy pipe.

        This method builds and executes a GraphQL mutation to create a card
        with the provided title and field values.

        :param pipe_id: str = Pipe ID where the card will be created
        :param title: str = Card title
        :param fields: list[list[str]] = List of [field_id, field_value] pairs

        :return: dict = Raw API response containing created card data

        :raises RequestError:
            When request execution fails
        :raises RequestError:
            When payload serialization fails
        :raises RequestError:
            When API returns an unexpected structure

        :example:
            >>> service = CardService(PipefyHttpClient("token"))
            >>> isinstance(service.createCard("1", "Test Card", []), dict)
            True
        """
        try:
            fields_payload: List[Dict[str, Any]] = [
                {"field_id": field_id, "field_value": field_value}
                for field_id, field_value in fields
                if field_value
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

            response: Dict[str, Any] = self._client.sendRequest(query, timeout=60)

            return response

        except Exception as exc:
            raise RequestError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: createCard\n"
                f"Error: {str(exc)}"
            ) from exc

    def getRawCard(
            self,
            card_id: str,
            query_body: str
    ) -> Dict[str, Any]:
        """
        Execute a raw GraphQL query for a card.

        This method provides full control over the GraphQL query structure,
        allowing the caller to define exactly which fields should be retrieved.

        This is the official low-level method for retrieving card data.

        :param card_id: str = Card ID
        :param query_body: str = GraphQL body inside `card { ... }`

        :return: dict = Raw API response

        :raises RequestError:
            When request execution fails

        :example:
            >>> client = PipefyHttpClient("token")
            >>> service = CardService(client)
            >>> query = "id title"
            >>> callable(service.getRawCard)
            True
        """
        try:
            query: str = f"""
            {{
              card(id: {card_id}) {{
                {query_body}
              }}
            }}
            """

            response: Dict[str, Any] = self._client.sendRequest(query, timeout=60)

            return response

        except Exception as exc:
            raise RequestError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: getRawCard\n"
                f"Error: {str(exc)}"
            ) from exc

    # ============================================================
    # Structured (High-Level)
    # ============================================================

    def getCardStructured(
            self,
            card_id: str,
            field_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Retrieve a card using a predefined structured query.

        This method abstracts GraphQL complexity and returns a consistent,
        rich dataset including phases, fields, labels, and assignees.

        NOTE:
            Pipefy GraphQL does NOT support filtering fields at query level.
            Field filtering is handled after response parsing.

        :param card_id: str = Card ID
        :param field_ids: list[str] | None = Optional list of field IDs to filter

        :return: dict = Structured card data

        :raises RequestError:
            When request execution fails
        :raises RequestError:
            When API response structure is invalid

        :example:
            >>> client = PipefyHttpClient("token")
            >>> service = CardService(client)
            >>> callable(service.getCardStructured)
            True
        """
        try:
            query_body: str = """
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
            """

            response: Dict[str, Any] = self.getRawCard(card_id, query_body)

            # ============================================================
            # SAFE EXTRACTION
            # ============================================================
            data: Dict[str, Any] = response.get("data", {})
            card_data: Dict[str, Any] = data.get("card", {})

            if not card_data:
                raise ValueError("Card not found in API response")

            # ============================================================
            # FIELD FILTERING (CORE FIX)
            # ============================================================
            if field_ids:
                fields: List[Dict[str, Any]] = card_data.get("fields", [])

                filtered_fields: List[Dict[str, Any]] = []

                for field in fields:
                    field_meta: Dict[str, Any] = field.get("field") or {}

                    field_id: Optional[str] = field_meta.get("id")

                    if field_id and field_id in field_ids:
                        filtered_fields.append(field)

                card_data["fields"] = filtered_fields

            return card_data

        except Exception as exc:
            raise RequestError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: getCardStructured\n"
                f"Error: {str(exc)}"
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

        :raises RequestError:
            When request execution fails
        :raises RequestError:
            When API response structure is invalid

        :example:
            >>> service = CardService(PipefyHttpClient("token"))
            >>> isinstance(service.moveCardToPhase("1", "1"), dict)
            True
        """
        try:
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

            response: Dict[str, Any] = self._client.sendRequest(query, timeout=60)

            return response

        except Exception as exc:
            raise RequestError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: moveCardToPhase\n"
                f"Error: {str(exc)}"
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

        :raises RequestError:
            When request execution fails
        :raises RequestError:
            When API response structure is invalid or missing expected fields

        :example:
            >>> service = CardService(PipefyHttpClient("token"))
            >>> isinstance(service.searchCards("1", "Test"), list)
            True
        """
        try:
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

            response: Dict[str, Any] = self._client.sendRequest(query, timeout=60)

            edges: List[Dict[str, Any]] = (
                response
                .get("data", {})
                .get("cards", {})
                .get("edges", [])
            )

            return [edge.get("node", {}) for edge in edges if edge.get("node")]

        except Exception as exc:
            raise RequestError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: searchCards\n"
                f"Error: {str(exc)}"
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

        :raises RequestError:
            When request execution fails
        :raises RequestError:
            When API response structure is invalid

        :example:
            >>> service = CardService(PipefyHttpClient("token"))
            >>> isinstance(service.relateCards("1", "2", "3"), dict)
            True
        """
        try:
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

            response: Dict[str, Any] = self._client.sendRequest(query, timeout=60)

            return response

        except Exception as exc:
            raise RequestError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: relateCards\n"
                f"Error: {str(exc)}"
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

        :raises RequestError:
            When attribute query building fails
        :raises RequestError:
            When request execution fails
        :raises RequestError:
            When API response structure is invalid or incomplete

        :example:
            >>> service = CardService(PipefyHttpClient("token"))
            >>> isinstance(service.listAllCards("1"), list)
            True
        """
        try:
            attributes = attributes or ["id", "title"]

            query_attributes: str = QueryBuilder.buildCardAttributes(attributes)

            all_cards: List[Dict[str, Any]] = []
            after: Optional[str] = None

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

                data: Dict[str, Any] = (
                    response
                    .get("data", {})
                    .get("allCards", {})
                )

                edges: List[Dict[str, Any]] = data.get("edges", [])
                page_info: Dict[str, Any] = data.get("pageInfo", {})

                for edge in edges:
                    node: Dict[str, Any] = edge.get("node", {})

                    if only_phase_name:
                        phase_name: Optional[str] = (
                            node
                            .get("current_phase", {})
                            .get("name")
                        )
                        if phase_name != only_phase_name:
                            continue

                    all_cards.append(node)

                if not page_info.get("hasNextPage"):
                    break

                after = page_info.get("endCursor")

            return all_cards

        except Exception as exc:
            raise RequestError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: listAllCards\n"
                f"Error: {str(exc)}"
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

        :raises RequestError:
            When request execution fails
        :raises RequestError:
            When API response structure is invalid or incomplete

        :example:
            >>> service = CardService(PipefyHttpClient("token"))
            >>> isinstance(service.listCardsFromPhase("1"), list)
            True
        """
        try:
            all_cards: List[Dict[str, Any]] = []
            after: Optional[str] = None

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

                cards_data: Dict[str, Any] = (
                    response
                    .get("data", {})
                    .get("phase", {})
                    .get("cards", {})
                )

                edges: List[Dict[str, Any]] = cards_data.get("edges", [])
                page_info: Dict[str, Any] = cards_data.get("pageInfo", {})

                for edge in edges:
                    node: Dict[str, Any] = edge.get("node", {})
                    if node:
                        all_cards.append(node)

                if not page_info.get("hasNextPage"):
                    break

                after = page_info.get("endCursor")

            return all_cards

        except Exception as exc:
            raise RequestError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: listCardsFromPhase\n"
                f"Error: {str(exc)}"
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

        :raises RequestError:
            When request execution fails
        :raises RequestError:
            When API response structure is invalid

        :example:
            >>> service = CardService(PipefyHttpClient("token"))
            >>> isinstance(service.deleteCard("1"), dict)
            True
        """
        try:
            query: str = f"""
            mutation {{
                deleteCard(input: {{ id: {card_id} }}) {{
                    success
                }}
            }}
            """

            response: Dict[str, Any] = self._client.sendRequest(query, timeout=60)

            return response

        except Exception as exc:
            raise RequestError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: deleteCard\n"
                f"Error: {str(exc)}"
            ) from exc

    def updateField(
            self,
            card_id: str,
            field_id: str,
            value: str
    ) -> Dict[str, Any]:
        """
        Update a single field of a card.

        This is a convenience wrapper over updateFields,
        simplifying usage for single field updates.

        :param card_id: str = Card identifier
        :param field_id: str = Field identifier
        :param value: str = Field value

        :return: dict = Raw API response

        :raises RequestError:
            When request execution fails

        :example:
            >>> service = CardService(PipefyHttpClient("token"))
            >>> callable(service.updateField)
            True
        """
        try:
            return self.updateFields(
                card_id=card_id,
                fields={field_id: value}
            )

        except Exception as exc:
            raise RequestError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: updateField\n"
                f"Error: {str(exc)}"
            ) from exc

    def updateFields(
            self,
            card_id: str,
            fields: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update multiple fields of a card.

        This method updates multiple card fields using a dictionary
        mapping field IDs to their respective values.

        :param card_id: str = Card identifier
        :param fields: dict[str, Any] = Mapping of field_id to value

        :return: dict = Raw API response

        :raises RequestError:
            When payload serialization fails
        :raises RequestError:
            When request execution fails
        :raises RequestError:
            When API response structure is invalid

        :example:
            >>> service = CardService(PipefyHttpClient("token"))
            >>> callable(service.updateFields)
            True
        """
        try:
            if not isinstance(fields, dict):
                raise ValueError("fields must be a dictionary")

            values: List[Dict[str, Any]] = [
                {"fieldId": field_id, "value": value}
                for field_id, value in fields.items()
                if value is not None
            ]

            query: str = f"""
            mutation {{
                updateFieldsValues(input: {{
                    nodeId: {card_id},
                    values: {json.dumps(values)}
                }}) {{
                    success
                }}
            }}
            """

            response: Dict[str, Any] = self._client.sendRequest(query, timeout=60)

            return response

        except Exception as exc:
            raise RequestError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: updateFields\n"
                f"Error: {str(exc)}"
            ) from exc

    def updateCardField(
            self,
            card_id: str,
            field_id: str,
            new_value: Any
    ) -> Dict[str, Any]:
        """
        Update a single field of a card using GraphQL variables.

        This method executes a GraphQL mutation using variables to safely update
        a single field value of a card.

        :param card_id: str = Card ID to be updated
        :param field_id: str = Field ID to be updated
        :param new_value: Any = New value to assign to the field

        :return: dict = Raw API response indicating operation success

        :raises RequestError:
            When request execution fails
        :raises RequestError:
            When variables payload is invalid
        :raises RequestError:
            When API response structure is invalid

        :example:
            >>> service = CardService(PipefyHttpClient("token"))
            >>> isinstance(service.updateCardField("1", "field", "value"), dict)
            True
        """
        try:
            query: str = """
            mutation UpdateSingleField($cardId: ID!, $fieldId: ID!, $newValue: [UndefinedInput]) {
                updateCardField(input: {
                    card_id: $cardId,
                    field_id: $fieldId,
                    new_value: $newValue
                }) {
                    success
                }
            }
            """

            variables: Dict[str, Any] = {
                "cardId": card_id,
                "fieldId": field_id,
                "newValue": new_value
            }

            response: Dict[str, Any] = self._client.sendRequest(query, variables, 60)

            return response

        except Exception as exc:
            raise RequestError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: updateCardField\n"
                f"Error: {str(exc)}"
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

        :raises RequestError:
            When request execution fails
        :raises RequestError:
            When payload serialization fails
        :raises RequestError:
            When API response structure is invalid

        :example:
            >>> service = CardService(PipefyHttpClient("token"))
            >>> isinstance(service.updateAssigneeIds("1", []), dict)
            True
        """
        try:
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

            response: Dict[str, Any] = self._client.sendRequest(query, timeout=60)

            return response

        except Exception as exc:
            raise RequestError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: updateAssigneeIds\n"
                f"Error: {str(exc)}"
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

        :raises RequestError:
            When request execution fails
        :raises RequestError:
            When payload serialization fails
        :raises RequestError:
            When API response structure is invalid

        :example:
            >>> service = CardService(PipefyHttpClient("token"))
            >>> isinstance(service.updateLabelIds("1", []), dict)
            True
        """
        try:
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

            response: Dict[str, Any] = self._client.sendRequest(query, timeout=60)

            return response

        except Exception as exc:
            raise RequestError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: updateLabelIds\n"
                f"Error: {str(exc)}"
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

        :raises RequestError:
            When request execution fails
        :raises RequestError:
            When response parsing fails

        :example:
            >>> service = CardService(PipefyHttpClient("token"))
            >>> callable(service.getCardModel)
            True
        """
        try:
            card_data: Dict[str, Any] = self.getCardStructured(
                card_id,
                query_body
            )

            if not card_data:
                raise ValueError("Empty card data returned from getCardStructured")

            return Card.fromDict(card_data)

        except Exception as exc:
            raise RequestError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: getCardModel\n"
                f"Error: {str(exc)}"
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

        :raises RequestError:
            When attribute query building fails
        :raises RequestError:
            When request execution fails
        :raises RequestError:
            When response parsing into Card model fails
        :raises RequestError:
            When API response structure is invalid

        :example:
            >>> service = CardService(PipefyHttpClient("token"))
            >>> isinstance(service.listAllCardsPaginated("1"), list)
            True
        """
        try:
            attributes = attributes or ["id", "title"]

            query_attributes: str = QueryBuilder.buildCardAttributes(attributes)

            all_cards: List[Card] = []
            after: Optional[str] = None

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

                data: Dict[str, Any] = (
                    response
                    .get("data", {})
                    .get("allCards", {})
                )

                page_info_data: Dict[str, Any] = data.get("pageInfo", {})

                page_info: PageInfo = PageInfo(
                    hasNextPage=page_info_data.get("hasNextPage", False),
                    endCursor=page_info_data.get("endCursor")
                )

                edges: List[Edge] = [
                    Edge(Card.fromDict(edge.get("node", {})))
                    for edge in data.get("edges", [])
                ]

                paginated: PaginatedResponse = PaginatedResponse(edges, page_info)

                all_cards.extend(paginated.nodes())

                if not paginated.page_info.hasNextPage:
                    break

                after = paginated.page_info.endCursor

            return all_cards

        except Exception as exc:
            raise RequestError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: listAllCardsPaginated\n"
                f"Error: {str(exc)}"
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

        :raises RequestError:
            When request execution fails
        :raises RequestError:
            When response parsing into Card model fails
        :raises RequestError:
            When API response structure is invalid or incomplete

        :example:
            >>> service = CardService(PipefyHttpClient("token"))
            >>> isinstance(service.listCardsFromPhasePaginated("1"), list)
            True
        """
        try:
            all_cards: List[Card] = []
            after: Optional[str] = None

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

                phase_data: Dict[str, Any] = (
                    response
                    .get("data", {})
                    .get("phase", {})
                )

                cards_data: Dict[str, Any] = phase_data.get("cards", {})

                page_info_data: Dict[str, Any] = cards_data.get("pageInfo", {})

                page_info: PageInfo = PageInfo(
                    hasNextPage=page_info_data.get("hasNextPage", False),
                    endCursor=page_info_data.get("endCursor")
                )

                edges: List[Edge] = [
                    Edge(Card.fromDict(edge.get("node", {})))
                    for edge in cards_data.get("edges", [])
                ]

                paginated: PaginatedResponse = PaginatedResponse(edges, page_info)

                all_cards.extend(paginated.nodes())

                if not paginated.page_info.hasNextPage:
                    break

                after = paginated.page_info.endCursor

            return all_cards

        except Exception as exc:
            raise RequestError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: listCardsFromPhasePaginated\n"
                f"Error: {str(exc)}"
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