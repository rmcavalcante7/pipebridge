# PipeBridge

PipeBridge is a Python SDK for Pipefy that provides a semantic, reliable layer for building maintainable automations and integrations.

Instead of stitching together raw GraphQL queries, validation logic, and payload handling in every project, PipeBridge gives you predictable workflows, typed models, and extension points for real-world automation scenarios.

> PipeBridge is not a thin GraphQL wrapper.
> It is an integration framework for production-oriented Pipefy automation.

## Why PipeBridge?

PipeBridge helps reduce the friction of direct Pipefy integrations by providing:

- a simple public facade
- typed and semantic models
- safe field updates
- safe phase transitions
- file upload and download flows
- schema caching
- extensibility through rules, handlers, policies, and steps

## Installation

```bash
pip install pipebridge
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

## Core Capabilities

### Safe card field updates

```python
from pipebridge import CardUpdateConfig

api.cards.updateFields(
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

### Safe phase moves

```python
from pipebridge import CardMoveConfig

api.cards.moveSafely(
    card_id="123",
    destination_phase_id="999",
    expected_current_phase_id="456",
    config=CardMoveConfig(validate_required_fields=True),
)
```

### File upload and download

```python
from pipebridge import FileUploadRequest, FileDownloadRequest

upload_request = FileUploadRequest(
    file_name="sample.txt",
    file_bytes=b"content",
    card_id="123",
    field_id="attachments",
    organization_id="999",
    expected_phase_id="456",
)

api.files.uploadFile(upload_request)

download_request = FileDownloadRequest(
    card_id="123",
    field_id="attachments",
    output_dir="./downloads",
)

files = api.files.downloadAllAttachments(download_request)
```

### Extensibility

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

## Learn More

- Documentation: https://rmcavalcante7.github.io/pipebridge/
- Examples: https://github.com/rmcavalcante7/pipebridge/tree/main/useCases
- Repository: https://github.com/rmcavalcante7/pipebridge

## License

MIT
