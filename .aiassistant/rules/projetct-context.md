---
apply: always
---

# PROMPT DE CONTINUACAO - PIPEFY SDK

## Leitura obrigatoria

Este arquivo registra o estado atual, as decisoes arquiteturais consolidadas, os pontos ainda em aberto e a forma correta de continuar o desenvolvimento deste SDK.

Ele deve ser tratado como memoria persistida do projeto.

Se uma nova sessao for iniciada, este documento deve ser lido antes de qualquer alteracao relevante no codigo.

O objetivo aqui nao e apenas listar features. O objetivo e preservar:

- a intencao arquitetural
- os contratos internos ja consolidados
- os aprendizados extraidos do comportamento real da API do Pipefy
- os cuidados que evitam regressao
- os proximos passos com maior retorno tecnico

Este projeto ja passou da fase de exploracao. Estamos em fase de consolidacao arquitetural e expansao controlada.

---

## Contexto geral do projeto

Estamos construindo um SDK Python para integracao com Pipefy.

Este SDK nao deve ser tratado como wrapper raso de GraphQL. A intencao do projeto e ter uma biblioteca robusta, previsivel, extensivel e adequada para uso serio em integracoes internas ou publicacao futura.

Principios centrais:

- Clean Architecture
- separacao clara de responsabilidades
- tipagem forte
- docstrings Sphinx detalhadas
- exceptions semanticas e ricas em contexto
- comportamento guiado pela documentacao oficial e confirmado empiricamente em pontos criticos
- foco em manutencao futura e previsibilidade operacional

O projeto foi se sofisticando ao longo do tempo. Hoje ele ja possui:

- facade publica do SDK
- services por dominio
- models tipados
- flows com workflow generico
- rules desacopladas
- policies de resiliencia
- exceptions organizadas por categoria
- update de campos de card via fluxo novo e dispatcher por tipo

---

## Estrutura atual consolidada

Visao macro do pacote:

```text
src/pipefy/
  client/
  exceptions/
  facade/
  integrations/
  models/
  service/
    card/
    file/
    phase/
    pipe/
  workflow/
```

Papeis:

- `client/`
  - transporte HTTP / GraphQL
  - traducao de falhas de transporte

- `exceptions/`
  - taxonomia de erros do SDK
  - base rica em contexto

- `facade/`
  - boundary publico do SDK
  - ponto de entrada estavel para o consumidor

- `integrations/`
  - integracoes externas de menor nivel, especialmente file handling

- `models/`
  - representacoes tipadas do dominio

- `service/`
  - orquestracao de casos de uso por dominio

- `workflow/`
  - infraestrutura generica de execucao, regras e resiliencia

---

## Facade: boundary publico do SDK

O usuario do SDK deve interagir preferencialmente por:

```python
api = Pipefy(token=..., base_url=...)
```

Superficie publica principal:

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

Ponto importante:

- a refatoracao interna pode continuar mudando
- a facade deve permanecer estavel
- testes funcionais publicos devem usar a facade sempre que possivel
- testes estruturais internos podem acessar internals quando o objetivo for validar infraestrutura tecnica, como circuit breaker

Recentemente, o update de campos de card foi exposto na facade:

- `api.cards.updateField(...)`
- `api.cards.updateFields(...)`

Tambem foi exposto um metodo de catalogo de schema do pipe:

- `api.pipes.getFieldCatalog(pipe_id)`

---

## Reorganizacao dos services por dominio

Os services antigos soltos na pasta `service/` foram removidos.

Hoje a organizacao canonica e:

```text
src/pipefy/service/card/
src/pipefy/service/file/
src/pipefy/service/phase/
src/pipefy/service/pipe/
```

Dentro de cada dominio, queries e mutations foram extraidas para modulos dedicados.

Exemplos:

- `src/pipefy/service/card/queries/cardQueries.py`
- `src/pipefy/service/card/mutations/cardMutations.py`
- `src/pipefy/service/phase/queries/phaseQueries.py`
- `src/pipefy/service/pipe/queries/pipeQueries.py`

Racional:

- remover GraphQL inline dentro dos services
- separar construcao de query da logica de negocio
- facilitar reuso
- facilitar manutencao
- deixar cada service mais legivel

---

## Workflow generico consolidado

