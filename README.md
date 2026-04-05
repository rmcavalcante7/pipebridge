# PipeBridge

SDK Python para integracao com Pipefy com foco em:

- facade publica simples
- models tipados
- update seguro de campos
- move seguro entre fases
- upload e download de arquivos
- cache de schema
- extensibilidade por regras, handlers, policies e steps

Este projeto nao foi desenhado como wrapper raso de GraphQL. A proposta aqui e entregar uma camada de integracao previsivel, extensivel e adequada para cenarios reais de automacao.

## Instalacao

```bash
pip install pipebridge
```

Para desenvolvimento:

```bash
pip install -e .[dev]
```

## Quick Start

```python
from pipebridge import PipeBridge

api = PipeBridge(
  token="SEU_TOKEN",
  base_url="https://app.pipefy.com/queries",
)

card = api.cards.get("123456789")
print(card.title)
print(card.current_phase.name if card.current_phase else None)
```

## Superficie Publica

A entrada principal do SDK e a facade:

```python
api = PipeBridge(token="SEU_TOKEN", base_url="https://app.pipefy.com/queries")
```

Dominios publicos:

- `api.cards`
- `api.phases`
- `api.pipes`
- `api.files`

Subniveis quando aplicavel:

- `api.cards.raw`
- `api.cards.structured`
- `api.phases.raw`
- `api.phases.structured`
- `api.pipes.raw`
- `api.pipes.structured`

Objetos tambem expostos no topo do pacote:

- `PipefyHttpClient`
- `CardService`
- `FileService`
- `PipeService`
- `PhaseService`
- `FileUploadRequest`
- `FileDownloadRequest`
- `UploadConfig`
- `CardUpdateConfig`
- `CardMoveConfig`

## Principais Capacidades

### 1. Recuperacao de cards, pipes e fases

```python
card = api.cards.get("123")
phase = api.phases.get("456")
pipe = api.pipes.get("789")
```

### 2. Catalogo de schema do pipe

```python
pipe = api.pipes.getFieldCatalog("789")

for phase in pipe.iterPhases():
    print(phase.name)
    for field in phase.iterFields():
        print(field.id, field.type, field.options)
```

Esse catalogo e importante para:

- discovery de campos
- validacao de update
- suporte a tipos
- cache de schema

### 3. Update de campos de card

```python
from pipebridge import CardUpdateConfig

result = api.cards.updateFields(
  card_id="123",
  fields={
    "titulo": "Novo valor",
    "prioridade": "Alta",
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

O fluxo de update atual suporta familias importantes de campo, incluindo:

- texto curto e longo
- numero
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

Observacao importante:

- `connector` ficou fora do escopo da V1 por decisao arquitetural

### 4. Move seguro entre fases

```python
from pipebridge import CardMoveConfig

result = api.cards.moveSafely(
  card_id="123",
  destination_phase_id="999",
  expected_current_phase_id="456",
  config=CardMoveConfig(validate_required_fields=True),
)
```

Esse fluxo valida:

- se a fase atual e a esperada, quando informada
- se a transicao e permitida pela configuracao da fase atual
- se os campos obrigatorios da fase destino estao preenchidos

### 5. Upload e download de arquivos

```python
from pipebridge import FileUploadRequest, FileDownloadRequest, UploadConfig

upload_request = FileUploadRequest(
  file_name="arquivo.txt",
  file_bytes=b"conteudo",
  card_id="123",
  field_id="anexos",
  organization_id="999",
  expected_phase_id="456",
)

upload_result = api.files.uploadFile(upload_request)

download_request = FileDownloadRequest(
  card_id="123",
  field_id="anexos",
  output_dir="./downloads",
)

files = api.files.downloadAllAttachments(download_request)
```

## Extensibilidade

Uma das propostas centrais do projeto e permitir extensao sem fork do SDK.

### 1. Regras customizadas

Voce pode injetar regras extras em fluxos publicos.

Exemplo com update:

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
  field_id="codigo",
  value="VALOR",
  extra_rules=[UppercaseOnlyRule("codigo")],
)
```

### 2. Regex pronta para validacao de campo

```python
from pipebridge.service.card.flows.update.rules.regexFieldPatternRule import (
  RegexFieldPatternRule,
)

api.cards.updateField(
  card_id="123",
  field_id="codigo",
  value="ABC-123",
  extra_rules=[
    RegexFieldPatternRule({"codigo": r"^[A-Z]{3}-\d{3}$"})
  ],
)
```

