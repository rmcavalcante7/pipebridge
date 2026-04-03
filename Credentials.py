from dataclasses import dataclass

from infra_core import BaseCredentials, FernetEncryption, CredentialsLoader
from infra_core.credentials.setup.credentials_setup_service import (
    CredentialsSetupService,
)
#
#
@dataclass(frozen=True)
class MyPipefyCredentials(BaseCredentials):
    api_token: str


if __name__ == "__main__":

    api_token = ""
    # ============================================================
    # Setup
    # # ============================================================
    setup = CredentialsSetupService(FernetEncryption)

    # Rodar para criar um novo arquivo de armazenamento
    setup.setup(MyPipefyCredentials(api_token=api_token), name="pipefy_automation_factory")

    # rodar para testar o carregamento de alguma credencial já salva
    # TOKEN = CredentialsLoader.load(MyPipefyCredentials, FernetEncryption, name='pipefy')
    TOKEN = CredentialsLoader.load(MyPipefyCredentials, FernetEncryption, name='pipefy_automation_factory')
    print(TOKEN)

