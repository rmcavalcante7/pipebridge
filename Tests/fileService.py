# ============================================================
# Dependencies
# ============================================================
from infra_core import FernetEncryption, CredentialsLoader
from Credentials import MyPipefyCredentials

from pipefy import Pipefy

import traceback
from typing import List, Optional
from pathlib import Path

from pipefy.models.file.fileUploadRequest import FileUploadRequest
from pipefy.models.file.fileDownloadRequest import FileDownloadRequest



# ============================================================
# Setup
# ============================================================

def getApi(credential_name: str, base_url: str) -> Pipefy:
    """
    Initialize Pipefy API safely.

    :param credential_name: str = Credential identifier
    :param base_url: str = API base URL

    :return: Pipefy = Initialized API client

    :raises Exception:
        When credential loading fails

    :example:
        >>> callable(getApi)
        True
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

def testUpload(api: Pipefy, card_id: str, field_id: str, org_id: str, expected_phase_id: Optional[str] = None) -> None:
    """
    Test file upload workflow using request object.

    :param api: Pipefy
    :param card_id: str
    :param field_id: str
    :param org_id: str

    :return: None

    :example:
        >>> callable(testUpload)
        True
    """
    print("\n=== TEST: files.upload ===")

    request = FileUploadRequest(
        file_name="7-Novo_test_file.txt",
        file_bytes=b"hello from pipfey sdk",
        card_id=card_id,
        field_id=field_id,
        organization_id=org_id,
        replace_files=True,
        expected_phase_id=expected_phase_id
    )

    result = api.files.uploadFile(request)

    # --------------------------------------------------------
    # Assertions
    # --------------------------------------------------------
    from pipefy.integrations.file.fileUploadResult import FileUploadResult

    assert isinstance(result, FileUploadResult), "Result must be FileUploadResult"
    assert result.success is True, "Upload must be successful"

    assert isinstance(result.file_path, list), "file_path must be list"

    for file_path in result.file_path:
        assert isinstance(file_path, str), "file_path must contain strings"
        assert file_path.startswith("orgs/"), "Invalid file_path format"

    if result.download_url is not None:
        assert isinstance(result.download_url, str), "download_url must be string"

    print("Upload result:", result)
    print("✔ upload OK")



def uploadFileBlockBaseRule(
    api: Pipefy,
    card_id: str,
    field_id: str,
    phase_id: str,
    org_id: str,
    expected_phase_id: Optional[str] = None
) -> None:
    """
    Test custom rule blocking upload.

    This test validates that:
        - Custom rules are executed
        - Rule can block execution
        - Upload is prevented when rule fails

    :param api: Pipefy
    :param card_id: str
    :param field_id: str
    :param org_id: str
    :param expected_phase_id: Optional[str]

    :return: None

    :example:
        >>> callable(uploadFileBlockBaseRule)
        True
    """
    from pipefy.service.file.flows.rules.baseRule import BaseRule

    class BlockTxtRule(BaseRule):
        """
        Blocks .txt file uploads.
        """

        def execute(self, context) -> None:
            """
            Executes rule validation.

            :param context: UploadPipelineContext

            :raises Exception:
                When file is .txt
            """
            if context.request.file_name.endswith(".txt"):
                raise Exception("TXT files are not allowed")

        def __str__(self) -> str:
            return "<BlockTxtRule>"

        def __repr__(self) -> str:
            return "<BlockTxtRule()>"

    print("\n=== TEST: files.upload (custom rule blocking) ===")

    request = FileUploadRequest(
        file_name="7-Novo_test_file.txt",  # 🔥 deve falhar
        file_bytes=b"hello from pipfey sdk",
        card_id=card_id,
        field_id=field_id,
        organization_id=org_id,
        replace_files=True,
        expected_phase_id=phase_id
    )

    try:
        api.files.uploadFile(
            request=request,
            extra_rules=[BlockTxtRule()]
        )

        # --------------------------------------------------------
        # FAIL: deveria ter bloqueado
        # --------------------------------------------------------
        assert False, "Upload should have been blocked by BlockTxtRule"

    except Exception as exc:
        # --------------------------------------------------------
        # PASS: erro esperado
        # --------------------------------------------------------
        assert "TXT files are not allowed" in str(exc), \
            f"Unexpected error: {exc}"

        print("✔ custom rule executed and blocked upload")
        print("Error:", exc)

def uploadFileAllowCustomRule(
    api: Pipefy,
    card_id: str,
    field_id: str,
    phase_id: str,
    org_id: str,

) -> None:
    """
    Test custom rule allowing upload.

    :example:
        >>> callable(uploadFileAllowCustomRule)
        True
    """
    from pipefy.service.file.flows.rules.baseRule import BaseRule

    class AllowAllRule(BaseRule):
        def execute(self, context) -> None:
            pass

    print("\n=== TEST: files.upload (custom rule allow) ===")

    request = FileUploadRequest(
        file_name="valid_file.png",
        file_bytes=b"valid content",
        card_id=card_id,
        field_id=field_id,
        organization_id=org_id,
        expected_phase_id=phase_id,
        replace_files=True
    )

    result = api.files.uploadFile(
        request=request,
        extra_rules=[AllowAllRule()]
    )

    from pipefy.integrations.file.fileUploadResult import FileUploadResult

    assert isinstance(result, FileUploadResult)
    assert result.success is True

    print("✔ upload allowed with custom rule")


def testDownload(api: Pipefy, card_id: str, field_id: str) -> None:
    """
    Test file download workflow using request object.

    :param api: Pipefy
    :param card_id: str
    :param field_id: str

    :return: None

    :example:
        >>> callable(testDownload)
        True
    """
    print("\n=== TEST: files.download ===")

    request = FileDownloadRequest(
        card_id=card_id,
        field_id=field_id,
        output_dir="./downloads_test"
    )

    files: List[Path] = api.files.downloadAllAttachments(request)

    assert isinstance(files, list), "Download must return a list"

    for file_path in files:
        assert isinstance(file_path, Path), "Each item must be Path"
        assert file_path.exists(), f"File does not exist: {file_path}"

    print(f"Downloaded {len(files)} files")
    print("✔ download OK")


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
    FIELD_ID = 'c_digo'
    try:
        # ========================================================
        # CORE FLOW
        # ========================================================
        testUpload(api, card_id=CARD_ID, field_id=FIELD_ID, org_id=ORGANIZATION_ID, expected_phase_id=PHASE_ID)

        uploadFileBlockBaseRule(api, card_id=CARD_ID, field_id=FIELD_ID, org_id=ORGANIZATION_ID, phase_id=PHASE_ID)
        uploadFileAllowCustomRule(api, card_id=CARD_ID, field_id=FIELD_ID, org_id=ORGANIZATION_ID, phase_id=PHASE_ID)

        testDownload(api, CARD_ID, FIELD_ID)

        print("\n🎯 ALL FILE TESTS PASSED")

    except Exception as error:
        print("\n❌ TEST FAILED:")
        print(error)
        print(traceback.format_exc())