O antigo motor acoplado ao upload foi extraido para um nucleo generico em `workflow/`.

Estrutura conceitual:

- `workflow/context`
- `workflow/engine`
- `workflow/rules`
- `workflow/steps`
- `workflow/policies`
- `workflow/config`
- `workflow/resilience`

Arquitetura atual:

- `RuleEngine`
  - executa regras
  - respeita prioridade
  - deixa `PipefyError` semantico subir
  - encapsula falhas tecnicas em `RuleExecutionError`

- `ExecutionEngine`
  - executa steps
  - nao conhece retry, jitter ou circuit breaker diretamente
  - so resolve e aplica policies
  - encapsula falhas tecnicas em `StepExecutionError`

- `PolicyChain`
  - permite compor varias policies sobre o mesmo step

- `ProfilePolicyResolver`
  - resolve a cadeia de policies de acordo com o profile do step

- `RetryPolicy`
  - retry externo ao step

- `CircuitBreakerPolicy`
  - breaker externo ao step

Importante:

- step nao conhece politica
- engine nao conhece politica concreta
- quem conhece politica e o resolver/chain

Esse desenho deve ser preservado.

---

## Upload de arquivos: estado atual

O subdominio de arquivos foi reorganizado por fluxo.

Estrutura atual:

```text
src/pipefy/service/file/
  fileService.py
  fileServiceContext.py
  flows/
    upload/
      fileUploadFlow.py
      config/
        uploadConfig.py
      context/
        uploadPipelineContext.py
      steps/
      rules/
    download/
      baseFileDownloadFlow.py
      fileDownloadContext.py
      fileDownloadFlow.py
```

O fluxo de upload funciona em cima do workflow generico.

O fluxo de download tambem ja foi separado.

O teste `Tests/fileService.py` foi reorganizado em:

- testes publicos via facade
- teste interno de infraestrutura para circuit breaker

Ponto importante de extensibilidade:

- `extra_rules` esta exposto publicamente
- `extra_handlers` esta exposto publicamente no fluxo de update de card
- extensao por `steps` foi exposta publicamente apenas no fluxo de upload
  - via `extra_steps_before`
  - via `extra_steps_after`
- por enquanto, card update e move nao expoem `steps` customizados na API publica
  - isso foi uma decisao deliberada de escopo e seguranca da V1
  - o upload ja tinha pipeline madura o suficiente para esse ponto de extensao

Esse teste ja passou integralmente.

---

## Exceptions: estado atual consolidado

As exceptions foram profundamente reorganizadas.

Hoje a pasta `src/pipefy/exceptions` esta estruturada por categoria:

```text
src/pipefy/exceptions/
  core/
  auth/
  config/
  file/
  transport/
  workflow/
  validation/
  __init__.py
```

Isso substituiu o estado antigo onde havia muitos arquivos soltos, com nomes inconsistentes e subutilizacao das classes.

### Objetivo da refatoracao

As exceptions agora devem cumprir quatro papeis:

1. representar falhas semanticamente
2. servir de contrato entre camadas
3. carregar contexto operacional util
4. informar politicas como retryabilidade

### Base semantica

A base do SDK foi fortalecida para carregar:

- mensagem
- contexto
- cause
- retryable
- error_code
- class_name
- method_name

### Aplicacao pratica ja feita

- `httpClient` agora distingue melhor timeout, connection, auth, rate limit e resposta inesperada
- `workflow` usa erros semanticos como `CircuitBreakerOpenError` e `RetryExhaustedError`
- flows de arquivo usam erros especificos de dominio
- services preservam `PipefyError` ao inves de embrulhar tudo em `RequestError`

### Validation package

O pacote `validation` tambem foi reorganizado e consolidado:

- `errors.py`
- `field.py`
- `phase.py`

Isso melhora:

- clareza conceitual
- organizacao fisica
- previsibilidade de imports

### Estado mental correto

As exceptions nao devem mais ser tratadas como "mensagens bonitas".

Elas devem ser tratadas como parte da arquitetura.

---

## Models: fonte da verdade

Os models sao centrais no projeto.

Pontos importantes:

- `Card`
  - usa `fields_map` como acesso O(1)

- `Phase`
  - usa `fields_map` como acesso O(1) ao schema da fase

