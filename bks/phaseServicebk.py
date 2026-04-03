# ============================================================
# Dependencies
# ============================================================
import inspect
from typing import Any, Dict, List, Optional

from pipefy.client.httpClient import PipefyHttpClient
from pipefy.exceptions import RequestError
from typing import Generator
from pipefy.models.card import Card
from typing import List

from pipefy.models.phase import Phase


class PhaseService:
    """
    Service responsible for phase operations in Pipefy.

    This service provides access to:
    - Phase details
    - Phase fields
    - Cards within phases (basic access)

    It complements PipeService by isolating phase-level logic.

    :example:
        >>> client = PipefyHttpClient("token")
        >>> service = PhaseService(client)
        >>> isinstance(service, PhaseService)
        True
    """

    def __init__(self, client: PipefyHttpClient) -> None:
        """
        Initialize PhaseService.

        :param client: PipefyHttpClient = HTTP client instance

        :example:
            >>> service = PhaseService(PipefyHttpClient("token"))
        """
        self._client: PipefyHttpClient = client

    # ============================================================
    # Phase Info
    # ============================================================

    def getPhaseInfo(self, phase_id: str) -> Dict[str, Any]:
        """
        Retrieve basic information about a phase.

        :param phase_id: str = Phase ID

        :return: dict = Phase data

        :raises RequestError:
            When request fails

        :example:
            >>> service = PhaseService(PipefyHttpClient("token"))
            >>> isinstance(service.getPhaseInfo("1"), dict)
            True
        """
        try:
            query = f"""
            {{
                phase(id: "{phase_id}") {{
                    id
                    name
                }}
            }}
            """
            return self._client.sendRequest(query, timeout=60)

        except Exception as exc:
            raise RequestError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: getPhaseInfo\n"
                f"Error: {str(exc)}"
            ) from exc

    # ============================================================
    # Phase Fields
    # ============================================================

    def getPhaseFields(self, phase_id: str) -> Dict[str, Any]:
        """
        Retrieve fields available in a phase.

        :param phase_id: str = Phase ID

        :return: dict = Fields data

        :raises RequestError:
            When request fails

        :example:
            >>> service = PhaseService(PipefyHttpClient("token"))
            >>> isinstance(service.getPhaseFields("1"), dict)
            True
        """
        try:
            query = f"""
            {{
                phase(id: "{phase_id}") {{
                    fields {{
                        id
                        label
                        type
                    }}
                }}
            }}
            """
            return self._client.sendRequest(query, timeout=60)

        except Exception as exc:
            raise RequestError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: getPhaseFields\n"
                f"Error: {str(exc)}"
            ) from exc

    # ============================================================
    # Phase Cards (Basic)
    # ============================================================

    def getPhaseCards(
        self,
        phase_id: str,
        first: int = 50
    ) -> Dict[str, Any]:
        """
        Retrieve cards from a phase (single page).

        :param phase_id: str = Phase ID
        :param first: int = Number of cards to retrieve

        :return: dict = Cards data

        :raises RequestError:
            When request fails

        :example:
            >>> service = PhaseService(PipefyHttpClient("token"))
            >>> isinstance(service.getPhaseCards("1"), dict)
            True
        """
        try:
            query = f"""
            {{
                phase(id: "{phase_id}") {{
                    cards(first: {first}) {{
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
            return self._client.sendRequest(query, timeout=60)

        except Exception as exc:
            raise RequestError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: getPhaseCards\n"
                f"Error: {str(exc)}"
            ) from exc

    # ============================================================
    # Phase Cards (IDs only - helper)
    # ============================================================

    def listPhaseCardIds(
        self,
        phase_id: str
    ) -> List[str]:
        """
        Retrieve all card IDs from a phase (single page).

        :param phase_id: str = Phase ID

        :return: list[str] = List of card IDs

        :raises RequestError:
            When request fails

        :example:
            >>> service = PhaseService(PipefyHttpClient("token"))
            >>> isinstance(service.listPhaseCardIds("1"), list)
            True
        """
        try:
            response = self.getPhaseCards(phase_id)

            edges = (
                response
                .get("data", {})
                .get("phase", {})
                .get("cards", {})
                .get("edges", [])
            )

            return [edge.get("node", {}).get("id") for edge in edges if edge.get("node")]

        except Exception as exc:
            raise RequestError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: listPhaseCardIds\n"
                f"Error: {str(exc)}"
            ) from exc

    def iterPhaseCards(
            self,
            phase_id: str,
            limit: int = 50
    ) -> Generator[Card, None, None]:
        """
        Iterate over cards in a phase using pagination (lazy loading).

        This method yields cards one by one, avoiding loading all data into memory.

        :param phase_id: str = Phase ID
        :param limit: int = Number of cards per request

        :yield: Card = Card model instance

        :raises RequestError:
            When request fails

        :example:
            >>> service = PhaseService(PipefyHttpClient("token"))
            >>> callable(service.iterPhaseCards)
            True
        """
        try:
            after: Optional[str] = None

            while True:
                after_param = f', after: "{after}"' if after else ''

                query = f"""
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

                response = self._client.sendRequest(query, timeout=60)

                cards_data = (
                    response
                    .get("data", {})
                    .get("phase", {})
                    .get("cards", {})
                )

                edges = cards_data.get("edges", [])
                page_info = cards_data.get("pageInfo", {})

                for edge in edges:
                    node = edge.get("node", {})
                    yield Card(**node)

                if not page_info.get("hasNextPage"):
                    break

                after = page_info.get("endCursor")

        except Exception as exc:
            raise RequestError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: iterPhaseCards\n"
                f"Error: {str(exc)}"
            ) from exc

    def listPhaseCardsPaginated(
            self,
            phase_id: str,
            limit: int = 50
    ) -> List[Card]:
        """
        Retrieve all cards from a phase as a list of models.

        :param phase_id: str = Phase ID
        :param limit: int = Page size

        :return: list[Card]

        :raises RequestError:

        :example:
            >>> service = PhaseService(PipefyHttpClient("token"))
            >>> isinstance(service.listPhaseCardsPaginated("1"), list)
            True
        """
        try:
            return list(self.iterPhaseCards(phase_id, limit))

        except Exception as exc:
            raise RequestError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: listPhaseCardsPaginated\n"
                f"Error: {str(exc)}"
            ) from exc

    def getPhaseModel(self, phase_id: str) -> Phase:
        """
        Retrieve phase as a typed model.

        :param phase_id: str = Phase ID

        :return: Phase

        :raises RequestError:

        :example:
            >>> service = PhaseService(PipefyHttpClient("token"))
            >>> isinstance(service.getPhaseModel("1"), Phase)
            True
        """
        try:
            response = self.getPhaseInfo(phase_id)
            return Phase.fromResponse(response)

        except Exception as exc:
            raise RequestError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: getPhaseModel\n"
                f"Error: {str(exc)}"
            ) from exc

    def getPhaseWithFieldsModel(self, phase_id: str) -> Phase:
        """
        Retrieve phase including fields as model.

        :param phase_id: str

        :return: Phase
        """
        try:
            response = self.getPhaseFields(phase_id)
            return Phase.fromResponse(response)

        except Exception as exc:
            raise RequestError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: getPhaseWithFieldsModel\n"
                f"Error: {str(exc)}"
            ) from exc


