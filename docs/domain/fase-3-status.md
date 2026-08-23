# Status da Fase 3 — Database e Ingestão

## O que foi validado de verdade

- **Schema**: todas as tabelas de `infra/database/models.py` compilam sem erro contra o dialeto PostgreSQL real (`CreateTable(...).compile(dialect=postgresql.dialect())`), incluindo o índice BRIN.
- **Migration**: `infra/database/migrations/versions/0001_initial_schema.py` roda em `alembic upgrade head --sql` (modo offline, gera DDL sem precisar de conexão) sem erro, produzindo SQL válido de Postgres.
- **Parsing de ingestão**: `infra/external_data/tesouro_direto.py` e `bcb_sgs.py` testados com dado real capturado nesta sessão (linhas reais do CSV do Tesouro Transparente, resposta real da API do BCB/SGS) — 15 testes unitários, todos passando.
- **mypy --strict**: limpo em `domain/` e `infra/`.

## O que NÃO foi validado

Este ambiente de desenvolvimento não tem PostgreSQL disponível (sem Docker, sem `psql`). Isso significa:

- `infra/database/repositories.py` (upsert idempotente via `ON CONFLICT DO UPDATE`) está escrito e com testes em `tests/integration/test_ingestion_repositories.py`, mas **esses testes nunca rodaram de verdade** — ficam marcados `@pytest.mark.integration` e são pulados automaticamente sem `DATABASE_URL` configurada. Rodam pela primeira vez em CI (contra um container Postgres) ou contra uma instância Neon de desenvolvimento.
- Os scripts `scripts/ingest/ingest_tesouro_direto.py` e `ingest_bcb_sgs.py` nunca foram executados ponta a ponta contra um banco real — só suas dependências (parsing, validação) foram exercitadas isoladamente.

Não estou reportando isso como "concluído" — está implementado e coberto por teste, mas a prova de que o SQL gerado (incluindo o `ON CONFLICT` específico do Postgres) funciona de verdade contra um servidor real ainda não existe. Primeira ação ao ter acesso a um Postgres (Neon ou local): rodar `alembic upgrade head` de verdade e a suíte `-m integration`.

## Decisões tomadas nesta fase

- **Ingestão do Tesouro Direto processa só a Data Base mais recente por padrão** (`filter_by_quote_date`), não o histórico de ~20 anos inteiro a cada execução — o arquivo é cumulativo e Data Base passada não muda retroativamente. Modo `--backfill` existe para a carga inicial única.
- **Códigos de série do BCB/SGS (11 = Selic diária, 433 = IPCA variação mensal) verificados por chamada real à API** nesta sessão, não por memória — resposta JSON capturada e usada como fixture de teste.
- **VNA de IPCA será construído a partir da variação mensal (série 433), não de um índice-número direto** — matematicamente equivalente (a razão IPCA_t/IPCA_0 da fórmula ANBIMA é o produto acumulado dos fatores mensais), e evita depender de uma série de índice-número que não localizamos com confiança no SGS.
- **`index_series_points` ganhou uma coluna `unit_period`** (não estava no discovery original) porque Selic (diária) e IPCA (mensal) sob a mesma tabela sem essa distinção seriam ambíguos de interpretar depois.
- Seed das tabelas `tax_brackets`/`custody_fee_schedules` com os valores já validados (`docs/domain/tributacao-fontes.md`) **não foi feito nesta etapa** — schema pronto, população fica para quando houver um banco real para popular.