- `Pipe`
  - usa `phases_map`, `labels_map` e `users_map`

Recentemente:

- `PhaseField` passou a suportar `uuid`

Isso foi importante para enriquecer o catalogo de schema do pipe e para futuras correlacoes com comportamento da API e do frontend.

Os models devem continuar sendo preferidos sobre `dict` cru sempre que o SDK estiver lidando com estado de dominio.

---

## Documentacao oficial e comportamento observado

Ponto importante que precisa ficar registrado com precisao:

Nao devemos tratar a documentacao oficial do Pipefy como algo "nao confiavel" por padrao.

Essa afirmacao ficou sendo propagada em contextos anteriores, mas hoje ela e forte demais e nao representa bem o estado atual do conhecimento do projeto.

O posicionamento correto e:

- a documentacao oficial do Pipefy deve ser tratada como referencia primaria
- a documentacao e util, relativamente bem elaborada e importante para discovery de objetos, tipos e operacoes
- o comportamento real da API ainda deve ser validado empiricamente quando estivermos lidando com pontos sensiveis, especialmente mutacoes de update, variacoes por tipo de campo e diferencas entre exemplos documentados e comportamento observado
- o frontend, o devtools e testes reais continuam sendo ferramentas auxiliares de confirmacao, nao substitutos automaticos da documentacao

Em outras palavras:

- a documentacao continua sendo a base
- o teste real e a confirmacao final quando houver duvida
- o SDK nao deve nascer de "desconfianca da doc", e sim de combinacao entre documentacao, testes e observacao pratica

Aprendizado consolidado:

- a documentacao oficial deve ser usada como fonte primaria
- o comportamento real precisa ser validado empiricamente em pontos criticos
- o frontend e o devtools ajudam a entender variacao por tipo
- o SDK nao deve copiar cegamente o frontend

Foi consolidado, a partir da implementacao atual e dos testes realizados, que:

- `updateCardField` e o caminho funcional central no SDK para update de campos
- a API trabalha com substituicao completa de estado do campo

Implicacao:

- nao existe patch parcial confiavel a ser assumido
- o SDK deve calcular o `new_value` final do campo
- anexar, remover ou substituir significa sempre enviar o valor final inteiro

Regra de ouro:

1. carregar estado atual do card
2. usar `Card.fields_map`
3. descobrir schema/tipo via fase
4. calcular `new_value`
5. aplicar update

Essa regra nao deve ser quebrada.

---

## Fluxo novo de update de card

Esta foi a ultima grande entrega funcional relevante ja implementada.

Estrutura:

```text
src/pipefy/service/card/flows/update/
  cardUpdateFlow.py
  cardUpdateConfig.py
  cardUpdateRequest.py
  cardUpdateResult.py
  context/
    cardUpdateContext.py
  dispatcher/
  rules/
  steps/
```

### Contexto

`CardUpdateContext` concentra:

- request
- client
- card_service
- phase_service
- config
- card
- phase
- resolved operations
- responses

### Steps

Fluxo atual de update:

1. `LoadCardStep`
2. `LoadPhaseSchemaStep`
3. `ResolveCardFieldUpdatesStep`
4. `ApplyCardFieldUpdatesStep`

### Rules

Rules atuais:

- `ValidateCardUpdateRequestRule`
- `ValidateCardPhaseRule`
- `ValidateCardFieldSchemaRule`
- `ValidateCardFieldFormatRule`

### Dispatcher

O dispatcher novo e orientado a `ResolvedFieldUpdate`, e nao a mutation pronta.

Responsabilidade:

- receber `field_type`
- normalizar o valor
- produzir `new_value`

O envio final para a mutation fica no step de aplicacao.

### Integracao

`CardService.updateFields(...)` hoje delega ao novo flow.

`CardsFacade` ja expoe:

- `updateField(...)`
- `updateFields(...)`

### Status

O teste de integracao focado no fluxo de update ja passou com sucesso em um card real.

Arquivo:

- `Tests/cardUpdateFlow.py`

Esse teste:

- carrega um card real
- carrega a fase atual
- identifica campos da fase atual
- lista campos fora da fase
- monta payloads seguros por tipo
- pula attachment e assignee por seguranca no teste
- executa update pela facade

Esse fluxo deve ser tratado como base atual oficial para updates de campos.

