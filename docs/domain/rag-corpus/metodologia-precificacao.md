# Como o preço dos títulos públicos é calculado

Fonte: "Metodologia ANBIMA de Precificação de Títulos Públicos Federais" (versão novembro/2023) — iniciativa conjunta da ANBIMA, Secretaria do Tesouro Nacional, Banco Central e B3.

## Tesouro Prefixado (LTN)

Título zero-cupom: não paga juros no meio do caminho, só o valor de face (R$ 1.000,00) no vencimento. O preço de hoje é o valor de face descontado pela taxa de juros vigente, pelo número de dias úteis até o vencimento (convenção 252 dias úteis por ano).

## Tesouro Prefixado com juros semestrais (NTN-F)

Paga cupons de juros a cada seis meses (10% ao ano, convenção de mercado) além do valor de face no vencimento. O preço é a soma de todos os fluxos futuros (cada cupom mais o principal final), cada um descontado separadamente pela taxa de juros até a respectiva data de pagamento.

## Tesouro IPCA+ (NTN-B Principal) e Tesouro IPCA+ com juros semestrais (NTN-B)

O valor de face desses títulos é corrigido diariamente pela inflação (IPCA), através de um número chamado VNA (Valor Nominal Atualizado). O VNA parte de R$ 1.000,00 na data-base (15/07/2000) e acumula a variação do IPCA mês a mês. Quando o IPCA do mês corrente ainda não foi divulgado pelo IBGE, usa-se uma projeção (apurada pelo Grupo Consultivo Macroeconômico da ANBIMA) até que o valor oficial seja publicado, normalmente por volta do dia 15 de cada mês.

O preço final é essa base corrigida (VNA) multiplicada pela cotação — que reflete o efeito da taxa de juros real contratada, do mesmo jeito que a taxa afeta o preço de um título prefixado.

## Tesouro Selic (LFT)

Título pós-fixado: seu valor de face acompanha a taxa Selic diariamente (via um fator acumulado desde a data-base). O preço de negociação normalmente fica muito próximo desse valor corrigido, com um pequeno ágio ou deságio negociado no mercado secundário — por isso o Tesouro Selic é o título com menor oscilação de preço no curto prazo entre os cinco tipos.

## Truncamento, não arredondamento

Um detalhe técnico importante: o Preço Unitário (PU) final é **truncado** em 6 casas decimais, não arredondado — o mesmo vale para vários passos intermediários do cálculo (fator de desconto, VNA). Isso significa que o PU oficial é sempre ligeiramente menor ou igual ao que um arredondamento simples produziria, nunca maior.
