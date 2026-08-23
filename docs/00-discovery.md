# VÉRTICE — Discovery Técnico (Fase 0)

Estado: aguardando aprovação. Nenhuma linha de código de produto foi escrita.

## 1. Visão arquitetural

VÉRTICE é um monólito modular com duas metades que nunca se confundem:

```
┌─────────────────────────────────────────────────────────┐
│                        FRONTEND                          │
│         Next.js 15 (SSR) · React · Tailwind · shadcn     │
└───────────────────────────┬───────────────────────────────┘
                             │ HTTP/JSON (OpenAPI v1)
┌───────────────────────────▼───────────────────────────────┐
│                      API (FastAPI)                        │
│   camada fina: validação de entrada, DTOs, orquestração   │
├───────────────────────────┬───────────────────┬───────────┤
│      MOTOR DETERMINÍSTICO │   CAMADA DE IA     │  INFRA    │
│  domain/ (pure Python,    │  explica, nunca    │ Postgres  │
│  sem I/O, sem framework)  │  calcula. Recebe   │ Redis     │
│  calendars · bonds ·      │  payload já        │ ingestão  │
│  taxation · pricing ·     │  calculado, chama  │ (GH       │
│  scenarios · market       │  function calling  │ Actions)  │
│                            │  de volta ao motor │           │
└────────────────────────────┴───────────────────┴───────────┘
```

Regra de fronteira, não de estilo: `domain/` não importa `fastapi`, `sqlalchemy`, `redis` nem qualquer SDK de LLM. Ele recebe primitivos e objetos de valor, devolve objetos de valor. Isso é o que torna os golden tests possíveis sem subir banco, API ou rede — e é o que garante que a camada de IA fisicamente não tem como calcular um PU, porque ela nunca importa o pacote que sabe fazer isso.

A API é orquestração, não lógica de negócio: recebe requisição, monta os objetos de domínio, chama o motor, persiste, devolve DTO. Se uma regra de tributação ou de precificação aparecer dentro de `api/routes/`, isso é um bug arquitetural, não uma escolha de estilo.

## 2. Arquitetura de pastas

```
vertice/
├── backend/
│   ├── domain/                      # zero dependência de framework/infra
│   │   ├── calendars/               # ANBIMA business-day calendar, du/252
│   │   ├── bonds/                   # LTN, NTN-F, NTN-B, NTN-B Principal, LFT
│   │   ├── indexers/                # IPCA, SELIC, CDI — séries e projeção de VNA
│   │   ├── taxation/                # IR regressivo, IOF, custódia B3
│   │   ├── pricing/                 # PU, marcação a mercado, fluxo de caixa
│   │   ├── scenarios/               # simulação de choque de taxa (bps)
│   │   └── shared/                  # Money, Rate, BusinessDate (value objects)
│   ├── application/                 # casos de uso: orquestra domain + repositórios
│   │   ├── simulations/
│   │   └── explanations/
│   ├── infra/
│   │   ├── database/                # SQLAlchemy models, Alembic migrations
│   │   ├── external_data/           # clients Tesouro Transparente, BCB/SGS
│   │   ├── cache/                   # Redis client, chaves versionadas
│   │   └── ai/                      # cliente LLM, RAG, guardrails, validador
│   ├── api/
│   │   └── v1/
│   │       ├── routes/
│   │       ├── schemas/             # DTOs Pydantic — nunca models internos
│   │       └── middleware/          # rate limit, CORS, logging
│   ├── scripts/
│   │   └── ingest/                  # entrypoints chamados pelo GH Actions
│   └── tests/
│       ├── unit/
│       ├── golden/
│       ├── integration/
│       └── api/
├── frontend/
│   ├── app/                         # App Router, rotas SSR de título
│   ├── components/
│   ├── lib/                         # cliente da API, formatação numérica
│   └── tests/
├── infrastructure/
│   └── ci/                          # workflows GitHub Actions
├── docs/
│   ├── adr/
│   └── domain/                      # metodologia de cálculo por título, fontes
└── README.md
```

Justificativa: `domain/` e `application/` separados porque casos de uso (ex.: "simular venda antecipada") coordenam repositório + motor + cache, mas não são regra financeira em si — se um dia o motor virar um pacote publicável isoladamente, `application/` fica para trás sem arrastar infra.

## 3. Modelagem do domínio financeiro

Objetos de valor (imutáveis, sem identidade):