---

## Dispatcher de update: cobertura atual

O fluxo novo de update ja suporta familias relevantes de tipos.

### Tipos atualmente cobertos

- `attachment`
- `short_text`
- `long_text`
- `select`
- `number`
- `datetime`
- `date`
- `due_date`
- `assignee`
- `assignee_select`
- `currency`
- `email`
- `phone`
- `cpf`
- `cnpj`
- `label_select`
- `radio_horizontal`
- `radio_vertical`
- `checklist_horizontal`
- `checklist_vertical`
- `connector`

### Familias de handlers

Handlers implementados:

- texto simples
- opcao unica
- checklist
- numero/currency
- data/datetime/due_date
- assignee
- attachment
- connector

### O que ainda merece atencao

Apesar de os tipos acima estarem no registry, alguns deles ainda estao com suporte funcional inicial, e nao com semantica de negocio profunda.

Exemplos:

- `email`
- `phone`
- `cpf`
- `cnpj`
- `currency`
- `connector`

Hoje eles estao cobertos em nivel de compatibilidade e validacao opcional de formato, mas nao necessariamente com toda a inteligencia especifica de negocio que pode surgir futuramente.

---

## Validacoes opcionais no update

Ponto muito importante consolidado:

Nem toda validacao deve ser obrigatoria.

Motivo:

- alguns consumidores sabem exatamente o que estao fazendo
- algumas validacoes encarecem o fluxo
- o SDK deve oferecer seguranca por padrao, mas sem punir sempre quem quer performance

### Config do fluxo

`CardUpdateConfig` hoje permite controlar:

- `validate_phase`
- `validate_field_existence`
- `validate_field_options`
- `validate_field_type`
- `validate_field_format`
- `load_phase_schema`
- configs de retry e circuit breaker

### Validacao de options

A validacao de options foi corretamente posicionada em rules, nao no dispatcher.

Isso e importante.

Dispatcher:

- resolve tipo e valor

Rule:

- decide se aquele valor faz sentido para a configuracao real do campo naquela fase

Isso precisa continuar assim.

### Validacao de formato

Foi adicionada uma rule opcional:

- `ValidateCardFieldFormatRule`

Ela valida semanticamente:

- email
- phone
- cpf
- cnpj
- currency
- date

Por default, ela vem desligada:

- `validate_field_format=False`

Isso foi intencional.

### Regras customizadas do usuario

O fluxo de update ja aceita `extra_rules`.

Esse suporte foi exposto ate a facade:

- `api.cards.updateField(..., extra_rules=[...])`
- `api.cards.updateFields(..., extra_rules=[...])`

Tambem foi criada uma regra utilitaria para regex:

- `RegexFieldPatternRule`

Ela permite cenarios como:

- validar um campo com padrao de codigo interno
- validar um identificador de negocio
- reforcar um contrato customizado sem criar uma classe de regra completa

Mas o usuario continua livre para criar qualquer `BaseRule` propria.

Esse ponto e importante porque preserva extensibilidade sem deformar o core do SDK.

---

## PipeService: catalogo de schema do pipe

Foi implementado um recurso importante para discovery de campos:

- `api.pipes.getFieldCatalog(pipe_id)`
- `PipeService.getPipeFieldCatalog(pipe_id)`

### Intencao

Obter o schema configurado no pipe inteiro, usando models, e nao `dict` cru.

Ou seja:

- retorna `Pipe`
- com `phases`
- e cada `Phase` com `fields`

### Descoberta importante

A tentativa inicial de buscar `phases { fields { ... } }` diretamente na query de `pipe` nao trouxe `fields` preenchidos de forma confiavel.

Correcao aplicada:

- buscar o pipe com as fases
- enriquecer cada fase usando `PhaseService.getPhaseModel(phase_id)`

Isso tornou o catalogo confiavel.

### Teste

`Tests/pipService.py` foi atualizado e agora:

- testa `pipes.getFieldCatalog`
- imprime a estrutura completa do catalogo

Esse catalogo e muito importante para o proximo passo de cache de schema.

---

## Testes relevantes ja existentes

### Arquivos principais

- `Tests/fileService.py`
- `Tests/cardService.py`
- `Tests/phaseService.py`
- `Tests/pipService.py`
- `Tests/cardUpdateFlow.py`

