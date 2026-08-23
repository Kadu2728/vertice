# Status dos golden tests (Fase 2)

Este documento existe porque §45/§46 do projeto proíbem dizer que algo está pronto sem validação, e ADR-005 proíbe relaxar tolerância silenciosamente. Aqui está exatamente o que foi validado, o que não foi, e por quê — não só "21 testes passando".

Fonte de dados: Tesouro Transparente, `PrecoTaxaTesouroDireto.csv` (https://www.tesourotransparente.gov.br/ckan/dataset/taxas-dos-titulos-ofertados-pelo-tesouro-direto), baixado em 2026-08-21, Data Base 20/08/2026. Fixtures em `backend/tests/golden/fixtures/tesouro_transparente_2026_08_20.py`.

## Achado prévio: lado "Compra" vs. "Venda"/"PU Base"

O CSV publica `Taxa Compra`/`PU Compra` e `Taxa Venda`/`PU Venda` (que na amostra coletada é sempre idêntico a `PU Base`). Testado nos dois lados para LTN:

- **Compra**: `Taxa Compra` aplicada à fórmula oficial reproduz `PU Compra` quase exatamente (diferença de R$ 0,001–0,002 em PUs de R$ 500–950 — ruído de truncamento, não erro).
- **Venda/Base**: a mesma fórmula com `Taxa Venda` diverge sistematicamente de `PU Venda` por R$ 0,3–0,5, crescendo com o valor do PU mas não com o prazo — não é o padrão esperado de um erro de taxa (que escalaria com duration/prazo). Pesquisa externa (ver abaixo) indica que o regime de liquidação de compra e venda mudou em 13/09/2021 e são operacionalmente diferentes; a causa exata da divergência no PU Venda/Base não foi identificada.

**Decisão**: golden tests usam exclusivamente o lado Compra. Não inventamos uma explicação para o lado Venda — fica registrado como não compreendido, não como resolvido.

## LTN — validado

Tolerância R$ 0,01, dentro dela com folga (R$ 0,001–0,002 de diferença real). Prova calendário ANBIMA + fórmula LTN corretos. Gate de CI real — falha aqui é regressão, ponto final.

## NTN-F — gap real, não resolvido

PU calculado diverge do oficial numa quantidade que **cresce com o número de cupons remanescentes**: R$ 0,0025 (1 cupom) até R$ 0,065 (~21 cupons). Testado variando a casa de arredondamento da taxa semestral e do fluxo descontado de 5 a 16 casas — o resíduo não muda de forma relevante, o que descarta "precisão insuficiente" como explicação.

Duas hipóteses seguem abertas, nenhuma confirmada:
1. As datas de cupom usadas nos testes são sintéticas (geradas por convenção semestral a partir do vencimento), não a grade real de emissão da série específica — se a série real tiver datas de cupom ligeiramente diferentes, cada fluxo intermediário erra na direção certa para produzir exatamente este padrão.
2. Existe um passo de truncamento específico do Tesouro Direto para fluxos intermediários que a extração de texto do PDF da metodologia ANBIMA não capturou — as equações no documento são objetos gráficos, não texto (ver `docs/domain/precificacao-anbima.md`).

Pesquisa externa (um desenvolvedor terceiro que construiu um simulador equivalente e o validou contra 270 mil combinações históricas — https://www.tabnews.com.br/tesouroemfoco/criei-um-simulador-de-precificacao-do-tesouro-direto-e-o-validei-contra-270-mil-combinacoes-historicas-de-taxa-e-preco) confirma que esta família de título (prefixado/IPCA+ com juros semestrais) é a mais difícil de acertar bit-a-bit mesmo com esforço dedicado — ele atingiu 99,26% de acerto, não 100%, com falhas concentradas nesses tipos. Isso não resolve o problema, mas indica que não é um erro grosseiro do motor — é uma particularidade genuinamente fina da metodologia.

Teste atual (`test_ntnf_golden.py`) usa tolerância R$ 0,10, documentada e visível — não R$ 0,01. Continua pegando regressão grande, não finge precisão que não existe.

## NTN-B Principal — gap majoritariamente atribuível ao dado, não à fórmula

VNA usado (R$ 4.740,845804) veio de fonte terciária (brasilindicadores.com.br), não da série oficial ANBIMA/BCB — não conseguimos, dentro do escopo desta pesquisa, uma fonte primária de VNA histórico por data sem acesso pago à ANBIMA. O resíduo observado (~0,03% do PU na maioria dos casos, R$ 0,04–1,22 em PUs de R$ 900–3.850) é compatível com o VNA estar defasado por 1–3 dias de projeção de IPCA — a mesma fórmula de cotação zero-cupom já foi validada com folga de milésimos de real via LTN. Um caso (vencimento 2032) bateu quase exato (R$ 0,036), reforçando que a fórmula em si está correta e o ruído é do dado de entrada.

Tolerância atual: R$ 1,50, documentada. Revisitar com VNA oficial assim que a Fase 3 (ingestão) existir — nesse ponto, se o resíduo não cair para a ordem de centavos, o problema passa a ser da fórmula, não do dado, e este documento precisa ser atualizado.

## NTN-B (com cupom) — soma dos dois gaps acima

Resíduo até R$ 1,40 — não é um terceiro problema novo, é NTN-F (cupom) + NTN-B Principal (VNA) combinados. Resolver os dois de cima deve resolver este.

## LFT — sem golden test ainda

Não escrevemos golden test para LFT. Motivo: o VNA de LFT depende do fator diário acumulado da Taxa Selic (BCB), e não obtivemos, dentro do escopo desta pesquisa, uma fonte primária confiável do fator acumulado para a data-base usada nos outros testes. Inventar um número aqui violaria diretamente a regra do projeto contra alucinar dado financeiro (§43) — preferível deixar marcado como pendente a fingir uma validação que não existe.

**Pendência explícita para a Fase 3**: ingestão da série de Selic diária do BCB (SGS) permite construir este golden test com dado real.

## O que isso significa para a Fase 3 em diante

- `domain/pricing/ltn.py`: pronto, validado, sem ressalvas.
- `domain/pricing/ntnf.py` e `domain/pricing/ntnb.py`: implementação funcional e plausível, mas com gap de precisão documentado e não fechado — não tratar como "concluído" até a investigação acima avançar.
- `domain/indexers/ipca.py` (VNA): fórmula implementada conforme a metodologia oficial (casos I/II/III), mas sem validação golden própria — só validação indireta via NTN-B Principal com dado de terceiro.
- `domain/indexers/selic.py` (VNA): zero validação golden até agora. Prioridade alta assim que houver ingestão de Selic.