- `Money` — `Decimal` + moeda (fixa em BRL no MVP, mas explícita para não confundir com taxa).
- `Rate` — `Decimal` anualizada, base 252, com contexto (nominal vs. real).
- `BusinessDate` — data + calendário associado; toda aritmética de prazo passa por aqui, nunca por `date2 - date1` cru.
- `CashFlow` — `(BusinessDate, Money, tipo: cupom|principal)`.

Entidades de domínio (com identidade, mas sem depender de ORM):

- `BondSeries` — uma série específica de título (ex.: NTN-B 2035): tipo, data de emissão, vencimento, taxa de cupom quando aplicável, indexador.
- `MarketQuote` — cotação oficial diária de uma série (taxa indicativa ANBIMA/Tesouro, PU, data).
- `IndexSeriesPoint` — valor de IPCA/SELIC/CDI em uma data de referência.
- `TaxationResult` — decomposição de IR, IOF e custódia sobre um resgate.
- `Simulation` — parâmetros de entrada do usuário (título, data de compra, valor) + resultado calculado, versionado por `calculation_engine_version`.
- `ScenarioResult` — resultado de um `Simulation` sob um choque de taxa (bps).

## 4. Entidades (visão de persistência)

| Entidade | Chave | Observação |
|---|---|---|
| `bond_series` | `id` (uuid) | catálogo de séries emitidas; fonte: Tesouro Transparente |
| `bond_market_quotes` | `(bond_series_id, quote_date)` | append-only, histórico diário oficial |
| `index_series_points` | `(indexer, reference_date)` | IPCA/SELIC/CDI, fonte BCB/SGS |
| `tax_brackets` | `id` versionado por `valid_from` | tabela IR regressiva, versionada no tempo |
| `custody_fee_schedules` | `id` versionado por `valid_from` | taxa de custódia B3, versionada |
| `simulations` | `id` (uuid não sequencial) | snapshot da entrada + resultado + `engine_version` |
| `scenario_results` | `(simulation_id, shock_bps)` | cache dos pontos do slider |

`simulations.id` é UUID v4 (não sequencial) porque também serve de identificador da URL pública de compartilhamento — um ID sequencial vazaria volume de uso e permitiria enumeração.

## 5. Banco de dados

PostgreSQL (Neon), migrations via Alembic.

Decisões de precisão (detalhe em [ADR-004](adr/ADR-004-financial-precision.md)):

- Valores monetários: `NUMERIC(18,6)` internamente (permite precisão de cálculo intermediário), formatados para 2 casas apenas na borda de apresentação.
- Taxas: `NUMERIC(12,8)`.
- PU: `NUMERIC(18,6)` — a casa decimal exata da metodologia oficial é um item a confirmar na Fase 1 contra a documentação ANBIMA/Tesouro (ver §17, ambiguidade A1). Nunca `FLOAT`/`DOUBLE PRECISION` em coluna financeira.

Índices:

- `bond_market_quotes`: índice composto `(bond_series_id, quote_date DESC)` para a consulta mais comum (última cotação / série temporal de um título).
- `index_series_points`: índice `(indexer, reference_date DESC)`.
- BRIN em `bond_market_quotes.quote_date`: **avaliado e adotado**. A tabela é append-only, ordenada fisicamente por data de ingestão (que coincide com `quote_date`), e cresce ~poucas centenas de linhas/dia por ano — padrão exatamente onde BRIN vence B-tree em custo de armazenamento sem perda relevante de performance em range scans por data. B-tree adicional continua existindo para o composto `(bond_series_id, quote_date)`, que é o padrão de acesso real da aplicação; BRIN cobre varreduras analíticas/ingestão por período. Não aplicado em `simulations` (baixo volume, sem padrão de escrita ordenada previsível) nem em `index_series_points` (volume pequeno o suficiente para B-tree simples).
- FKs com `ON DELETE RESTRICT` em tabelas de catálogo (`bond_series`, `tax_brackets`) — histórico financeiro não pode perder a série que referencia.

## 6. Contratos de API (v1)

```
GET  /health
GET  /ready

GET  /api/v1/bonds                          # catálogo de séries disponíveis
GET  /api/v1/bonds/{bond_series_id}/quotes  # histórico de cotação (paginado)

POST /api/v1/simulations                    # cria simulação a partir de título+data+valor
GET  /api/v1/simulations/{id}                # snapshot público (usado na URL compartilhável)
POST /api/v1/simulations/{id}/scenarios      # recalcula sob choque de taxa (bps)

POST /api/v1/explanations                    # gera texto explicativo a partir de um simulation_id
```

