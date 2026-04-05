# Use Cases

Esta pasta contem exemplos executaveis para usuarios finais do SDK.

Objetivo:
- servir como ponto de partida fora do contexto de testes
- mostrar a API publica real do pacote
- evitar qualquer dependencia de `Credentials.py` ou `infra_core`

Padrao de autenticacao:
- passe `--token`
- ou defina `PIPEFY_API_TOKEN`

Endpoint:
- passe `--base-url`
- ou use `PIPEFY_BASE_URL`
- se nada for informado, o exemplo usa `https://app.pipefy.com/queries`

Exemplos:

```powershell
python useCases/pipe_field_catalog.py --token SEU_TOKEN --pipe-id 307064875
python useCases/pipe_cascade_inspection.py --token SEU_TOKEN --pipe-id 307064875 --max-cards-per-phase 3
python useCases/card_update_current_phase.py --token SEU_TOKEN --card-id 1330664077 --target-assignee-name "RAFAEL MOTA CAVALCANTE"
python useCases/card_update_with_extra_rules.py --token SEU_TOKEN --card-id 1330664077 --field-id descreva_a_torre --value "VALOR_CUSTOM"
python useCases/card_move_safely.py --token SEU_TOKEN --card-id 1330664077 --destination-phase-id 342616253 --expected-current-phase-id 342616258
python useCases/file_upload_download.py --token SEU_TOKEN --card-id 1328390184 --field-id c_digo --organization-id 133269 --expected-phase-id 342616256 --download-output-dir .\\downloads
python useCases/file_upload_with_rules_and_policies.py --token SEU_TOKEN --card-id 1328390184 --field-id c_digo --organization-id 133269 --expected-phase-id 342616256
python useCases/file_upload_with_custom_steps.py --token SEU_TOKEN --card-id 1328390184 --field-id c_digo --organization-id 133269 --expected-phase-id 342616256
python useCases/custom_card_update_handler.py --token SEU_TOKEN --card-id 1330664077 --field-id descreva_a_torre --value "valor customizado"
```