### Observacoes

- `fileService.py`
  - ja foi reorganizado e passou

- `cardUpdateFlow.py`
  - cobre o fluxo novo de update
  - ja passou

- `pipService.py`
  - agora inclui o teste do catalogo de fields
  - imprime a estrutura do pipe/fases/campos

Separacao mental correta:

- testes publicos devem passar pela facade
- testes internos de infraestrutura podem tocar internals quando isso for o proprio objeto do teste

---

## Cache de schema: decisao tomada e proximo passo importante

Foi discutida a ideia de manter um cache do schema do pipe para evitar buscar o schema a cada update.

### Direcao escolhida

Nao implementar thread de refresh em background como primeira versao.

### Motivo

Thread de background adiciona muita complexidade:

- lifecycle
- shutdown
- concorrencia
- stale data menos previsivel
- complexidade de debugging
- mais dificuldade de explicar comportamento do SDK para o usuario
- maior custo de manutencao para um ganho que ainda nao foi provado como necessario
- mais pontos de falha silenciosa

O cache precisa existir, mas a primeira versao deve ser deliberadamente simples, previsivel e facil de auditar.

### Estrategia correta para a primeira fase

Implementar:

- cache em memoria
- por `pipe_id`
- com TTL
- lazy refresh on demand
- lock por chave
- invalidador manual

Essa primeira fase deve ser pensada como um cache de leitura de schema, nao como um subsistema autonomo.

Ou seja:

- ele nao "roda sozinho"
- ele nao depende de thread propria
- ele nao tenta adivinhar quando deve atualizar em background
- ele apenas responde de forma eficiente quando o SDK precisa de schema

### Motivacao tecnica real para o cache

O motivo do cache nao e apenas performance generica. O motivo e estrutural.

Hoje o SDK ja tem um fluxo de update de card que depende de schema para:

- descobrir o tipo do campo
- descobrir opcoes configuradas
- validar compatibilidade do valor enviado
- decidir se o campo pertence ou nao a fase atual
- no futuro, potencialmente orientar heuristicas mais ricas por familia de campo

Se a cada execucao de update esse schema precisar ser reconsultado da API, teremos:

- mais latencia
- mais custo de rede
- mais dependencia de disponibilidade imediata da API
- repeticao de trabalho para estruturas que mudam pouco

O schema do pipe tende a ser muito menos volatil que os dados do card.

Isso torna o cache uma otima troca:

- o estado do card continua sendo buscado de forma fresca
- o schema do pipe/fase pode ser reutilizado com TTL

### Fonte da verdade do cache

O cache deve armazenar models, nao dicionarios crus.

Mais especificamente:

- `Pipe`
- contendo `phases`
- contendo `Phase.fields`
- contendo `PhaseField`

Ou seja, o cache deve operar sobre a mesma estrutura de dominio que o resto do SDK ja usa.

Isso evita criar mais um formato intermediario e reduz risco de incoerencia.

### Escopo correto do cache

O cache deve ser orientado por `pipe_id`.

Racional:

- o schema e, por natureza, uma propriedade do pipe e das fases do pipe
- se o SDK souber o `pipe_id`, ele consegue obter um catalogo reutilizavel do conjunto de fases e campos
- esse catalogo pode ser usado por varios cards diferentes do mesmo pipe

Isso e melhor do que cachear por `card_id`, porque:

- o card muda com muito mais frequencia
- o schema e compartilhado
- o objetivo aqui e reuso estrutural

### Interface sugerida para o cache

Uma interface boa para a primeira versao seria algo como:

- `get(pipe_id) -> Pipe | None`
- `set(pipe_id, pipe_schema) -> None`
- `getOrLoad(pipe_id, loader) -> Pipe`
- `invalidate(pipe_id) -> None`
- `invalidateAll() -> None`

Cada entrada deve carregar metadados como:

- `loaded_at`
- `expires_at`
- opcionalmente `last_access_at`

### Semantica de expiracao

O cache deve funcionar com TTL.

Comportamento esperado:

- se existe entrada valida, retorna imediatamente
- se nao existe entrada, carrega
- se a entrada expirou, recarrega sob lock
- se varias threads pedirem a mesma chave ao mesmo tempo, apenas uma carrega e as outras aguardam

