"""Fixtures congeladas a partir do arquivo oficial "Taxas dos Títulos
Ofertados pelo Tesouro Direto" (Tesouro Transparente):

Fonte: https://www.tesourotransparente.gov.br/ckan/dataset/taxas-dos-titulos-ofertados-pelo-tesouro-direto
Arquivo: PrecoTaxaTesouroDireto.csv
Baixado em: 2026-08-21. Data Base usada: 20/08/2026 (última disponível no
momento do download).

Usamos exclusivamente o lado "Compra" (Taxa Compra Manha / PU Compra Manha)
porque é o único lado que reproduz de forma essencialmente exata a fórmula
oficial de PU a partir da taxa — ver docs/domain/golden-tests-status.md
para a investigação completa sobre por que o lado "Venda"/"PU Base" diverge
sistematicamente (não é bug do motor: é um dado de mercado que ainda não
identificamos a regra exata de formação, e por isso não vira golden
reference até isso ser resolvido)."""

from datetime import date
from decimal import Decimal
from typing import NamedTuple

SETTLEMENT = date(2026, 8, 20)


def semiannual_coupon_dates(maturity: date, settlement: date) -> tuple[date, ...]:
    """Gera as datas semestrais (mesmo dia/mês do vencimento, a cada 6
    meses) voltando ~25 anos. `build_cash_flow_schedule` descarta as
    anteriores à liquidação — geradas em excesso aqui de propósito, para
    não depender de conhecer a data de emissão real da série."""
    dates: list[date] = []
    cursor = maturity
    floor_year = settlement.year - 25
    while cursor.year > floor_year:
        dates.append(cursor)
        month = cursor.month - 6
        year = cursor.year
        if month <= 0:
            month += 12
            year -= 1
        cursor = cursor.replace(year=year, month=month)
    return tuple(sorted(dates))


class LtnCase(NamedTuple):
    maturity: date
    taxa_compra_pct: Decimal
    pu_compra_oficial: Decimal


LTN_CASES: tuple[LtnCase, ...] = (
    LtnCase(date(2027, 1, 1), Decimal("13.48"), Decimal("955.84")),
    LtnCase(date(2028, 1, 1), Decimal("13.90"), Decimal("838.52")),
    LtnCase(date(2029, 1, 1), Decimal("14.29"), Decimal("731.84")),
    LtnCase(date(2031, 1, 1), Decimal("14.62"), Decimal("554.21")),
    LtnCase(date(2032, 1, 1), Decimal("14.73"), Decimal("481.05")),
)


class NtnfCase(NamedTuple):
    maturity: date
    taxa_compra_pct: Decimal
    pu_compra_oficial: Decimal


# NTN-F: cupom 10% a.a. — convenção padrão de mercado para todas as séries
# em oferta. PU aqui NÃO é golden reference tight ainda (ver status doc);
# mantido para acompanhar o gap enquanto ele é investigado.
NTNF_CASES: tuple[NtnfCase, ...] = (
    NtnfCase(date(2027, 1, 1), Decimal("13.44"), Decimal("1002.62")),
    NtnfCase(date(2029, 1, 1), Decimal("14.11"), Decimal("939.69")),
    NtnfCase(date(2031, 1, 1), Decimal("14.64"), Decimal("877.89")),
    NtnfCase(date(2033, 1, 1), Decimal("14.77"), Decimal("832.61")),
    NtnfCase(date(2035, 1, 1), Decimal("14.79"), Decimal("801.04")),
    NtnfCase(date(2037, 1, 1), Decimal("14.76"), Decimal("778.36")),
)


class NtnbPrincipalCase(NamedTuple):
    maturity: date
    taxa_compra_pct: Decimal
    pu_compra_oficial: Decimal


# VNA usado: R$ 4.740,845804, obtido de fonte terciária (brasilindicadores.com.br,
# citando validade "a partir de 18/08/2026") — NÃO é fonte primária ANBIMA,
# por isso o gap observado aqui é parcialmente atribuível a imprecisão do
# VNA, não só à fórmula. Ver docs/domain/golden-tests-status.md.
NTNB_PRINCIPAL_VNA = Decimal("4740.845804")
NTNB_PRINCIPAL_CASES: tuple[NtnbPrincipalCase, ...] = (
    NtnbPrincipalCase(date(2029, 5, 15), Decimal("8.05"), Decimal("3847.04")),
    NtnbPrincipalCase(date(2032, 8, 15), Decimal("8.09"), Decimal("2985.55")),
    NtnbPrincipalCase(date(2035, 5, 15), Decimal("7.93"), Decimal("2446.97")),
    NtnbPrincipalCase(date(2040, 8, 15), Decimal("7.56"), Decimal("1721.43")),
    NtnbPrincipalCase(date(2045, 5, 15), Decimal("7.39"), Decimal("1257.73")),
    NtnbPrincipalCase(date(2050, 8, 15), Decimal("7.34"), Decimal("876.66")),
)


class NtnbCase(NamedTuple):
    maturity: date
    taxa_compra_pct: Decimal
    pu_compra_oficial: Decimal


# NTN-B: cupom 6% a.a. sobre o VNA. Mesmo VNA de NTNB_PRINCIPAL_VNA — mesma
# ressalva de fonte. Combina o gap de cupom (como NTN-F) com o gap de VNA
# (como NTN-B Principal); usado só para acompanhar a investigação conjunta.
NTNB_CASES: tuple[NtnbCase, ...] = (
    NtnbCase(date(2030, 8, 15), Decimal("8.10"), Decimal("4434.39")),
    NtnbCase(date(2032, 8, 15), Decimal("8.08"), Decimal("4309.86")),
    NtnbCase(date(2040, 8, 15), Decimal("7.67"), Decimal("4107.83")),
    NtnbCase(date(2050, 8, 15), Decimal("7.51"), Decimal("3994.06")),
)
