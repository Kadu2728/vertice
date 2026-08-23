# Status da Fase 4 — API

## Atualização — conectada a um Postgres real (Fase 5.3)

O item "rodar contra um Postgres real" deixou de ser pendência. Instalado PostgreSQL 17 localmente (`winget`), banco `vertice` criado, migrations rodadas, dados reais ingeridos do Tesouro Transparente (35 séries, duas Data Base: 02/01/2025 e a mais recente disponível) via `scripts/ingest/ingest_tesouro_direto.py` — que ganhou um flag `--date` pra permitir ingerir uma Data Base específica além do "dia mais recente" padrão. `scripts/seed_ntnf_coupons.py` (novo, uso único) preenche `coupon_rate_annual` e `bond_coupon_dates` das séries NTN-F — gap real da ingestão: o CSV do Tesouro não traz taxa de cupom nem calendário de pagamento.

Frontend (`frontend/lib/api.ts`) trocou o mock por chamadas reais (`GET /bonds`, `POST /simulations`, `POST /simulations/{id}/scenarios`, `GET /simulations/{id}`) — testado de ponta a ponta no navegador, número por número batendo com chamadas `curl` diretas à API.

**Incidente e correção**: os testes de integração (`tests/integration/`) usavam a mesma variável `DATABASE_URL` do ambiente de dev. Assim que `.env` passou a configurá-la para o Postgres real, rodar `pytest` também rodou os testes de integração contra o banco de dev — e o teardown da fixture (`Base.metadata.drop_all`) apagou toda a ingestão real. Corrigido com uma variável separada, `TEST_DATABASE_URL`, apontando para um banco `vertice_test` dedicado, mais uma checagem em runtime que recusa rodar se as duas variáveis apontarem para o mesmo lugar. Dado real re-ingerido depois da correção. Documentado aqui para não se repetir.

**Comparação com o vencimento removida do frontend**: existia como mock (dado estático, nunca uma feature real do backend). Com "deixa o mock pra depois", o componente foi removido em vez de mantido desconectado — a lógica de referência (valores calculados uma vez com as regras reais de IR/custódia) continua em `frontend/lib/mock-data.ts` como material de apoio para quando essa feature for implementada de verdade no backend.

## O que está pronto e validado

- **Contrato completo**: `/health`, `/ready`, `GET /api/v1/bonds`, `GET /api/v1/bonds/{id}`, `GET /api/v1/bonds/{id}/quotes`, `POST /api/v1/simulations`, `GET /api/v1/simulations/{id}`, `POST /api/v1/simulations/{id}/scenarios`. OpenAPI gera corretamente (`/openapi.json` verificado).
- **Erros em RFC 7807** (`application/problem+json`), com `type` em esquema `urn:vertice:error:...` em vez de uma URL https inventada.
- **130 testes passando** (domain + application + infra + API), **mypy --strict limpo em 56 arquivos** (`domain/`, `application/`, `infra/`, `api/`).
- **Simulação end-to-end funcional para LTN e NTN-F** — os dois tipos com precificação totalmente implementada e testada (ver `docs/domain/golden-tests-status.md`). Fluxo completo: cálculo de PU na compra e hoje, quantidade de títulos, valor bruto, IOF+IR (na ordem correta — IOF primeiro, IR sobre o rendimento já líquido de IOF), taxa de custódia, valor líquido.
- **Simulador de cenário** (`POST /simulations/{id}/scenarios`) aplica choque de taxa em bps (-200 a +200, passo 50) reaproveitando o mesmo motor — validado que choque positivo derruba preço e negativo eleva.

## Decisões tomadas nesta fase

- **`BondCatalogPort` (Protocol) como porta de inversão de dependência**: a API inteira é testável com um catálogo falso em memória, sem depender de Postgres (que este ambiente não tem). A implementação real (`infra/database/bond_catalog_repository.py`) satisfaz o mesmo Protocol mas nunca rodou contra um banco de verdade — mesma ressalva transparente das Fases 2 e 3.
- **NTN-B, NTN-B Principal e LFT ficam fora desta primeira versão da API** (`BondTypeNotYetSupported`, mapeado para HTTP 501): dependem de VNA, cuja orquestração (projeção de IPCA/Selic a partir dos dados brutos ingeridos na Fase 3) ainda não existe. Implementar isso agora, sobre uma base de VNA ainda não validada golden (ver Fase 2/3), teria criado uma API que promete um número que não é confiável — contra a prioridade #1 do projeto (correção matemática antes de completude de superfície).
- **`/api/v1/explanations` não foi implementado** — depende da camada de IA, que é Fase 6. Não pular etapa.
- **Ordem IOF→IR** implementada em `domain/taxation/net_proceeds.py`: IOF incide primeiro sobre o rendimento bruto, IR incide sobre o rendimento já líquido de IOF. Confirmado por múltiplas fontes de mercado, não por um único texto legal primário — sinalizado no código como premissa a validar juridicamente (§38 do prompt do projeto).
- **Simulação usa o lado "Compra"** (Tesouro compra do investidor) para ambas as pontas (compra e referência), não o par bid/ask completo — o lado "Venda" tem uma divergência de precisão ainda não compreendida (Fase 2). Modelar o bid/ask completo antes de resolver isso embutiria um erro não diagnosticado no núcleo do produto.

## Bug de infraestrutura de teste encontrado e corrigido

`tests/http_api/conftest.py` inicialmente definia constantes geradas dinamicamente (um `uuid4()`) que eram importadas por arquivos de teste via `from tests.http_api.conftest import LTN_ID`. Isso causou uma segunda instância do módulo (pytest importa `conftest.py` pelo próprio mecanismo de plugin, não por `import` comum) — o UUID usado pela fixture divergia do UUID usado pela URL da requisição, gerando 404 onde deveria haver 200. Corrigido movendo os dados compartilhados para `tests/http_api/support.py`, um módulo comum importado normalmente pelos dois lados. Documentado aqui porque é um erro sutil e fácil de reintroduzir sem essa explicação.

## Pendências explícitas

- Orquestração de VNA (IPCA/Selic) para destravar NTN-B/NTN-B Principal/LFT na API.
- `/api/v1/explanations` — Fase 6.
- Comparação com o vencimento como feature real de backend (removida do frontend, ver acima).
- Job de ingestão diário automatizado (GitHub Actions, ADR-002) — hoje é rodado manualmente neste ambiente de dev.
