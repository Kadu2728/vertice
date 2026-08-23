from decimal import Decimal

from domain.shared.decimal_math import decimal_power
from domain.shared.money import Money
from domain.shared.rounding import truncate

BASE_VALUE = Decimal(1000)  # Valor Nominal na Data-Base — 15/07/2000


def vna_month_closed(ipca_index_prev_month: Decimal, ipca_index_base_month: Decimal) -> Money:
    """Caso I — data do cálculo coincide com o dia 15 do mês, IPCA do mês
    anterior já divulgado. VNA = VN_db × (IPCA_{t-1} / IPCA_0).
    Ver docs/domain/precificacao-anbima.md, caso I."""
    factor = ipca_index_prev_month / ipca_index_base_month
    return Money(truncate(BASE_VALUE * factor, 6))


def vna_pro_rata_official(
    vna_prev_month: Money,
    ipca_index_t1: Decimal,
    ipca_index_t2: Decimal,
    business_days_elapsed: int,
    business_days_in_reference_window: int,
) -> Money:
    """Caso II — entre a divulgação do IPCA do mês anterior e o dia 15.
    VNA = VNA_{t-1} × (IPCA_{t-1}/IPCA_{t-2})^(du1/du2).
    Ver docs/domain/precificacao-anbima.md, caso II."""
    variation = truncate(ipca_index_t1 / ipca_index_t2, 16)  # Variação Mês Oficial: T-16
    exponent = Decimal(business_days_elapsed) / Decimal(business_days_in_reference_window)
    factor = truncate(decimal_power(variation, exponent), 14)  # Fator Pro Rata: T-14
    return Money(truncate(vna_prev_month.amount * factor, 6))


def vna_pro_rata_projected(
    vna_prev_month: Money,
    ipca_projection: Decimal,
    business_days_elapsed: int,
    business_days_in_reference_window: int,
) -> Money:
    """Caso III — após o dia 15, IPCA do mês corrente ainda não divulgado.
    Usa a projeção do Grupo Consultivo Macroeconômico ANBIMA.
    VNA = VNA_{t-1} × (1 + IPCA_proj)^(du1/du2). `ipca_projection` (A-2 na
    tabela ANBIMA) é dado externo — não calculado por este módulo.
    Ver docs/domain/precificacao-anbima.md, caso III, inclusive a regra de
    borda quando o dia 15 cai em dia não útil (projeção vale até o SEGUNDO
    dia útil após o dia 15, não o primeiro — responsabilidade de quem
    calcula business_days_elapsed respeitar isso)."""
    exponent = Decimal(business_days_elapsed) / Decimal(business_days_in_reference_window)
    factor = truncate(decimal_power(Decimal(1) + ipca_projection, exponent), 14)
    return Money(truncate(vna_prev_month.amount * factor, 6))