Todos os endpoints devolvem DTOs Pydantic próprios em `api/v1/schemas/`, nunca os modelos SQLAlchemy. `POST /simulations` é idempotente por payload (mesmo título+data+valor+engine_version reaproveita registro/cache em vez de duplicar linha). Erros seguem RFC 7807 (`application/problem+json`) — corpo estruturado com `type`, `title`, `detail`, em vez de string solta, para o frontend distinguir erro de validação de erro de dado ausente sem parsear mensagem.

## 7. Fluxo de dados

Simulação (caminho crítico, sem IA):

```
usuário → POST /simulations {bond_series_id, purchase_date, amount}
  → application/simulations: valida, busca BondSeries + MarketQuote + IndexSeries no repositório
  → domain/pricing: calcula PU na compra, PU hoje, PU no vencimento
  → domain/taxation: aplica IR regressivo + IOF (se <30d) + custódia
  → persiste Simulation (com calculation_engine_version)
  → devolve DTO com decomposição completa (bruto, líquido hoje, líquido vencimento, waterfall)
```

Explicação (opcional, best-effort):

```
frontend → POST /explanations {simulation_id}
  → application/explanations: recarrega Simulation (números já calculados, imutáveis)
  → monta payload estruturado (somente os campos definidos em §19 da spec original)
  → infra/ai: chama LLM com structured output (Pydantic)
  → infra/ai/validator: extrai números do texto gerado, compara contra o payload
  → diverge? descarta e usa template estático. converge? devolve texto.
```

## 8. Estratégia de ingestão

Job diário via GitHub Actions (sem fila, ver [ADR-002](adr/ADR-002-no-queue-mvp.md)):

```
Tesouro Transparente (CSV/API) ─┐
BCB/SGS (IPCA, SELIC, CDI)     ─┼→ download → validação de schema → normalização
                                 │   (tipos, casas decimais, datas)
                                 └→ deduplicação (chave natural) → upsert idempotente
                                     → validação pós-ingestão (contagem, gaps de data,
                                       outliers grosseiros) → log estruturado do resultado
```

Idempotência: upsert por chave natural (`bond_series_id + quote_date`, `indexer + reference_date`), nunca `INSERT` cego — reexecutar o job no mesmo dia não duplica nem quebra. Falha de ingestão não derruba a aplicação: dado do dia anterior continua servindo, e o job seguinte tenta de novo. Alerta (via log estruturado + step de CI que falha visivelmente) quando um dia útil passa sem ingestão bem-sucedida.

## 9. Estratégia de testes

Pirâmide, com peso deliberado nas camadas mais baratas e mais críticas:

- **Unit** (`domain/`): a maior fatia. Calendário, fórmulas de PU por tipo de título, tributação, arredondamento — cada um isolado, sem mock de infra porque não há infra para mockar.
- **Golden** (`tests/golden/`): motor completo contra dados oficiais publicados. Detalhe em §10.
- **Integration**: repositórios contra Postgres real (via container em CI), ingestão ponta a ponta contra fixtures gravadas das fontes oficiais, cache Redis.
- **API**: contrato (schema de request/response), erros, rate limiting — sem reexercitar lógica financeira que os testes unitários já cobrem.
- **Frontend**: componentes que exibem números (formatação, casas decimais, estados de loading/erro/vazio do waterfall e do slider de cenário).

Não perseguir cobertura por número. Um teste que não falha quando a lógica quebra não vale a linha que ocupa.

## 10. Estratégia dos golden tests

Este é o item que separa "calculadora que parece certa" de "motor validado".

- **Fonte da verdade**: preços e taxas indicativas publicados pelo Tesouro Transparente / ANBIMA, para uma amostra ampla de séries × datas × tipos de título.
- **Método**: para cada `(bond_series, quote_date)` no fixture congelado, o motor recebe apenas os inputs que um cálculo naquela data teria disponível (taxa indicativa do dia, VNA/IPCA já divulgado até aquela data) e reproduz o PU oficial.
- **Tolerância**: R$ 0,01 por título — adotada, mas condicional: só é válida onde a metodologia oficial permite chegar a essa granularidade sem ambiguidade de arredondamento intermediário (ver §17, A1). Onde não permitir, a tolerância real é documentada por tipo de título junto ao teste, nunca relaxada silenciosamente no código de produção.
- **Cobertura mínima**: os 5 tipos de título, múltiplos vencimentos, datas atravessando mudança de indexador/cupom, e pelo menos uma janela de estresse de mercado (para pegar erro de calendário/arredondamento que só aparece com taxa fora do comum).
- **Gate de CI**: golden tests rodam em todo PR que toca `domain/`. Falha de tolerância bloqueia merge — não é warning, é build vermelho.
- Fixtures ficam versionadas no repo (não buscadas ao vivo no teste), para o teste ser determinístico e não depender de a fonte externa estar no ar.

