# Precificação — metodologia oficial ANBIMA (fonte primária de A1 e A2)

**Fonte**: "Metodologia ANBIMA de Precificação de Títulos Públicos Federais", versão novembro/2023.
URL: https://data-strapi.prd.anbima.com.br/uploads/Metodologias_ANBIMA_de_Precificacao_Titulos_Publicos_VF_7d2a9bb200.pdf
(também indexado em anbima.com.br/data/files/... — mesmo conteúdo, PDF binário; texto extraído via `pypdf` e revisado manualmente nesta sessão.)

Isso fecha as ambiguidades A1 e A2 do discovery (`docs/00-discovery.md` §17) com fonte primária, não com memória.

## A1 — Regras de arredondamento/truncamento por variável (§7, "Quadro Resumo")

Notação oficial: **T** = truncado, **A** = arredondado, **I** = informado (recebido pronto, não calculado). O número após a letra é a quantidade de casas decimais.

| Variável | LTN | NTN-F | NTN-B / NTN-B Principal¹ | LFT |
|---|---|---|---|---|
| Taxa de Retorno (% a.a.) | T-4 / I-4 | T-4 / I-4 | T-4 / I-4 | T-4 / I-4 |
| Juros Semestrais (%) | — | A-5 | A-6 | — |
| Fluxo de Pagamentos Descontados | — | A-9 | A-10 | — |
| Cotação | — | — | T-4 | T-4 |
| VNA (mês fechado) | — | — | T-6 / I-6 | T-6 / I-6 |
| VNA (projeção) | — | — | T-6 | T-6 |
| Fator acumulado Taxa Selic | — | — | — | A-16² |
| Projeção do índice | — | — | A-2 | — |
| Fator pro rata (projeção) | — | — | T-14 | — |
| Variação mês oficial | — | — | T-16 | — |
| Exponencial de dias | T-14 | T-14 | T-14 | T-14 |
| **PU** | **T-6 / I-6** | **T-6 / I-6** | **T-6** | **T-6** |
| Valor financeiro (R$) | T-2 | T-2 | T-2 | T-2 |

¹ A metodologia documenta NTN-B (com cupom) explicitamente; NTN-B Principal (strip, zero-cupom) usa a mesma linha de VNA/Cotação/PU — ver nota de implementação abaixo.
² "No primeiro dia útil, o fator da Taxa Selic é arredondado na oitava casa decimal; a partir do segundo dia útil, passa a ser acumulado e arredondado com 16 casas decimais."

**Implicação direta para `Money`/`Rate`**: PU trunca em 6 casas (não arredonda) antes de virar valor financeiro; valor financeiro final trunca em 2 casas. Isso já muda `domain/shared/money.py` e `rate.py`, que hoje só têm `ROUND_HALF_UP` — será necessário um modo de truncamento explícito por variável, não um arredondamento genérico. Tratar em `domain/pricing`, não alterar o objeto de valor genérico para não acoplar regra de um domínio específico a um objeto de uso geral.

## A2 — Projeção do VNA (NTN-B / NTN-B Principal), §7.3.1

Data-base: 15/07/2000, VN na data-base = R$ 1.000,00. Três casos, mutuamente exclusivos por data de liquidação:

**I. Data do cálculo coincide com o dia 15 do mês** (IPCA do mês anterior já divulgado pelo IBGE):
`VNA = VN_db × (IPCA_{t-1} / IPCA_0)`
onde `IPCA_{t-1}` é o número-índice do IPCA do mês anterior ao de referência, `IPCA_0` o número-índice do mês anterior à data-base.

**II. Entre a divulgação do IPCA do mês anterior e o dia 15**:
`VNA = VNA_{t-1} × (IPCA_{t-1} / IPCA_{t-2})^(du1/du2)`
`du1` = dias úteis entre o dia 15 do mês anterior (inclusive) e a liquidação (exclusive); `du2` = dias úteis entre os dois dias 15 consecutivos.

**III. Após o dia 15, IPCA do mês corrente ainda não divulgado** — usa projeção do Grupo Consultivo Macroeconômico ANBIMA:
`VNA = VNA_{t-1} × (1 + IPCA_proj)^(du1/du2)`
`du1` = dias úteis entre o dia 15 do mês de referência (inclusive) e a liquidação (exclusive); `du2` = dias úteis entre o dia 15 do mês de referência e o dia 15 do mês seguinte.

**Regra de borda**: se o dia 15 cair em dia não útil, a correção pelo IPCA oficial só acontece no dia útil seguinte — a projeção continua valendo até o **segundo** dia útil após o dia 15, não o primeiro.

`Cotação` (NTN-B, com cupom) = soma dos fluxos de juros (6% a.a. sobre VNA, convertido a taxa semestral) e do principal, descontados pela TIR (=taxa efetiva anual). `PU = (Cotação / 100) × VNA`.

## Fórmulas confirmadas por tipo (§7.1–7.4) — variáveis, não a álgebra renderizada

O PDF usa objetos de equação que não extraem como texto; as variáveis e a estrutura, porém, são explícitas e batem com a convenção de mercado padrão:

- **LTN**: zero-cupom. `PU = VN / (1+Taxa)^(du/252)`, `VN = 1000`, `du` = dias úteis entre liquidação (inclusive) e vencimento.
- **NTN-F**: cupom semestral (`i` definido em edital — 10% a.a. de mercado, mas o edital é a fonte real por série). `PU` = soma dos cupons + principal, descontados pela TIR, cada fluxo em `dui/252`.
- **NTN-B**: como acima, mas sobre `Cotação` em relação ao VNA (cupom 6% a.a. sobre VNA), depois `PU = (Cotação/100) × VNA`.
- **NTN-B Principal**: **não tem seção própria no documento**. Nota de implementação: é o strip de principal da NTN-B — mesmo VNA, mesma fórmula de `Cotação`, mas com um único fluxo (`n=1`, sem cupom, `Juros=0`). Decisão de engenharia, não a metodologia inventando algo novo — a validar contra golden test (PU oficial publicado de NTN-B Principal) na Fase 2, não presumir sem checar.
- **LFT**: `VNA = 1000 × fator diário acumulado da Taxa Selic` (BCB), `PU = (Cotação/100) × VNA`, `Cotação` calculada a partir do deságio/ágio (`Rentabilidade` negociada) via fórmula exponencial em `du/252`.

## Pendências que sobrevivem a esta pesquisa

- A fórmula algébrica exata renderizada (não só as variáveis) de cada bloco deve ser conferida contra o PU oficial publicado em golden tests (Fase 2) — a extração de texto não capturou os objetos de equação do PDF. Este documento contém tudo que é necessário para escrever a primeira versão da fórmula; o golden test é o que prova que a primeira versão está certa.
- Regra de arredondamento acima é a convenção **ANBIMA**. O documento (§7, cabeçalho) afirma que os padrões refletem "iniciativa conjunta da ANBIMA, STN, Banco Central e B3" para os sistemas de liquidação — ou seja, é razoável tratá-la como a convenção também usada pelo Tesouro Direto, mas isso não estava explícito letra por letra; golden test contra o histórico do Tesouro Transparente confirma na prática.
