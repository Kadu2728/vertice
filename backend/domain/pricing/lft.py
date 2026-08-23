from datetime import date
from decimal import Decimal

from domain.bonds.bond_series import BondSeries
from domain.calendars.anbima import AnbimaCalendar
from domain.pricing.discounted_cash_flows import cotacao_zero_coupon
from domain.shared.money import Money
from domain.shared.rate import Rate
from domain.shared.rounding import truncate

_COTACAO_BASE = Decimal(100)


def price_lft(
    bond: BondSeries, settlement: date, calendar: AnbimaCalendar, rentabilidade: Rate, vna: Money
) -> Money:
    """LFT — pós-fixado Selic. Cotação reflete o ágio/deságio negociado
    sobre a Selic; PU = (Cotação/100) × VNA. `vna` já deve vir calculado por
    domain/indexers/selic.py (fator Selic acumulado desde a data-base) —
    este módulo só desconta a cotação. Ver docs/domain/precificacao-anbima.md §7.4.1."""
    du = calendar.business_days_between(settlement, bond.maturity_date)
    cotacao = cotacao_zero_coupon(rentabilidade, du)
    pu = truncate((cotacao / _COTACAO_BASE) * vna.amount, 6)  # PU: T-6
    return Money(pu)
