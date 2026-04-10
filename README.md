<p align="center">
  <img src="https://raw.githubusercontent.com/rmcavalcante7/pipebridge/main/assets/branding/pipebridge-logo.svg" alt="PipeBridge logo" width="720" />
</p>

<p align="center">
  <a href="https://github.com/rmcavalcante7/pipebridge/releases/tag/v0.2.1">
    <img src="https://img.shields.io/badge/tag-v0.2.1-2563EB" alt="Tag v0.2.1" />
  </a>
  <a href="https://github.com/rmcavalcante7/pipebridge/actions/workflows/ci.yml">
    <img src="https://img.shields.io/github/actions/workflow/status/rmcavalcante7/pipebridge/ci.yml?branch=main&label=CI" alt="CI" />
  </a>
  <a href="https://rmcavalcante7.github.io/pipebridge/">
    <img src="https://img.shields.io/badge/docs-GitHub%20Pages-0B7285" alt="Docs" />
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-1F2937" alt="License" />
  </a>
  <img src="https://img.shields.io/badge/python-3.14-3776AB" alt="Python 3.14" />
</p>

# PipeBridge

PipeBridge is a Python SDK for Pipefy that gives you a semantic, reliable layer for building production-grade automations.

Instead of wiring raw GraphQL queries, manual validation, and brittle payload handling into every integration, PipeBridge gives you predictable workflows, typed models, and extension points that fit real automation scenarios.

> PipeBridge is not a thin GraphQL wrapper.
> It is an integration framework designed for maintainable Pipefy automation.

New in `v0.2.1`:

- start form schema coverage in the pipe catalog
- safe card creation against start form fields
- transport-level TLS and retry configuration

Quick links:

- Documentation: https://rmcavalcante7.github.io/pipebridge/
- Use cases: https://github.com/rmcavalcante7/pipebridge/tree/main/useCases
- PyPI: https://pypi.org/project/pipebridge/

## Summary