Esse ultimo ponto e importante para evitar avalanche de requests em caso de expiracao simultanea.

### Onde esse cache deve viver

A recomendacao mais coerente no projeto atual e colocá-lo perto do dominio de pipe, e nao como cache global generico.

Candidatos adequados:

- `src/pipefy/service/pipe/cache/pipeSchemaCache.py`
- ou `src/pipefy/cache/pipeSchemaCache.py`

A melhor opcao hoje parece ser a primeira:

- `service/pipe/cache/pipeSchemaCache.py`

Porque o objeto que esta sendo cacheado e schema de pipe, nao qualquer coisa do SDK.

### Integracao esperada com o update de card

No fluxo de update de card, o uso ideal do cache e:

1. carregar o card atual
2. descobrir o `pipe_id` relacionado
3. consultar o cache do schema do pipe
4. obter a fase atual a partir do `Pipe.phases_map`
5. usar `Phase.fields_map` para validacoes e resolucao de tipo

Observacao importante:

- o estado do card deve continuar vindo da API em tempo real
- o cache nao substitui o carregamento do card
- o cache substitui apenas a parte de schema repetitivo

Isso precisa ficar muito claro para evitar um erro conceitual futuro: cachear dado de card como se fosse schema.

### Responsabilidades do cache

O cache deve:

- armazenar schema modelado do pipe
- controlar expiracao
- sincronizar concorrencia por chave
- oferecer invalidacao manual

O cache nao deve:

- decidir politica de negocio
- montar queries
- fazer validacao de formato
- conhecer dispatcher de update
- rodar loops autonomos em background na primeira versao

### Parametros desejaveis

Quando for implementado, seria bom prever configuracao como:

- `enabled=True`
- `ttl_seconds=300`
- `max_entries=100`
- `background_refresh=False`

Mesmo que `max_entries` ainda nao seja plenamente explorado no primeiro momento, vale a pena deixar a ideia registrada porque evita crescimento descontrolado no futuro.

### Estrategia de fallback

Mesmo com cache, o SDK deve continuar robusto quando:

- o cache estiver vazio
- a entrada tiver expirado
- o carregamento do schema falhar

Ou seja:

- cache e acelerador
- nao dependencia rigida para funcionamento basico

Se o cache falhar em algum ponto interno, o SDK ainda deve ser capaz de buscar o schema diretamente, ou ao menos falhar de forma clara e sem corromper estado.

### Invalidation

Precisamos considerar que o schema do pipe pode mudar:

- campos novos
- campos removidos
- opcoes alteradas
- campos movidos entre fases

Portanto, o cache deve prever:

- expiracao por TTL
- invalidacao explicita por `pipe_id`
- invalidacao total

No futuro, se o usuario souber que alterou o pipe, ele pode explicitamente invalidar o schema.

### Por que nao background refresh agora

Vale repetir de forma mais forte:

A ideia de refresh em thread paralela nao foi rejeitada para sempre. Ela foi adiada por prudencia arquitetural.

Hoje ela nao e a melhor primeira entrega porque:

- adiciona muito estado implícito
- dificulta reproducao de bugs
- torna o comportamento do SDK menos obvio
- exige politicas adicionais de ciclo de vida
- nao ha evidencia ainda de que o ganho supera a complexidade

Se no futuro isso voltar, deve ser:

- opcional
- desativado por default
- restrito a chaves ja acessadas
- bem documentado

### Sequencia recomendada de implementacao

Quando este trabalho comecar, a ordem recomendada e:

1. criar o modulo de cache do schema do pipe
2. implementar entrada com TTL e lock por chave
3. integrar com `PipeService.getFieldCatalog`
4. integrar com `CardUpdateFlow`
5. expor invalidacao manual se fizer sentido
6. so depois pensar em background refresh opcional

Essa ordem minimiza risco e deixa o ganho aparecer cedo.

### Beneficios esperados

Se implementado corretamente, o cache deve trazer:

- menor latencia no update de card
- menos round-trips para buscar schema
- menor custo operacional em cenarios com muitos updates
- validacoes opcionais mais baratas
- melhor base para futuras features orientadas a schema

### Riscos principais

Os riscos que precisam ser conscientemente controlados sao:

