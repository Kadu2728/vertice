from datetime import date
from decimal import Decimal

from domain.bonds.bond_series import BondSeries
from domain.bonds.bond_type import BondType
from domain.calendars.anbima import AnbimaCalendar
from domain.pricing.ntnb import price_ntnb, price_ntnb_principal
from domain.shared.money import Money
from domain.shared.rate import Rate, RateBasis

VNA = Money(Decimal("3200.123456"))


def test_price_ntnb_principal_zero_rate_equals_vna():
    calendar = AnbimaCalendar()
    bond = BondSeries(
        id="NTNBP-2035", bond_type=BondType.NTN_B_PRINCIPAL, maturity_date=date(2035, 5, 15)
    )
    tir = Rate(Decimal("0"), RateBasis.REAL)
    pu = price_ntnb_principal(bond, date(2026, 1, 2), calendar, tir, VNA)
    assert pu.amount == VNA.amount


def test_price_ntnb_principal_positive_rate_discounts_below_vna():
    calendar = AnbimaCalendar()
    bond = BondSeries(
        id="NTNBP-2035", bond_type=BondType.NTN_B_PRINCIPAL, maturity_date=date(2035, 5, 15)
    )
    tir = Rate(Decimal("0.06"), RateBasis.REAL)
    pu = price_ntnb_principal(bond, date(2026, 1, 2), calendar, tir, VNA)
    assert pu < VNA


def test_price_ntnb_at_par_when_tir_equals_coupon_rate():
    calendar = AnbimaCalendar()
    settlement = date(2026, 1, 2)

    def add_business_days(start: date, n: int) -> date:
        d = start
        added = 0
        while added < n:
            d = date.fromordinal(d.toordinal() + 1)
            if calendar.is_business_day(d):
                added += 1
        return d

    mid = add_business_days(settlement, 126)
    maturity = add_business_days(settlement, 252)

    bond = BondSeries(
        id="NTNB-PAR",
        bond_type=BondType.NTN_B,
        maturity_date=maturity,
        coupon_rate_annual=Decimal("0.06"),
        coupon_dates=(mid, maturity),
    )
    tir = Rate(Decimal("0.06"), RateBasis.REAL)
    pu = price_ntnb(bond, settlement, calendar, tir, VNA)
    assert abs(pu.amount - VNA.amount) < Decimal("0.20")
