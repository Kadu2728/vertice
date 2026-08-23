from datetime import date
from decimal import Decimal

from domain.bonds.bond_series import BondSeries
from domain.bonds.cash_flow import build_cash_flow_schedule
from domain.calendars.anbima import AnbimaCalendar
from domain.pricing.coupons import semiannual_coupon_rate
from domain.pricing.discounted_cash_flows import present_value_fraction
from domain.shared.money import Money
from domain.shared.rate import Rate
from domain.shared.rounding import truncate

FACE_VALUE = Decimal(1000)
_COUPON_ROUNDING_PLACES = 5  # Juros Semestrais: A-5
_FLOW_ROUNDING_PLACES = 9  # Fluxo de Pagamentos Descontados: A-9


def price_ntnf(bond: BondSeries, settlement: date, calendar: AnbimaCalendar, tir: Rate) -> Money:
    """NTN-F — prefixado com cupom semestral. PU = soma dos fluxos (cupom +
    principal) descontados pela TIR. Ver docs/domain/precificacao-anbima.md §7.2."""
    if bond.coupon_rate_annual is None:
        raise ValueError("NTN-F exige coupon_rate_annual")
    semiannual_rate = semiannual_coupon_rate(bond.coupon_rate_annual, _COUPON_ROUNDING_PLACES)
    flows = build_cash_flow_schedule(bond, settlement, calendar, semiannual_rate)
    pv_fraction = present_value_fraction(flows, tir, _FLOW_ROUNDING_PLACES)
    pu = truncate(pv_fraction * FACE_VALUE, 6)  # PU: T-6
    return Money(pu)
