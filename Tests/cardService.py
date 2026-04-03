
# ============================================================
# Dependencies
# ============================================================
from infra_core import FernetEncryption, CredentialsLoader
from Credentials import MyPipefyCredentials

from pipefy import Pipefy

from pprint import pprint


# ============================================================
# Setup
# ============================================================

def getApi(credential_name: str, base_url: str) -> Pipefy:
    """
    Initialize Pipefy API safely.

    :return: Pipefy = Initialized API client

    :raises Exception:
        When credential loading fails
    """
    if not credential_name:
        raise Exception("Credential name must be set")
    credential = CredentialsLoader.load(
        MyPipefyCredentials,
        FernetEncryption,
        name=credential_name
    )

    return Pipefy(token=credential.api_token, base_url=base_url)


# ============================================================
# Tests
# ============================================================

def testRawCard(api: Pipefy, card_id: str) -> None:
    """
    Test raw card query execution.

    :param api: Pipefy
    :param card_id: str

    :return: None
    """
    print("\n=== TEST: cards.raw.get ===")

    query = """
    fields {
      field {
        id
      }
      value
    }
    """

    result = api.cards.raw.get(card_id, query)

    assert isinstance(result, dict), "Result must be dict"

    data = result.get("data", {}).get("card", {})
    assert isinstance(data, dict), "Card data must be dict"

    pprint(data)
    print("✔ raw OK")


def testStructured(api: Pipefy, card_id: str) -> None:
    """
    Test structured card retrieval.

    :param api: Pipefy
    :param card_id: str

    :return: None
    """
    print("\n=== TEST: cards.structured.get ===")

    result = api.cards.structured.get(card_id)

    assert isinstance(result, dict), "Result must be dict"

    pprint(result)
    print("✔ structured OK")


def testStructuredCustomQuery(api: Pipefy, card_id: str) -> None:
    """
    Test structured card retrieval with custom query.

    :param api: Pipefy
    :param card_id: str

    :return: None
    """
    print("\n=== TEST: cards.structured.get (custom) ===")

    query = """
        fields {
            field {
                id
            }
            value
        }
    """

    result = api.cards.structured.get(card_id, query)

    assert isinstance(result, dict), "Result must be dict"

    pprint(result)
    print("✔ structured custom OK")


def testModel(api: Pipefy, card_id: str) -> None:
    """
    Test card model retrieval.

    :param api: Pipefy
    :param card_id: str

    :return: None
    """
    print("\n=== TEST: cards.get ===")

    card = api.cards.get(card_id)

    assert card is not None, "Card must not be None"
    assert hasattr(card, "id"), "Card must have id"
    assert hasattr(card, "title"), "Card must have title"

    print("ID:", card.id)
    print("Title:", card.title)

    print("✔ model OK")


def testListAllCards(api: Pipefy, pipe_id: str) -> None:
    """
    Test listing all cards from pipe.

    :param api: Pipefy
    :param pipe_id: str

    :return: None
    """
    print("\n=== TEST: cards.list ===")

    cards = api.cards.list(pipe_id)

    assert isinstance(cards, list), "Cards must be list"

    print("Total cards:", len(cards))
    print("✔ list pipe OK")


def testListCardsFromPhase(api: Pipefy, phase_id: str) -> None:
    """
    Test listing cards from a phase.

    :param api: Pipefy
    :param phase_id: str

    :return: None
    """
    print("\n=== TEST: phases.listCards ===")

    cards = api.phases.listCards(phase_id)

    assert isinstance(cards, list), "Cards must be list"

    print("Total cards:", len(cards))
    print("✔ list phase OK")



def testPaginationPipe(api: Pipefy, pipe_id: str) -> None:
    """
    Test paginated retrieval from pipe.

    :param api: Pipefy
    :param pipe_id: str

    :return: None
    """
    print("\n=== TEST: cards.list (paginated) ===")

    cards = api.cards.list(pipe_id)

    assert isinstance(cards, list)

    for card in cards[:5]:
        assert hasattr(card, "id")

    print("✔ pagination pipe OK")


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    credential_name = 'pipefy'
    credential_name = 'pipefy_automation_factory'

    if credential_name == 'pipefy':
        # TIMDECOM
        CARD_ID = "35814650"
        PIPE_ID = "11881"
        PHASE_ID = "83728"
        base_url: str = "https://accenture.pipefy.com/queries"
    elif credential_name == 'pipefy_automation_factory':
        # Automation Factory
        CARD_ID = "1328390184"
        PIPE_ID = "307064875"
        PHASE_ID = "342616251"
        base_url: str = 'https://app.pipefy.com/queries'
    else:
        raise Exception("Invalid credential name")

    api = getApi(credential_name=credential_name, base_url=base_url)

    try:
        # testRawCard(api, CARD_ID)
        # testStructured(api, CARD_ID)
        # testStructuredCustomQuery(api, CARD_ID)
        testModel(api, CARD_ID)

        testListAllCards(api, PIPE_ID)
        testListCardsFromPhase(api, PHASE_ID)

        testPaginationPipe(api, PIPE_ID)

        print("\n🎯 ALL TESTS PASSED")

    except Exception as error:
        print("\n❌ TEST FAILED:")
        print(error)
# ============================================================
# Main
# ============================================================
