# ADR-002 — Sem fila (Celery/etc.) no MVP

## Status
Aceito.

## Contexto
Existem dois candidatos naturais a trabalho assíncrono: a ingestão diária de dados oficiais, e eventualmente chamadas de IA mais longas. Fila (Celery + broker) é o reflexo padrão nesse cenário.

## Decisão
Ingestão roda como job diário simples via GitHub Actions (script Python invocado pelo workflow, sem worker de longa duração). Chamadas de IA são síncronas com timeout curto e fallback determinístico (ver ADR-003) — não precisam de fila porque não podem bloquear a resposta ao usuário além de um limite curto, e se estourarem esse limite a resposta cai para o template estático em vez de esperar numa fila.

## Alternativas descartadas
- **Celery + Redis/RabbitMQ como broker** — resolve um problema (processamento assíncrono de longa duração, retries distribuídos) que o produto não tem no MVP: a ingestão é um batch diário de volume pequeno, e a IA precisa responder rápido ou cair em fallback, não ser enfileirada para depois.
- **Fila serverless (SQS, Cloud Tasks)** — mesma objeção, com o custo adicional de outro serviço gerenciado para operar.

## Consequências
Se o volume de ingestão crescer (múltiplas fontes, múltiplas vezes ao dia) ou se surgir um caso de uso genuinamente assíncrono (ex.: processamento em lote sob demanda do usuário), este ADR é revisitado — não é uma rejeição permanente de fila, é a constatação de que introduzi-la agora seria infraestrutura sem carga real para justificá-la.
