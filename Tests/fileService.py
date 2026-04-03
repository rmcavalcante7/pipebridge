# ============================================================
# Dependencies
# ============================================================
from infra_core import FernetEncryption, CredentialsLoader
from Credentials import MyPipefyCredentials

from pipefy import Pipefy

import traceback
from typing import List
from pathlib import Path


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
# FILE TESTS
# ============================================================

def testUpload(api: Pipefy, card_id: str, field_id: str, org_id: int) -> None:
    """
    Test file upload workflow.

    :param api: Pipefy
    :param card_id: str
    :param field_id: str
    :param org_id: int

    :return: None
    """
    print("\n=== TEST: files.upload ===")

    file_name = "2test_file.txt"
    file_bytes = b"hello from pipfey sdk"

    result = api.files.upload(
        file_name=file_name,
        file_bytes=file_bytes,
        card_id=card_id,
        field_id=field_id,
        organization_id=org_id,
        replace_files=False
    )

    # --------------------------------------------------------
    # Assertions
    # --------------------------------------------------------
    from pipefy.integrations.file.fileUploadResult import FileUploadResult

    assert isinstance(result, FileUploadResult), "Result must be FileUploadResult"
    assert result.success is True, "Upload must be successful"

    assert isinstance(result.file_path, list), "file_path must list of strings"
    for file_path in result.file_path:
        assert file_path.startswith("orgs/"), "Invalid file_path format"

    if result.download_url is not None:
        assert isinstance(result.download_url, str), "download_url must be string"

    # --------------------------------------------------------
    # Output
    # --------------------------------------------------------
    print("Upload result:", result)
    print("File path:", result.file_path)
    print("Download URL:", result.download_url)

    print("✔ upload OK")

def testDownload(api: Pipefy, card_id: str, field_id:str) -> None:
    """
    Test file download workflow.

    :param api: Pipefy
    :param card_id: str

    :return: None
    """
    print("\n=== TEST: files.download ===")

    output_dir = "./downloads_test"

    files: List[Path] = api.files.download(
        card_id=card_id,
        field_id=field_id,
        output_dir=output_dir
    )

    assert isinstance(files, list), "Download must return a list"

    for file_path in files:
        assert isinstance(file_path, Path), "Each item must be Path"
        assert file_path.exists(), f"File does not exist: {file_path}"

    print(f"Downloaded {len(files)} files")
    print("✔ download OK")


def testUploadValidation(api: Pipefy) -> None:
    """
    Test validation errors for upload.

    :param api: Pipefy

    :return: None
    """
    print("\n=== TEST: files.upload (validation) ===")

    try:
        api.files.upload(
            file_name="",
            file_bytes=b"",
            card_id="",
            field_id="",
            organization_id="invalid"  # errado de propósito
        )
        assert False, "ValidationError expected"

    except Exception as exc:
        print("Expected error:", exc)
        print("✔ validation OK")


def testDownloadValidation(api: Pipefy) -> None:
    """
    Test validation errors for download.

    :param api: Pipefy

    :return: None
    """
    print("\n=== TEST: files.download (validation) ===")

    try:
        api.files.download(
            card_id="",
            output_dir=""
        )
        assert False, "ValidationError expected"

    except Exception as exc:
        print("Expected error:", exc)
        print("✔ validation OK")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    credential_name = 'pipefy'
    credential_name = 'pipefy_automation_factory'

    base_url = ''
    if credential_name == 'pipefy-não rodar aqui':
        # TIMDECOM
        # CARD_ID = "35814650"
        # PIPE_ID = "11881"
        # PHASE_ID = "83728"
        # base_url: str = "https://accenture.pipefy.com/queries"
        pass
    elif credential_name == 'pipefy_automation_factory':
        # Automation Factory
        CARD_ID = "1328390184"
        PIPE_ID = "307064875"
        PHASE_ID = "342616256"
        base_url: str = 'https://app.pipefy.com/queries'
        ORGANIZATION_ID = '133269'
    else:
        raise Exception("Invalid credential name")

    api = getApi(credential_name=credential_name, base_url=base_url)

    try:
        # ========================================================
        # CORE FLOW
        # ========================================================
        field_id = 'c_digo'
        testUpload(api, card_id=CARD_ID, field_id=field_id, org_id=ORGANIZATION_ID)
        testDownload(api, card_id=CARD_ID, field_id=field_id)

        # ========================================================
        # VALIDATIONS
        # ========================================================
        testUploadValidation(api)
        testDownloadValidation(api)

        print("\n🎯 ALL FILE TESTS PASSED")

    except Exception as error:
        print("\n❌ TEST FAILED:")
        print(error)
        print(traceback.format_exc())