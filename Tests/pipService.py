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
# PIPE TESTS
# ============================================================

def testPipeRaw(api: Pipefy, pipe_id: str) -> None:
    """
    Test raw pipe retrieval.

    :param api: Pipefy
    :param pipe_id: str

    :return: None
    """
    print("\n=== TEST: pipes.raw.get ===")

    query_body = """
        id
        name
    """

    result: Dict[str, Any] = api.pipes.raw.get(pipe_id, query_body)

    assert isinstance(result, dict), "Result must be dict"

    data = result.get("data", {}).get("pipe", {})
    assert isinstance(data, dict), "Pipe data must be dict"

    pprint(data)
    print("✔ raw OK")


def testPipeStructured(api: Pipefy, pipe_id: str) -> None:
    """
    Test structured pipe retrieval.

    :param api: Pipefy
    :param pipe_id: str

    :return: None
    """
    print("\n=== TEST: pipes.structured.get ===")

    result: Dict[str, Any] = api.pipes.structured.get(pipe_id)

    assert isinstance(result, dict), "Result must be dict"

    assert "id" in result, "Missing id"
    assert "name" in result, "Missing name"

    assert isinstance(result.get("phases", []), list)
    assert isinstance(result.get("labels", []), list)
    assert isinstance(result.get("users", []), list)

    print("ID:", result["id"])
    print("Name:", result["name"])
    print("Phases:", len(result.get("phases", [])))

    print("✔ structured OK")


def testPipeModel(api: Pipefy, pipe_id: str) -> None:
    """
    Test pipe model parsing and access patterns.

    :param api: Pipefy
    :param pipe_id: str

    :return: None
    """
    print("\n=== TEST: pipes.get ===")

    pipe = api.pipes.get(pipe_id)

    assert pipe is not None, "Pipe must not be None"
    assert hasattr(pipe, "id")
    assert hasattr(pipe, "name")

    print("ID:", pipe.id)
    print("Name:", pipe.name)
    print("Organization:", pipe.organization_id)
    print("Cards:", pipe.cards_count)

    assert isinstance(pipe.phases, list)
    assert isinstance(pipe.labels, list)
    assert isinstance(pipe.users, list)

    # ============================================================
    # O(1) ACCESS TESTS
    # ============================================================

    if pipe.phases_map:
        first_phase = next(iter(pipe.phases_map.values()))

        phase_by_id = pipe.getPhase(first_phase.id)
        assert phase_by_id.id == first_phase.id

        phase_direct = pipe[first_phase.id]
        assert phase_direct.id == first_phase.id

        print("✔ phase access OK")

    if pipe.labels_map:
        first_label = next(iter(pipe.labels_map.values()))

        label = pipe.getLabel(first_label.id)
        assert label.id == first_label.id

        print("✔ label access OK")

    if pipe.users_map:
        first_user = next(iter(pipe.users_map.values()))

        user = pipe.getUser(first_user.id)

        assert user.id == first_user.id
        assert hasattr(user, "name")
        assert hasattr(user, "email")

        print("✔ user access OK")

    # ============================================================
    # Parse errors visibility
    # ============================================================

    if hasattr(pipe, "_parse_errors"):
        assert isinstance(pipe._parse_errors, list)

    print("✔ model OK")


def testPipeCustomQuery(api: Pipefy, pipe_id: str) -> None:
    """
    Test pipe retrieval with custom query.

    :param api: Pipefy
    :param pipe_id: str

    :return: None
    """
    print("\n=== TEST: pipes.get (custom query) ===")

    query_body = """
        id
        name

        phases {
            id
            name
            fields {
                id
                label
                type
            }
        }
    """

    pipe = api.pipes.get(pipe_id, query_body=query_body)

    assert pipe is not None
    assert hasattr(pipe, "id")

    print("ID:", pipe.id)
    print("Name:", pipe.name)

    assert isinstance(pipe.phases, list)

    if pipe.phases:
        first_phase = pipe.phases[0]

        assert hasattr(first_phase, "id")

        if hasattr(first_phase, "fields"):
            assert isinstance(first_phase.fields, list)

    print("✔ custom query OK")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    credential_name = 'pipefy'
    credential_name = 'pipefy_automation_factory'  # Change to your credential name
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
        # ========================================================
        # CORE FLOW
        # ========================================================
        testPipeRaw(api, PIPE_ID)
        testPipeStructured(api, PIPE_ID)
        testPipeModel(api, PIPE_ID)

        # ========================================================
        # ADVANCED
        # ========================================================
        testPipeCustomQuery(api, PIPE_ID)

        print("\n🎯 ALL TESTS PASSED")

    except Exception as error:
        print("\n❌ TEST FAILED:")
        print(error)
        print(traceback.format_exc())