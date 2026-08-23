# Fontes e validação — tributação

Rastreamento de onde cada regra tributária implementada em `domain/taxation/` veio e o que ainda falta confirmar contra o texto oficial antes de virar golden reference (§43 do prompt do projeto: nunca inventar regra tributária, sempre documentar a fonte).

## IR regressivo (`income_tax.py`)

- **Fonte**: Lei 11.033/2004, art. 1º.
- **Status**: tabela estável desde 2005, sem alteração legislativa conhecida. Confiança alta.
- **Pendente**: nenhuma ação — considerar validado até indicação em contrário.

## IOF regressivo (`iof.py`)

- **Fonte**: Decreto 6.306/2007, Anexo I — texto compilado conferido em http://www.planalto.gov.br/ccivil_03/_ato2007-2010/2007/decreto/d6306compilado.htm (baixado e parseado nesta sessão, 2026-08-21).
- **Status**: **validado**. Os 30 valores extraídos diretamente do HTML oficial (dia 1 = 96% ... dia 29 = 3%, dia 30 = 0%) conferem exatamente com os 29 já implementados em `_IOF_TABLE`. Nenhuma correção necessária.
- **Pendente**: nenhuma ação de valor. A4 (particularidade de IOF específica do Tesouro Direto além da tabela padrão) segue sem indicação de exceção na fonte consultada — considerar a tabela padrão como aplicável até indicação em contrário.

## Custódia B3

- **Fonte**: B3, "Tarifas de Tesouro Direto" (https://www.b3.com.br/pt_br/produtos-e-servicos/tarifas/tarifas-de-tesouro-direto/), cruzado com o comunicado oficial "Entenda a nova taxa de custódia" do Tesouro Direto sobre a mudança de modelo vigente desde 31/12/2024.
- **Regras confirmadas**:
  - 0,20% a.a. sobre o valor dos títulos, para Tesouro Selic, Tesouro IPCA+ e Tesouro Prefixado.
  - Tesouro Selic: isento até R$ 10.000,00 em estoque por CPF; acima disso, incide só sobre o excedente.
  - Provisionada diariamente pro rata a partir de D+1 da liquidação da compra; cobrança efetiva só ocorre em um de três eventos — venda antecipada, vencimento, ou pagamento de cupom semestral — o que ocorrer primeiro.
  - Tesouro Educa+ e Tesouro Renda+ têm regras próprias (isenção ao carregar até o vencimento; isenção de resgate até 4 e 6 salários-mínimos, respectivamente) — fora do escopo do MVP (§39 do prompt do projeto não lista esses títulos).
- **Pendente**: nenhuma ação para os 5 tipos de título do MVP. Percentual e isenção prontos para entrar em `tax_brackets`/`custody_fee_schedules` (schema versionado, `docs/00-discovery.md` §5) na Fase 3.

## PU — arredondamento intermediário e metodologia de VNA

- **Fonte**: "Metodologia ANBIMA de Precificação de Títulos Públicos Federais", versão novembro/2023 — ver `docs/domain/precificacao-anbima.md` para a tabela completa de truncamento/arredondamento por variável (A1) e as três fórmulas de projeção do VNA (A2), extraídas e revisadas nesta sessão.
- **Status**: A1 e A2 resolvidas com fonte primária. Pendência remanescente: confirmar a álgebra exata renderizada (não só as variáveis) contra o PU oficial publicado, via golden tests na Fase 2 — ver nota final de `precificacao-anbima.md`.