## 11. Estratégia de IA

Contrato de payload (motor → IA), campos numéricos como texto formatado, não `float`:

```json
{
  "bond_name": "Tesouro IPCA+ 2035",
  "purchase_date": "2024-03-10",
  "reference_date": "2026-08-21",
  "gross_value": "1234.56",
  "net_value_today": "1198.30",
  "net_value_at_maturity": "1810.00",
  "tax_ir": "36.26",
  "tax_iof": "0.00",
  "custody_fee": "1.94",
  "rate_impact": "-42.10",
  "index_impact": "+87.60",
  "engine_version": "2026.08.1"
}
```

- **Function calling**: perguntas contrafactuais ("e se eu vender em março?") traduzem-se em chamada tipada `simulate_sale(simulation_id, sale_date)` executada pelo motor; a LLM nunca infere a resposta, só a formata.
- **Structured output**: resposta da LLM validada contra schema Pydantic (`ExplanationOutput`: apenas campos textuais — título, corpo, avisos — nenhum campo numérico de fonte de verdade).
- **RAG restrito**: ~200 páginas de documentação oficial (Tesouro, tributação, regulatório). `pgvector` só se a alternativa mais simples (busca lexical / poucos documentos carregados em memória) não bastar — decisão a confirmar no início da Fase 6, não antes.
- **Validador numérico**: pós-geração, extrai todo número do texto (regex de valores monetários/percentuais) e compara contra o payload original; qualquer divergência descarta a resposta.
- **Guardrails**: bloqueio de perguntas de recomendação individualizada ("devo vender?") por classificação de intenção antes de chamar a LLM, com resposta padrão que redireciona para cenários objetivos — não é a LLM que se autocensura, é a camada de aplicação que nem chega a perguntar.
- **Fallback**: qualquer falha (timeout, provider fora do ar, schema inválido, divergência numérica) cai em template estático determinístico construído a partir do mesmo payload. Usuário nunca vê "erro de IA" — vê explicação, só que mais simples.

## 12. Estratégia de segurança

- Rate limiting por IP nos endpoints de escrita (`POST /simulations`, `/scenarios`, `/explanations`) — camada de middleware, não confiar em nada vindo do frontend.
- Validação de entrada estrita via Pydantic (datas dentro do intervalo emitido/vencido do título, valores positivos e com teto de payload razoável).
- CORS restrito ao domínio do frontend em produção.
- Headers de segurança padrão (CSP, X-Content-Type-Options, etc.) na resposta da API e do Next.js.
- Segredos exclusivamente via variável de ambiente — nunca em código ou log.
- SSRF: clients de dados externos (Tesouro Transparente, BCB/SGS, provider de LLM) com allowlist de host fixo, timeout curto e sem seguir redirect para host arbitrário.
- Logs estruturados sem PII — o produto não coleta CPF nem dado pessoal, então a superfície de vazamento é pequena por desenho, não por filtro após o fato.
- IDs de simulação pública são UUID v4 não sequencial (ver §4) — sem enumeração, sem exigir login para gerar.

## 13. Estratégia de cache (Redis)

- Chave: `simulation:{engine_version}:{hash(bond_series_id, purchase_date, amount, reference_date)}`.
- Chave de cenário: `scenario:{engine_version}:{simulation_id}:{shock_bps}`.
- `engine_version` **dentro da chave**, não como campo auxiliar — muda a versão do motor, a chave muda, o resultado antigo simplesmente não é encontrado (nunca é servido como se fosse equivalente). Resolve diretamente o risco citado na spec de tratar resultados de versões diferentes como iguais.
- TTL curto (ordem de horas) para simulação — dado de mercado muda diariamente, então cache de ontem não deve sobreviver ao próximo pregão. Invalidação principal é por tempo, não por evento.
- Cache de resposta de IA por `simulation_id` + hash da pergunta, TTL mais longo (o texto explicativo não muda com o tempo do jeito que o preço muda).
- Nada de cache indiscriminado em endpoints de leitura de catálogo (`/bonds`) — volume baixo, não justifica a complexidade de invalidação.

