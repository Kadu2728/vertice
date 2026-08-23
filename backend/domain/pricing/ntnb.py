from datetime import date
from decimal import Decimal

from domain.bonds.bond_series import BondSeries
from domain.bonds.cash_flow import build_cash_flow_schedule
from domain.calendars.anbima import AnbimaCalendar
from domain.pricing.coupons import semiannual_coupon_rate
from domain.pricing.discounted_cash_flows import cotacao_zero_coupon, present_value_fraction
from domain.shared.money import Money
from domain.shared.rate import Rate
from domain.shared.rounding import truncate

_COTACAO_BASE = Decimal(100)
_COUPON_ROUNDING_PLACES = 6  # Juros Semestrais: A-6 (NTN-B, diferente da NTN-F)
_FLOW_ROUNDING_PLACES = 10  # Fluxo de Pagamentos Descontados: A-10 (NTN-B, diferente da NTN-F)


def price_ntnb(
    bond: BondSeries, settlement: date, calendar: AnbimaCalendar, tir: Rate, vna: Money
) -> Money:
    """NTN-B — IPCA+ com cupom semestral (6% a.a. sobre o VNA). Cotação vem
    do DCF em base 100; PU = (Cotação/100) × VNA. `vna` já deve vir
    calculado por domain/indexers/ipca.py para a data de liquidação — este
    módulo só desconta fluxos, não projeta índice. Ver docs/domain/precificacao-anbima.md §7.3.1."""
    if bond.coupon_rate_annual is None:
        raise ValueError("NTN-B exige coupon_rate_annual")
    semiannual_rate = semiannual_coupon_rate(bond.coupon_rate_annual, _COUPON_ROUNDING_PLACES)
    flows = build_cash_flow_schedule(bond, settlement, calendar, semiannual_rate)
    cotacao_fraction = present_value_fraction(flows, tir, _FLOW_ROUNDING_PLACES)
    cotacao = truncate(cotacao_fraction * _COTACAO_BASE, 4)  # Cotação: T-4
    pu = truncate((cotacao / _COTACAO_BASE) * vna.amount, 6)  # PU: T-6
    return Money(pu)


def price_ntnb_principal(
    bond: BondSeries, settlement: date, calendar: AnbimaCalendar, tir: Rate, vna: Money
) -> Money:
    """NTN-B Principal — strip de principal da NTN-B: mesmo VNA, sem cupom,
    fluxo único no vencimento. Metodologia ANBIMA não documenta uma seção
    própria para este título (ver nota em docs/domain/precificacao-anbima.md);
    tratado aqui como o caso particular n=1 da NTN-B, a confirmar em golden test."""
    du = calendar.business_days_between(settlement, bond.maturity_date)
    cotacao = cotacao_zero_coupon(tir, du)
    pu = truncate((cotacao / _COTACAO_BASE) * vna.amount, 6)  # PU: T-6
    return Money(pu)