# ============================================================
# Main (Usage Example)
# ============================================================

if __name__ == "__main__":
    """
    Simple execution example.
    """

    try:
        TOKEN = ""
        PHASE_ID = "83728"


        client = PipefyHttpClient(TOKEN)
        service = PhaseService(client)

        # ====================================================
        # 1. Phase Info (Model)
        # ====================================================
        print("\n--- Phase Info (Model) ---")
        phase_model = service.getPhaseModel(phase_id=PHASE_ID)

        print("ID:", phase_model.id)
        print("Name:", phase_model.name)

        # ====================================================
        # 2. Phase Fields (Model)
        # ====================================================
        print("\n--- Phase Fields (Model) ---")
        phase_with_fields = service.getPhaseWithFieldsModel(phase_id=PHASE_ID)

        for field in phase_with_fields.fields:
            print(field.id, field.label, field.type)

        # ====================================================
        # 3. Cards (Single Page - legado mantido)
        # ====================================================
        print("\n--- Phase Cards (Single Page - Raw) ---")
        cards = service.getPhaseCards(phase_id=PHASE_ID)

        edges = (
            cards
            .get("data", {})
            .get("phase", {})
            .get("cards", {})
            .get("edges", [])
        )

        for edge in edges:
            node = edge.get("node", {})
            print(node.get("id"), node.get("title"))

        # ====================================================
        # 4. Card IDs Only
        # ====================================================
        print("\n--- Card IDs ---")
        card_ids = service.listPhaseCardIds(phase_id=PHASE_ID)

        print(f"Total IDs: {len(card_ids)}")
        for cid in card_ids[:5]:
            print(cid)

        # ====================================================
        # 5. Iterator (Lazy Pagination - Model)
        # ====================================================
        print("\n--- Iterating Cards (Model - Lazy) ---")
        count = 0

        for card in service.iterPhaseCards(phase_id=PHASE_ID):
            print(card.id, card.title)

            count += 1
            if count >= 5:
                break

        # ====================================================
        # 6. Full Pagination (List - Model)
        # ====================================================
        print("\n--- All Cards (Paginated - Model) ---")
        all_cards = service.listPhaseCardsPaginated(phase_id=PHASE_ID)

        print(f"Total cards: {len(all_cards)}")

        for card in all_cards[:5]:
            print(card.id, card.title)

    except Exception as error:
        print("\nError occurred:")
        print(error)