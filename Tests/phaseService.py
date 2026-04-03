# ============================================================
# Dependencies
# ============================================================
from infra_core import FernetEncryption, CredentialsLoader
from Credentials import MyPipefyCredentials

from pipefy import Pipefy
import traceback
from typing import Dict, Any
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
# PHASE TESTS
# ============================================================

def testPhaseRaw(api: Pipefy, phase_id: str) -> None:
    """
    Test raw phase retrieval.

    :param api: Pipefy
    :param phase_id: str

    :return: None
    """
    print("\n=== TEST: phases.raw.get ===")

    query_body = """
        id
        name
    """

    result: Dict[str, Any] = api.phases.raw.get(phase_id, query_body)

    assert isinstance(result, dict), "Result must be dict"

    data = result.get("data", {}).get("phase", {})
    assert isinstance(data, dict), "Phase data must be dict"

    pprint(data)
    print("✔ raw OK")


def testPhaseStructured(api: Pipefy, phase_id: str) -> None:
    """
    Test structured phase retrieval.

    :param api: Pipefy
    :param phase_id: str

    :return: None
    """
    print("\n=== TEST: phases.structured.get ===")

    result: Dict[str, Any] = api.phases.structured.get(phase_id)

    assert isinstance(result, dict), "Result must be dict"

    assert "id" in result, "Missing id"
    assert "name" in result, "Missing name"

    fields = result.get("fields", [])
    assert isinstance(fields, list), "Fields must be list"

    print("ID:", result.get("id"))
    print("Name:", result.get("name"))
    print("Fields count:", len(fields))

    print("✔ structured OK")


def testPhaseModel(api: Pipefy, phase_id: str) -> None:
    """
    Test phase model parsing and access patterns.

    :param api: Pipefy
    :param phase_id: str

    :return: None
    """
    print("\n=== TEST: phases.get ===")

    phase = api.phases.get(phase_id)

    assert phase is not None, "Phase must not be None"
    assert hasattr(phase, "id"), "Phase must have id"
    assert hasattr(phase, "name"), "Phase must have name"

    print("ID:", phase.id)
    print("Name:", phase.name)

    assert isinstance(phase.fields, list), "Fields must be list"

    # ============================================================
    # Field access patterns (CRITICAL TEST)
    # ============================================================
    if phase.fields_map:
        first_field = next(iter(phase.fields_map.values()))

        assert hasattr(first_field, "id")
        assert hasattr(first_field, "type")

        field_by_id = phase.getField(first_field.id)
        assert field_by_id.id == first_field.id

        field_direct = phase[first_field.id]
        assert field_direct.id == first_field.id

        print("✔ field access OK")

    # ============================================================
    # Parse errors visibility
    # ============================================================
    if hasattr(phase, "_parse_errors"):
        assert isinstance(phase._parse_errors, list)

    print("✔ model OK")


def testPhaseCustomQuery(api: Pipefy, phase_id: str) -> None:
    """
    Test phase retrieval with custom query.

    :param api: Pipefy
    :param phase_id: str

    :return: None
    """
    print("\n=== TEST: phases.get (custom query) ===")

    query_body = """
        id
        name

        cards(first: 5) {
            edges {
                node {
                    id
                    title
                }
            }
        }
    """

    phase = api.phases.get(phase_id, query_body=query_body)

    assert phase is not None
    assert hasattr(phase, "id")

    print("ID:", phase.id)
    print("Name:", phase.name)

    if hasattr(phase, "cards_preview"):
        assert isinstance(phase.cards_preview, list)

        if phase.cards_preview:
            print("First card:", phase.cards_preview[0])

    print("✔ custom query OK")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    credential_name = 'pipefy'
    credential_name = 'pipefy_automation_factory' # Change to your credential name
    if credential_name == 'pipefy':
        # TIMDECOM
        CARD_ID = "35814650"
        PIPE_ID = "11881"
        PHASE_ID = "83728"
        base_url: str = "https://accenture.pipefy.com/queries"
    elif credential_name == 'pipefy_automation_factory':
        # Automation Factory
        CARD_ID = "1328390184"
        PIPE_ID =  "342616251"  # teste "307087923"    # atuomation "307064875"
        PHASE_ID =  "342616256"  #  automation "342616256" # timdecom "342616251"
        base_url: str = 'https://app.pipefy.com/queries'
    else:
        raise Exception("Invalid credential name")




    api = getApi(credential_name=credential_name, base_url=base_url)

    try:
        # ========================================================
        # CORE FLOW
        # ========================================================
        # testPhaseRaw(api, PHASE_ID)
        # testPhaseStructured(api, PHASE_ID)
        testPhaseModel(api, PHASE_ID)

        # ========================================================
        # ADVANCED
        # ========================================================
        testPhaseCustomQuery(api, PHASE_ID)

        print("\n🎯 ALL TESTS PASSED")

    except Exception as error:
        print("\n❌ TEST FAILED:")
        print(error)
        print(traceback.format_exc())