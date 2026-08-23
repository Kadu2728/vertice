from datetime import date
from decimal import Decimal

from domain.bonds.bond_series import BondSeries
from domain.bonds.bond_type import BondType
from domain.calendars.anbima import AnbimaCalendar
from domain.pricing.lft import price_lft
from domain.shared.money import Money
from domain.shared.rate import Rate, RateBasis

VNA = Money(Decimal("13842.567891"))


def test_price_lft_zero_rentabilidade_equals_vna():
    calendar = AnbimaCalendar()
    bond = BondSeries(id="LFT-2029", bond_type=BondType.LFT, maturity_date=date(2029, 3, 1))
    rentabilidade = Rate(Decimal("0"), RateBasis.NOMINAL)
    pu = price_lft(bond, date(2026, 1, 2), calendar, rentabilidade, VNA)
    assert pu.amount == VNA.amount


def test_price_lft_positive_rentabilidade_is_desagio_below_vna():
    calendar = AnbimaCalendar()
    bond = BondSeries(id="LFT-2029", bond_type=BondType.LFT, maturity_date=date(2029, 3, 1))
    rentabilidade = Rate(Decimal("0.005"), RateBasis.NOMINAL)
    pu = price_lft(bond, date(2026, 1, 2), calendar, rentabilidade, VNA)
    assert pu < VNA


def test_price_lft_negative_rentabilidade_is_agio_above_vna():
    calendar = AnbimaCalendar()
    bond = BondSeries(id="LFT-2029", bond_type=BondType.LFT, maturity_date=date(2029, 3, 1))
    rentabilidade = Rate(Decimal("-0.003"), RateBasis.NOMINAL)
    pu = price_lft(bond, date(2026, 1, 2), calendar, rentabilidade, VNA)
    assert pu > VNA
