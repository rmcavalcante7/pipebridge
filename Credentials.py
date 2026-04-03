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

    api_token = "eyJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJQaXBlZnkiLCJpYXQiOjE3NzUwNDM0NDcsImp0aSI6ImFhZjQ0N2UyLWI1NzQtNGE3NS1hMzYxLTc3ZWM4NWYwNjA1ZiIsInN1YiI6MzA1Njc0MzA1LCJ1c2VyIjp7ImlkIjozMDU2NzQzMDUsImVtYWlsIjoicmFmYWVsLm0uY2F2YWxjYW50ZUBhY2NlbnR1cmUuY29tIn0sInVzZXJfdHlwZSI6ImF1dGhlbnRpY2F0ZWQifQ.wS973IfL2-Y3EaO4KnEt4oyz8yrLpCNjlRfoFvt2JhrcNmXSGOq_WAfgM1jAjbJCUmHpDNWbRlDJd2szDvbgmw"
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