- [Why PipeBridge?](#why-pipebridge)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Public Surface](#public-surface)
- [Core Capabilities](#core-capabilities)
- [Start Form Semantics](#start-form-semantics)
- [Full Structure Traversal](#full-structure-traversal)
- [Extensibility](#extensibility)
- [Models and Semantic Navigation](#models-and-semantic-navigation)
- [Transport Configuration](#transport-configuration)
- [Schema Cache](#schema-cache)
- [Ready-to-Use Examples](#ready-to-use-examples)
- [HTML Documentation](#html-documentation)
- [Tests](#tests)
- [Current Status](#current-status)
- [Vision](#vision)
- [Author](#author)
- [License](#license)

## Why PipeBridge?

Direct Pipefy integrations usually force you to deal with:

- verbose GraphQL operations
- inconsistent payload structures
- repeated validation logic
- unsafe phase transitions
- ad hoc file handling and retries

PipeBridge addresses that with:

- a simple public facade
- typed models with semantic navigation
- start form-aware schema discovery
- safe card creation
- safe field updates
- safe phase moves
- file upload and download flows
- transport-level TLS and retry controls
- schema caching
- extensibility through rules, handlers, policies, and steps

## Installation

```bash
pip install pipebridge
```

For development:

```bash
pip install -e .[dev]
```

## Quick Start

```python
from pipebridge import PipeBridge

api = PipeBridge(
  token="YOUR_TOKEN",
  base_url="https://app.pipefy.com/queries",
)

card = api.cards.get("123456789")
print(card.title)
print(card.current_phase.name if card.current_phase else None)
```

## Public Surface

The main SDK entry point is the facade:

```python
api = PipeBridge(token="YOUR_TOKEN", base_url="https://app.pipefy.com/queries")
```

Public domains:

- `api.cards`
- `api.phases`
- `api.pipes`
- `api.files`

Sub-levels when applicable:

- `api.cards.raw`
- `api.cards.structured`
- `api.phases.raw`
- `api.phases.structured`
- `api.pipes.raw`
- `api.pipes.structured`

Objects also exposed at the package top level:

- `PipefyHttpClient`
- `TransportConfig`
- `CardService`
- `FileService`
- `PipeService`
- `PhaseService`
- `FileUploadRequest`
- `FileDownloadRequest`
- `UploadConfig`
- `CardUpdateConfig`
- `CardMoveConfig`

## Core Capabilities

### 1. Card, pipe, and phase retrieval

```python
card = api.cards.get("123")
phase = api.phases.get("456")
pipe = api.pipes.get("789")
```

### 2. Pipe schema catalog and start form coverage

```python
pipe = api.pipes.getFieldCatalog("789")

for field in pipe.iterStartFormFields():
    print(field.id, field.internal_id, field.type, field.required)

for phase in pipe.iterPhases():
    print(phase.name)
    for field in phase.iterFields():
        print(field.id, field.internal_id, field.type, field.options)
```

This catalog is important for:

- field discovery
- start form discovery
- update validation
- type support
- schema caching
- internal field mapping via `internal_id`

### 3. Safe card creation from start form

```python
result = api.cards.createSafely(
  pipe_id="789",
  title="New request",
  fields={
    "oc": "12345",
    "request_type": "Purchase",
  },
)
```

This path is intended for users who prefer a more conservative entry flow.

It validates:

- whether the field belongs to the pipe start form
- whether required start form fields were filled
- whether option values are valid when the field exposes options

Important note:

- start-form connector fields must receive connected record ids, not display labels
- a full tenant-specific example of create, move, and update is available in `useCases/start_form_create_move_fill.py`

### 4. Safe card field updates

```python
from pipebridge import CardUpdateConfig

result = api.cards.updateFields(
  card_id="123",
  fields={
    "title": "New value",
    "priority": "High",
  },
  expected_phase_id="456",
  config=CardUpdateConfig(
    validate_field_existence=True,
    validate_field_options=True,
    validate_field_type=True,
    validate_field_format=True,
  ),
)
```

The current update flow supports important field families, including:

- short and long text
- number
- currency
- email
- date
- datetime
- due_date
- time
- select
- radio
- label_select
- checklist
- assignee_select
- attachment

Important note:

- `connector` is out of scope for V1 by architectural decision

### 5. Safe phase moves

```python
from pipebridge import CardMoveConfig

result = api.cards.moveSafely(
  card_id="123",
  destination_phase_id="999",
  expected_current_phase_id="456",
  config=CardMoveConfig(validate_required_fields=True),
)
```

This flow validates:

- whether the current phase matches the expected phase, when provided
- whether the transition is allowed by the current phase configuration
- whether required fields in the destination phase are filled

### 6. File upload and download

```python
from pipebridge import FileUploadRequest, FileDownloadRequest, UploadConfig

upload_request = FileUploadRequest(
  file_name="sample.txt",
  file_bytes=b"content",
  card_id="123",
  field_id="attachments",
  organization_id="999",
  expected_phase_id="456",
)

upload_result = api.files.uploadFile(upload_request)

download_request = FileDownloadRequest(
  card_id="123",
  field_id="attachments",
  output_dir="./downloads",
)

files = api.files.downloadAllAttachments(download_request)
```

### 7. Transport configuration

```python
from pipebridge import PipeBridge, TransportConfig

api = PipeBridge(
  token="YOUR_TOKEN",
  base_url="https://app.pipefy.com/queries",
  transport_config=TransportConfig(
    timeout=45,
    verify_ssl=True,
    max_retries=2,
    retry_delay_seconds=1.0,
    retry_backoff_multiplier=2.0,
  ),
)
```

This transport layer supports:

- global request timeout override
- TLS verification control
- custom CA bundle path for corporate environments
- conservative retry for transient timeout and connection errors

## Start Form Semantics

PipeBridge now models the start form as part of the pipe schema, but not as a regular phase.

That distinction matters because:

- Pipefy exposes `start_form_fields` at the pipe level
- card creation enters the pipe through the start form
- later navigation and movement still happen through regular phases

This keeps the SDK aligned with the platform instead of introducing a fake phase abstraction.

## Full Structure Traversal

For a complete real example, see:

- [useCases/pipe_cascade_inspection.py](https://github.com/rmcavalcante7/pipebridge/blob/main/useCases/pipe_cascade_inspection.py)

Simplified loop:

```python
pipe = api.pipes.get("PIPE_ID")

print(f"Pipe: {pipe.name} ({pipe.id})")

for phase_summary in pipe.iterPhases():
    phase = api.phases.get(phase_summary.id)
    print(f"Phase: {phase.name} ({phase.id})")

    for field in phase.iterFields():
        print(
            f"id={field.id} | "
            f"type={field.type} | "
            f"required={field.required} | "
            f"options={field.options}"
        )

    cards = api.phases.listCards(phase.id)
    for card in cards:
        print(f"Card: {card.title} ({card.id})")

        for card_field in card.iterFields():
            print(
                f"field_id={card_field.id} | "
                f"label={card_field.label} | "
                f"type={card_field.type} | "
                f"value={card_field.value}"
            )
```

## Extensibility

One of the project's core goals is to allow extension without forking the SDK.

### 1. Custom rules

You can inject extra rules into public flows.

Example with updates:

```python
from pipebridge.exceptions import ValidationError
from pipebridge.workflow.rules.baseRule import BaseRule


class UppercaseOnlyRule(BaseRule):
  def __init__(self, field_id: str) -> None:
    self.field_id = field_id

  def execute(self, context) -> None:
    value = context.request.fields.get(self.field_id)
    if not isinstance(value, str) or value != value.upper():
      raise ValidationError(
        message=f"Field '{self.field_id}' must be uppercase",
        class_name=self.__class__.__name__,
        method_name="execute",
      )


api.cards.updateField(
  card_id="123",
  field_id="code",
  value="VALUE",
  extra_rules=[UppercaseOnlyRule("code")],
)
```

### 2. Ready-to-use regex for field validation

```python
from pipebridge.service.card.flows.update.rules.regexFieldPatternRule import (
  RegexFieldPatternRule,
)

api.cards.updateField(
  card_id="123",
  field_id="code",
  value="ABC-123",
  extra_rules=[
    RegexFieldPatternRule({"code": r"^[A-Z]{3}-\d{3}$"})
  ],
)
```

### 3. Custom update handlers

You can override or add type support at runtime:

```python
from pipebridge.service.card.flows.update.dispatcher.baseCardFieldUpdateHandler import (
  BaseCardFieldUpdateHandler,
)
from pipebridge.service.card.flows.update.dispatcher.resolvedFieldUpdate import (
  ResolvedFieldUpdate,
)


class UppercaseTextHandler(BaseCardFieldUpdateHandler):
  def resolve(self, field_id, field_type, input_value, current_field=None, phase_field=None):
    return ResolvedFieldUpdate(
      field_id=field_id,
      field_type=field_type,
      input_value=input_value,
      current_field=current_field,
      phase_field=phase_field,
      new_value=str(input_value).strip().upper(),
    )


api.cards.updateField(
  card_id="123",
  field_id="title",
  value="my text",
  extra_handlers={"short_text": UppercaseTextHandler()},
)
```

### 4. Retry and circuit breaker policies

```python
from pipebridge import UploadConfig
from pipebridge.workflow.config.retryConfig import RetryConfig
from pipebridge.workflow.config.circuitBreakerConfig import CircuitBreakerConfig

config = UploadConfig(
  retry=RetryConfig(max_retries=5, base_delay=1.0),
  circuit=CircuitBreakerConfig(failure_threshold=5, recovery_timeout=5.0),
)

api.files.uploadFile(request=upload_request, config=config)
```

### 5. Custom upload steps

In V1, `steps` extensibility is publicly exposed only for uploads:

- `extra_steps_before`
- `extra_steps_after`

```python
from pipebridge.workflow.steps.baseStep import BaseStep


class RegisterMetadataStep(BaseStep):
  def execute(self, context) -> None:
    context.metadata["source"] = "custom-step"


api.files.uploadFile(
  request=upload_request,
  extra_steps_before=[RegisterMetadataStep()],
)
```

Note:

- card updates and safe moves do not yet expose custom `steps` in the V1 public API

## Models and Semantic Navigation

SDK models were designed for semantic navigation. The goal is to avoid direct structural map access whenever possible.

Examples:

```python
card = api.cards.get("123")

if card.hasField("title"):
    print(card.requireFieldValue("title"))

phase = api.phases.get("456")
print(phase.getFieldType("priority"))
print(phase.getFieldOptions("priority"))
print(phase.isFieldRequired("priority"))

pipe = api.pipes.getFieldCatalog("789")
for field in pipe.getFieldsByType("select"):
    print(field.id, field.label)

for start_form_field in pipe.iterStartFormFields():
    print(start_form_field.id, start_form_field.internal_id)
```

## Transport Configuration

`TransportConfig` is the public transport-layer configuration object exposed at the top level of the package.

Use it when you need:

- timeout control across SDK operations
- custom certificate bundles in corporate networks
- temporary TLS relaxation in controlled environments
- bounded retries for transient transport failures

```python
from pipebridge import PipefyHttpClient, TransportConfig

client = PipefyHttpClient(
  auth_key="YOUR_TOKEN",
  base_url="https://app.pipefy.com/queries",
  transport_config=TransportConfig(
    timeout=30,
    ca_bundle_path="/path/to/company-ca.pem",
    max_retries=1,
  ),
)
```

## Schema Cache

The SDK provides in-memory cache for pipe schema:

- keyed by `pipe_id`
- with TTL
- with per-key locking
- lazy refresh on demand
- no background thread in V1

On the card facade:

```python
stats = api.cards.getSchemaCacheStats()
entry = api.cards.getSchemaCacheEntryInfo("789")
api.cards.invalidateSchemaCache("789")
```

And for direct schema inspection:

```python
pipe_schema = api.pipes.getFieldCatalog("789")

for phase in pipe_schema.iterPhases():
    print(f"Phase: {phase.name} ({phase.id})")
    for field in phase.iterFields():
        print(
            f"id={field.id} | "
            f"label={field.label} | "
            f"type={field.type} | "
            f"required={field.required}"
        )
```

## Ready-to-Use Examples

The [useCases](https://github.com/rmcavalcante7/pipebridge/tree/main/useCases) folder is the recommended starting point for end users.

It contains executable examples for:

- pipe field catalog inspection
- cascading inspection across pipes, phases, and cards
- start form creation followed by safe move and phase filling
- card field updates
- updates with extra rules
- custom handler
- safe moves
- upload and download
- uploads with rules and policies
- uploads with custom steps

See [useCases/README.md](https://github.com/rmcavalcante7/pipebridge/tree/main/useCases/README.md).

## HTML Documentation

The project also includes a Sphinx documentation structure in [docs/](docs/).

This is the intended path for the SDK's navigable HTML documentation, including:

- overview
- quick start
- extensibility
- API reference
- development guides

To generate locally:

```bash
pip install -e .[docs]
sphinx-build -b html docs docs/_build/html
```

Main documentation entry point in the repository:

- [docs/index.rst](docs/index.rst)

Expected URL for published documentation via GitHub Pages:

- [https://rmcavalcante7.github.io/pipebridge/](https://rmcavalcante7.github.io/pipebridge/)

## Tests

The project is organized as follows:

- `tests/unit`
- `tests/functional`
- `tests/integration`
- `useCases/`

Role of each:

- `unit`
  - isolated logic
  - no network
  - no credentials

- `functional`
  - public API
  - no real Pipefy
  - with fakes/doubles

- `integration`
  - real Pipefy operations
  - depend on:
    - `PIPEFY_API_TOKEN`
    - optional `PIPEFY_BASE_URL`

Commands:

```bash
python -m pytest tests/unit tests/functional -v
python -m pytest tests/integration -v
python -m pytest tests -v
```

For real integration:

```powershell
$env:PIPEFY_API_TOKEN="YOUR_TOKEN"
$env:PIPEFY_BASE_URL="https://app.pipefy.com/queries"
python -m pytest tests/integration -v
```

For the destructive live create/move/update battery:

```powershell
$env:PIPEFY_API_TOKEN="YOUR_TOKEN"
$env:PIPEFY_BASE_URL="https://app.pipefy.com/queries"
$env:PIPEBRIDGE_ENABLE_DESTRUCTIVE_CREATE_TESTS="1"
$env:PIPEBRIDGE_TEST_PIPE_ID="307064875"
$env:PIPEBRIDGE_REFERENCE_CARD_ID="1330664077"  # optional, read-only reference
$env:PIPEBRIDGE_DELETE_CREATED_TEST_CARD="1"    # default behavior
python -m pytest tests/integration/test_card_service.py tests/integration/test_card_move_flow.py tests/integration/test_card_update_flow.py -v
```

Notes for the destructive live battery:

- it creates one new card per test session
- all live mutations in that battery run only against the created card
- the optional reference card is read-only and is used only to copy values when helpful
- when no reference card is provided, the helpers generate valid values by field type
- teardown can delete only the created card when `PIPEBRIDGE_DELETE_CREATED_TEST_CARD` is enabled

## Current Status

Current release highlights:

- coherent public facade
- start form-aware pipe schema catalog
- safe card creation via `createSafely(...)`
- transport configuration via `TransportConfig`
- TLS and retry controls at the HTTP boundary
- card update flow
- safe move flow
- upload/download flow
- semantic exceptions
- schema cache
- structured pytest suite
- end-user usage examples
- destructive live test battery that creates, updates, moves, validates, and optionally deletes only the card created for that run

Foundational capabilities already in place:

- coherent public facade
- card update flow
- safe move flow
- upload/download flow
- semantic exceptions
- schema cache
- structured pytest suite
- end-user usage examples

Still out of scope:

- `connector` as a complete relational operation
- public `steps` extensibility in updates and moves
- administrative operations for start form configuration

## Vision

PipeBridge aims to be the standard semantic integration layer for Pipefy automation.

The current product direction is clear:

- keep the public facade small and coherent
- make common automation flows safer by default
- support extension without forcing forks
- keep documentation and examples strong enough for real adoption

## Author

Rafael Mota Cavalcante

- GitHub: [rmcavalcante7](https://github.com/rmcavalcante7)
- LinkedIn: [rafael-cavalcante-dev-specialist](https://www.linkedin.com/in/rafael-cavalcante-dev-specialist)
- E-mail: [rafaelcavalcante7@msn.com](mailto:rafaelcavalcante7@msn.com)

## License

MIT