## 14. Estratégia de SEO

- Next.js SSR para páginas de título (`/tesouro-ipca-2035`, etc.), geradas a partir do catálogo real de séries — nenhuma página fabricada sem título e conteúdo correspondentes de fato existentes.
- `generateMetadata` por rota: title, description, canonical, Open Graph (incluindo imagem dinâmica com o resumo da série, quando fizer sentido).
- Structured data (`schema.org/FinancialProduct` ou equivalente aplicável) apenas se representar o conteúdo real da página, não como enchimento para rich snippet.
- Página de simulação compartilhada (`/s/{id}`) é indexável mas sem dado pessoal — OG tags descrevem o cenário (título + retorno), não o usuário.

## 15. Estratégia de observabilidade

- Logs estruturados (JSON) em cada camada: duração de cálculo do motor, duração de chamada externa (Tesouro/BCB/LLM), resultado de ingestão (linhas processadas, deduplicadas, rejeitadas), falhas de validação do payload de IA.
- `/health` (processo vivo) e `/ready` (dependências — Postgres, Redis — respondendo) separados, para o orquestrador de deploy diferenciar "reiniciar" de "não rotear tráfego ainda".
- Erros de motor financeiro logados com o input completo que os causou (sem dado pessoal, porque não existe) — reprodutibilidade total de qualquer PU calculado errado.
- Sem dado sensível em log porque não há dado sensível no sistema (não há CPF, não há login) — a política aqui é mais simples do que em produtos com autenticação.

## 16. Riscos técnicos

| Risco | Impacto | Mitigação |
|---|---|---|
| Metodologia de VNA (projeção pro-rata do IPCA) mal implementada | Preço de NTN-B/NTN-B Principal errado silenciosamente | Golden tests com janelas que cruzam datas de divulgação do IPCA; leitura da metodologia oficial ANBIMA antes de codar (§17, A1) |
| Casas decimais de arredondamento intermediário divergentes da convenção oficial | Diferenças de centavos que passam despercebidas em teste com tolerância larga | Tolerância documentada por tipo de título, nunca genérica; comparação também do PU intermediário, não só do valor líquido final |
| Fonte externa (Tesouro Transparente / BCB SGS) muda formato de CSV/API sem aviso | Ingestão quebra silenciosamente ou insere dado corrompido | Validação de schema explícita pós-download, falha ruidosa em vez de upsert de dado inválido |
| LLM aluccina número dentro de texto plausível | Usuário vê informação financeira errada com aparência de autoritativa | Validador numérico pós-geração (§11) é obrigatório, não opcional, antes de qualquer resposta chegar ao usuário |
| `float` entrando por conveniência em algum ponto da cadeia (ex.: lib externa) | Erro de precisão financeiro | `Decimal` de ponta a ponta no domain; conversão para tipo externo isolada e testada no ponto de fronteira |
| BRIN aplicado sem o padrão de escrita físico esperado se ingestão for reprocessada fora de ordem | Degradação de performance de leitura por correlação física quebrada | Ingestão sempre append cronológico; reprocessamento histórico via job separado que documenta a exceção, não via upsert solto |

## 17. Ambiguidades a resolver (não bloqueiam o discovery, bloqueiam a Fase 1 até serem fechadas com fonte oficial)

