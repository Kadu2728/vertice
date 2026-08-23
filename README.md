## VÉRTICE

Milhões de investidores possuem títulos públicos e não entendem por que o valor de mercado desses investimentos muda todo dia. Quando a taxa de juros muda, títulos prefixados e indexados ao IPCA sofrem marcação a mercado — o preço de negociação sobe ou desce mesmo sem nada "errado" ter acontecido. VÉRTICE simula essa marcação e explica o resultado em linguagem natural, sem exigir que o investidor entenda a matemática por trás.

### A decisão técnica central

O sistema é dividido em dois mundos que nunca se misturam:

- **Motor determinístico** (`backend/domain/`) — calcula todo preço, taxa, imposto e valor exibido. Puro Python, sem dependência de framework, banco ou IA — testável isoladamente.
- **Camada de IA** (`backend/application/explanations/`, `backend/infra/ai/`) — só explica em texto o que o motor já calculou. Nunca tem autoridade sobre número: um validador extrai todo valor monetário do texto gerado e descarta a resposta se algo não bater com o payload original, caindo num template estático determinístico.

Se um número aparece na tela, ele veio do motor. A IA nunca inventa, estima ou corrige um valor financeiro — essa fronteira é a razão de existir do projeto, não um detalhe de implementação.

## Como rodar

**Backend** (Python 3.12+, Postgres):

```bash
cd backend
python -m pip install -e .
cp .env.example .env  # preencher DATABASE_URL e TEST_DATABASE_URL
python -m alembic upgrade head
python -m scripts.ingest.ingest_tesouro_direto
python -m uvicorn api.main:app --reload --port 8000
```

**Frontend** (Node 20+):

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

## Como testar

```bash
cd backend
python -m pytest tests -v            # unitários, golden, API
python -m mypy domain application infra api  # tipagem estrita
```

## O que os golden tests provam

`backend/tests/golden/` recalcula o Preço Unitário de títulos reais, em datas reais, e compara com o preço oficial publicado pelo Tesouro Transparente. A LTN bate com tolerância de R$ 0,01 — validação real, não estimativa. NTN-F e NTN-B têm um resíduo de precisão documentado e ainda não resolvido (`docs/domain/golden-tests-status.md`); a tolerância desses testes é mais larga e visível no código, nunca afrouxada em silêncio.

## Documentação

- `docs/00-discovery.md` — arquitetura, modelagem de domínio, contratos de API, estratégia de dados.
- `docs/adr/` — decisões arquiteturais registradas, com a alternativa descartada e o motivo.
- `docs/domain/` — metodologia de precificação (com fonte oficial citada), status de cada fase, achados e incidentes ao longo da construção.
- `docs/design/` — direção visual aprovada e tokens de design.
