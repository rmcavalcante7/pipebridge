"""
GraphQL query builders for card-related operations.
"""

import json
from typing import Any, Optional


class CardQueries:
    """
    Factory for card GraphQL queries.

    The service layer provides the dynamic values and receives the final query
    string ready for execution.
    """

    @staticmethod
    def getById(card_id: str, query_body: str) -> str:
        """
        Build a card-by-id query.

        :param card_id: str = Card identifier
        :param query_body: str = GraphQL fields to retrieve inside the card

        :return: str = GraphQL query
        """
        return f"""
        {{
          card(id: {card_id}) {{
            {query_body}
          }}
        }}
        """

    @staticmethod
    def searchByTitle(pipe_id: str, title: str) -> str:
        """
        Build a card search query by title within a pipe.

        :param pipe_id: str = Pipe identifier
        :param title: str = Card title filter

        :return: str = GraphQL query
        """
        return f"""
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

    @staticmethod
    def listAllCards(
        pipe_id: str,
        query_attributes: str,
        after: Optional[str] = None,
        filters: Optional[dict[str, Any]] = None,
    ) -> str:
        """
        Build the paginated all-cards query for a pipe.

        :param pipe_id: str = Pipe identifier
        :param query_attributes: str = Card node attributes
        :param after: str | None = Pagination cursor
        :param filters: dict[str, Any] | None = Optional allCards filter payload

        :return: str = GraphQL query
        """
        after_param = f', after: "{after}"' if after else ""
        filter_param = f", filter: {json.dumps(filters)}" if filters else ""
        return f"""
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

    @staticmethod
    def listCardsFromPhase(
        phase_id: str,
        limit: int,
        after: Optional[str] = None,
        query_body: str = """
            id
            title
        """,
    ) -> str:
        """
        Build the paginated query that lists cards from a phase.

        :param phase_id: str = Phase identifier
        :param limit: int = Page size
        :param after: str | None = Pagination cursor
        :param query_body: str = Card node selection body

        :return: str = GraphQL query
        """
        after_param = f', after: "{after}"' if after else ""
        return f"""
        {{
          phase(id: "{phase_id}") {{
            cards(first: {limit}{after_param}) {{
              pageInfo {{
                hasNextPage
                endCursor
              }}
              edges {{
                node {{
                  {query_body}
                }}
              }}
            }}
          }}
        }}
        """