### 3. Handlers customizados no update

Voce pode sobrescrever ou adicionar suporte de tipo em runtime:

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
  field_id="titulo",
  value="meu texto",
  extra_handlers={"short_text": UppercaseTextHandler()},
)
```

### 4. Policies de retry e circuit breaker

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

### 5. Steps customizados no upload

Na V1, extensao por `steps` esta publica apenas no upload:

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

Observacao:

- update de card e move seguro ainda nao expoem `steps` customizados na API publica da V1

## Models e Navegacao Semantica

Os models do SDK foram desenhados para navegacao semantica. O objetivo e evitar acesso estrutural direto por mapas sempre que possivel.

Exemplos:

```python
card = api.cards.get("123")

if card.hasField("titulo"):
    print(card.requireFieldValue("titulo"))

phase = api.phases.get("456")
print(phase.getFieldType("prioridade"))
print(phase.getFieldOptions("prioridade"))
print(phase.isFieldRequired("prioridade"))

pipe = api.pipes.getFieldCatalog("789")
for field in pipe.getFieldsByType("select"):
    print(field.id, field.label)
```

## Cache de Schema

O SDK possui cache em memoria para schema de pipe:

- orientado por `pipe_id`
- com TTL
- lock por chave
- refresh lazy sob demanda
- sem thread em background na V1

Na facade de cards:

```python
stats = api.cards.getSchemaCacheStats()
entry = api.cards.getSchemaCacheEntryInfo("789")
api.cards.invalidateSchemaCache("789")
```

## Casos de Uso Prontos

A pasta [useCases/](useCases/) e o ponto de partida recomendado para usuarios finais.

Ela contem exemplos executaveis para:

- inspecao de catalogo de campos do pipe
- inspecao em cascata do pipe, fases e cards
- update de campos do card
- update com regras extras
- custom handler
- move seguro
- upload e download
- upload com regras e policies
- upload com steps customizados

Veja [useCases/README.md](useCases/README.md).

## Documentacao HTML

O projeto tambem possui estrutura de documentacao Sphinx em [docs/](docs/).

Esse e o caminho pensado para a documentacao HTML navegavel do SDK, incluindo:

- visao geral
- quick start
- extensibilidade
- referencia de API
- guias de desenvolvimento

Para gerar localmente:

```bash
pip install -e .[docs]
sphinx-build -b html docs docs/_build/html
```

Entrada principal da documentacao no repositório:

- [docs/index.rst](docs/index.rst)

URL esperada da documentacao publicada via GitHub Pages:

- `https://rmcavalcante7.github.io/pipebridge/`

## Testes

O projeto esta organizado assim:

- `tests/unit`
- `tests/functional`
- `tests/integration`
- `useCases/`

Papel de cada um:

- `unit`
  - logica isolada
  - sem rede
  - sem credenciais

- `functional`
  - API publica
  - sem Pipefy real
  - com fakes/doubles

- `integration`
  - operacoes reais no Pipefy
  - dependem de:
    - `PIPEFY_API_TOKEN`
    - `PIPEFY_BASE_URL` opcional

Comandos:

```bash
python -m pytest tests/unit tests/functional -v
python -m pytest tests/integration -v
python -m pytest tests -v
```

Para integracao real:

```powershell
$env:PIPEFY_API_TOKEN="SEU_TOKEN"
$env:PIPEFY_BASE_URL="https://app.pipefy.com/queries"
python -m pytest tests/integration -v
```

## Estado Atual da V1

A V1 esta fechada com:

- facade publica coerente
- fluxo de update de card
- fluxo de move seguro
- fluxo de upload/download
- exceptions semanticas
- cache de schema
- pytest estruturado
- exemplos de uso para usuario final

Fora do escopo da V1:

- `connector` como operacao relacional completa
- extensao publica por `steps` em update e move

## Autor

Rafael Mota Cavalcante

- GitHub: [rmcavalcante7](https://github.com/rmcavalcante7)
- LinkedIn: [rafael-cavalcante-dev-specialist](https://www.linkedin.com/in/rafael-cavalcante-dev-specialist)
- E-mail: [rafaelcavalcante7@msn.com](mailto:rafaelcavalcante7@msn.com)

## Licenca

MIT
