# Use Cases

This folder contains executable examples for end users of the SDK.

Purpose:
- serve as a starting point outside the test context
- show the real public API of the package
- avoid any dependency on `Credentials.py` or `infra_core`

Authentication pattern:
- pass `--token`
- or define `PIPEFY_API_TOKEN`

Endpoint:
- pass `--base-url`
- or use `PIPEFY_BASE_URL`
- if nothing is provided, the example uses `https://app.pipefy.com/queries`

Examples:

```powershell
python useCases/pipe_field_catalog.py --token YOUR_TOKEN --pipe-id 307064875
python useCases/pipe_cascade_inspection.py --token YOUR_TOKEN --pipe-id 307064875 --max-cards-per-phase 3
python useCases/card_update_current_phase.py --token YOUR_TOKEN --card-id 1330664077 --target-assignee-name "RAFAEL MOTA CAVALCANTE"
python useCases/card_update_with_extra_rules.py --token YOUR_TOKEN --card-id 1330664077 --field-id tower_description --value "CUSTOM_VALUE"
python useCases/card_move_safely.py --token YOUR_TOKEN --card-id 1330664077 --destination-phase-id 342616253 --expected-current-phase-id 342616258
python useCases/file_upload_download.py --token YOUR_TOKEN --card-id 1328390184 --field-id code --organization-id 133269 --expected-phase-id 342616256 --download-output-dir .\\downloads
python useCases/file_upload_with_rules_and_policies.py --token YOUR_TOKEN --card-id 1328390184 --field-id code --organization-id 133269 --expected-phase-id 342616256
python useCases/file_upload_with_custom_steps.py --token YOUR_TOKEN --card-id 1328390184 --field-id code --organization-id 133269 --expected-phase-id 342616256
python useCases/custom_card_update_handler.py --token YOUR_TOKEN --card-id 1330664077 --field-id tower_description --value "custom value"
```
