# ADR-001 — Python/FastAPI para o backend

## Status
Aceito.

## Contexto
O núcleo do produto é um motor de cálculo financeiro que precisa: manipular `Decimal` com controle fino de arredondamento, expor uma API tipada e documentada, e mais adiante integrar com uma camada de IA (RAG, function calling, structured output) sem fricção.

## Decisão
Python com FastAPI, Pydantic para validação/serialização, NumPy/SciPy apenas onde a matemática realmente pedir (ex.: resolução de taxa por método iterativo em fluxo de caixa descontado), SQLAlchemy sobre PostgreSQL.

## Alternativas descartadas
- **Node/TypeScript no backend também** — unificaria a linguagem com o frontend, mas o ecossistema de precisão decimal e de bibliotecas de matemática financeira é mais maduro em Python, e a integração com ferramentas de IA (SDKs, RAG, embeddings) é nativa no Python sem camada extra.
- **Go** — performance e tipagem fortes, mas `Decimal` e o ecossistema de dados financeiros exigiriam mais código próprio, e a integração com LLM tooling é menos direta.

## Consequências
Fronteira `domain/` sem dependência de FastAPI é obrigatória (não opcional) para o motor continuar testável isoladamente e para não vazar `HTTPException` ou `Request` para dentro da lógica financeira.
