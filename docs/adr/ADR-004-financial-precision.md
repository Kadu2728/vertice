# ADR-004 — Estratégia de precisão financeira

## Status
Aceito, com um ponto explicitamente aberto (ver Ambiguidade A1 no discovery).

## Contexto
Erros de ponto flutuante em `float`/`double` são inaceitáveis quando o resultado é um valor em reais mostrado a um investidor, e mais ainda quando ele é usado como golden test contra dado oficial com tolerância de centavo.

## Decisão
- `Decimal` em todo o `domain/`, sem exceção — nenhuma fórmula financeira opera sobre `float`.
- PostgreSQL: `NUMERIC`, nunca `FLOAT`/`DOUBLE PRECISION`, em qualquer coluna monetária, de taxa ou de PU.
- Precisão de armazenamento maior que a de apresentação: `NUMERIC(18,6)` para valores monetários internamente, formatação para 2 casas só na borda de exibição/serialização — arredondar cedo demais some com a diferença que um golden test existe para pegar.
- Regra de arredondamento explícita e centralizada por operação (não espalhada ad-hoc pelo código) — cada função de arredondamento do domínio documenta o método (`ROUND_HALF_UP` etc.) e por quê, porque a convenção varia por tipo de cálculo na prática de mercado.

## Alternativas descartadas
- **`float` com `round()` no fim** — mais simples, mas acumula erro de representação binária ao longo de cálculos encadeados (juros compostos, desconto de múltiplos fluxos); inaceitável para golden tests com tolerância de R$ 0,01.
- **Inteiro em centavos (`int`)** — evita ponto flutuante, mas taxas e fatores de desconto não são naturalmente inteiros; forçaria conversão para `Decimal` de qualquer forma em boa parte do motor, sem ganho real.

## Consequências
A casa decimal exata de arredondamento intermediário do PU por tipo de título (ANBIMA vs. Tesouro Direto podem divergir) ainda depende de leitura da metodologia oficial antes da Fase 1 fechar — este ADR fixa a estratégia (`Decimal`, `NUMERIC`, arredondamento explícito e centralizado), não o número de casas de cada fórmula específica.