- ~~**A1 — Casas decimais e regras de arredondamento intermediário do PU por tipo de título.**~~ **Resolvida com fonte primária** — ver `docs/domain/precificacao-anbima.md` (tabela oficial de truncamento/arredondamento por variável e tipo de título, Metodologia ANBIMA nov/2023).
- ~~**A2 — Metodologia exata de projeção do VNA.**~~ **Resolvida com fonte primária** — as três fórmulas de projeção (dia 15, entre divulgação e dia 15, após dia 15) estão em `docs/domain/precificacao-anbima.md`, incluindo a regra de borda quando o dia 15 cai em dia não útil.
- ~~**A3 — Tabela vigente de custódia B3.**~~ **Resolvida** — 0,20% a.a., isenção de Tesouro Selic até R$ 10.000/CPF, cobrança em D+1 provisionada diariamente e efetivada só em venda/vencimento/cupom. Fonte em `docs/domain/tributacao-fontes.md`.
- ~~**A4 — Escopo de IOF abaixo de 30 dias.**~~ **Resolvida** — tabela regressiva padrão confirmada linha a linha contra o Decreto 6.306/2007, Anexo I (texto oficial do planalto.gov.br), idêntica à já implementada em `domain/taxation/iof.py`. Sem indicação de particularidade para Tesouro Direto na fonte consultada.
- **A5 — Provedor de LLM** para a camada de explicação (Fase 6): a spec não fixa. Proposta: Claude via API Anthropic, coerente com o restante do tooling do projeto — mas fica como proposta, não decisão, até a Fase 6.
- **A6 — Escopo inicial do catálogo de séries** (todas as séries em oferta hoje vs. um subconjunto para MVP) — não bloqueia arquitetura, mas afeta o volume do primeiro job de ingestão.

A1-A4 foram fechadas com fonte oficial pesquisada e documentada, não por suposição. A5 e A6 seguem abertas — não bloqueiam `domain/pricing` nem `domain/taxation`, só decisões de Fase 6 e de escopo de ingestão respectivamente.

## 18. ADRs iniciais

- [ADR-001 — Python/FastAPI para o backend](adr/ADR-001-python-fastapi.md)
- [ADR-002 — Sem fila (Celery/etc.) no MVP](adr/ADR-002-no-queue-mvp.md)
- [ADR-003 — A IA nunca calcula números](adr/ADR-003-ai-does-not-calculate.md)
- [ADR-004 — Estratégia de precisão financeira](adr/ADR-004-financial-precision.md)
- [ADR-005 — Estratégia de golden tests](adr/ADR-005-golden-tests.md)
- ADR-006 — Direção visual: escrito na Fase 5.0, depois que o motor existir e houver algo real para o design representar.

## 19. Roadmap de implementação

| Fase | Entrega | Critério de saída |
|---|---|---|
| 1 — Domínio financeiro | `domain/calendars`, `domain/bonds`, `domain/taxation`, `domain/pricing`, `domain/scenarios`, 100% testável sem infra | Unit tests verdes; nenhuma import de framework dentro de `domain/` |
| 2 — Golden tests | Motor validado contra dados oficiais para os 5 tipos de título | Tolerância definida por tipo respeitada; CI com gate vermelho funcional |
| 3 — Database + Ingestão | Schema, migrations, job de ingestão diário, validação pós-ingestão | Ingestão idempotente rodando 2x seguidas sem duplicar nem divergir |
| 4 — API | Endpoints v1, DTOs, OpenAPI, tratamento de erro RFC 7807 | Contrato documentado; testes de API cobrindo erro e sucesso |
| 5 — Frontend | 5.0 plano de design (aguarda aprovação) → 5.1 tokens → 5.2 telas | Direção visual aprovada antes de qualquer componente; fluxo completo funcionando sem login |
| 6 — IA | Payload, function calling, structured output, RAG restrito, validador, fallback | Fallback testado com provider desligado; validador rejeitando divergência numérica em teste |
| 7 — SEO + Performance | SSR, metadata, cache aplicado | Páginas de título indexáveis e reais |
| 8 — Hardening | Segurança, acessibilidade, observabilidade, auditoria anti-slop | `avoid-ai-design` em modo detect rodado e cada achado corrigido ou justificado |

## 20. Convenções de commit e estrutura do README

**Commits**: mensagem explica a decisão, não o diff (`git diff` já mostra o quê). Atômicos, um assunto por commit. Sem "wip", sem "update", sem sequência de "fix: fix bug". Sem menção a ferramenta de IA na mensagem ou em co-author.

Exemplo de formato aceitável:
```
Usa calendário ANBIMA em vez de dias corridos no cálculo de du/252

Diferença de 1 dia útil perto de feriado mudava o PU em centavos —
golden test da NTN-B 2029 pegou isso na data 2024-11-14.
```

**README**: abre pelo problema (por que marcação a mercado confunde investidores) e pela decisão técnica central (motor determinístico vs. camada de IA) — não por lista de features. Contém: como rodar, como testar, o que os golden tests provam (e contra qual fonte), diagrama de arquitetura (a mesma imagem de §1, ou evolução dela). Sem emoji em cabeçalho, sem linha de badges decorativa, sem seção "Contributing"/"Roadmap" genérica de template.