- schema stale
- crescimento descontrolado do cache
- lock mal desenhado causando contencao desnecessaria
- mistura entre dado de card e schema de pipe

Esses riscos sao exatamente o motivo para a primeira versao ser simples.

### Uso esperado

O fluxo de update de card consultaria esse cache para:

- schema de fase
- tipo do campo
- opcoes
- metadados de validacao

### Segunda fase futura, se realmente fizer sentido

- refresh em thread opcional
- desativado por default

Essa decisao ja foi tomada.

Nao voltar para thread em background como default sem justificativa forte.

---

## Aprendizado consolidado sobre nomenclatura dos tipos de campo

Ao comparar o SDK com a documentacao oficial, foi observado que:

- a documentacao usa nomes que nem sempre batem exatamente com o que o codigo tinha inicialmente
- exemplo importante: `assignee_select`

Tambem foi identificado que a documentacao lista mais tipos do que os inicialmente suportados.

Isso levou a expansao do enum e do registry por familias.

Conclusao:

- o enum de tipos deve continuar sendo tratado como contrato central
- aliases e divergencias com a doc devem ser tratados de forma explicita
- o dispatcher deve crescer por familias, nao por adicao desorganizada de casos especiais

---

## O que nao fazer

Este projeto ja tem varias decisoes maduras. Portanto, evitar:

- reintroduzir queries inline massivas em services
- reespalhar retry/circuit breaker pelos steps
- colocar validacao de options dentro do dispatcher
- usar `dict` cru como fonte de verdade quando ja existe model
- embrulhar erros semanticos em `RequestError` generico sem necessidade
- refazer flow de update usando mutation especifica por tipo como estrategia principal
- adicionar thread de cache em background cedo demais
- usar imports legados que ja foram removidos

---

## O que ainda esta em aberto

Existem pontos de evolucao, mas nao pontos de crise.

### Em aberto com alto valor

1. cache de schema do pipe com TTL e lock
2. expandir testes do update para mais tipos novos
3. refinar semantica profunda de alguns tipos novos, se necessario
4. documentar melhor exemplos de `extra_rules` e `RegexFieldPatternRule`

### Em aberto, mas nao prioridade imediata

1. background refresh opcional do cache
2. especializacoes mais profundas de connector
3. validacoes muito especificas de dominio por tipo

---

## Estado mental correto do projeto neste momento

Estamos em uma fase muito boa do projeto.

Nao estamos mais:

- improvisando arquitetura
- tentando descobrir o shape do SDK
- acoplados ao upload
- com exceptions subutilizadas

Estamos agora em:

- consolidacao estrutural
- ganho incremental de capacidade
- reducao de custo operacional
- preparacao para performance e reuso

O projeto hoje ja tem bases fortes:

- workflow reutilizavel
- update de card funcional
- exceptions maduras
- service tree limpa
- facade preservada
- models como fonte de verdade

Isso significa que as proximas entregas devem ser feitas com calma e criterio, evitando solucoes apressadas.

---

## Proximo passo recomendado

O proximo passo tecnico mais coerente e:

### Implementar cache de schema do pipe

Com estas caracteristicas:

- em memoria
- por `pipe_id`
- TTL configuravel
- lock por entrada
- carregamento sob demanda
- invalidador manual
- sem thread em background na primeira versao

Uso primario:

- fluxo de update de card
- validacoes de schema/opcoes/tipo
- possivel reuso por outros fluxos

---

## Resumo final para retomada futura

Se uma nova sessao precisar retomar daqui, a leitura correta e:

1. o SDK ja tem workflow generico consolidado
2. o subdominio de file esta organizado por fluxo
3. exceptions foram reorganizadas e fortalecidas
4. services foram reorganizados por dominio
5. queries e mutations foram extraidas para modulos dedicados
6. o fluxo novo de update de card ja existe, funciona e esta integrado na facade
7. o dispatcher de update ja cobre uma familia ampla de tipos
8. validacoes opcionais de formato e regex customizada ja existem
9. o PipeService ja consegue construir um catalogo modelado de schema do pipe
10. o proximo passo mais valioso e cache de schema com TTL e lock

Se for continuar o desenvolvimento, nao voltar para uma arquitetura anterior.
Continuar a partir do estado atual consolidado.
