from decimal import Decimal

from domain.bonds.bond_type import BondType
from domain.taxation.custody import custody_fee


def test_ltn_has_no_exemption():
    fee = custody_fee(BondType.LTN, Decimal("5000"), days_accrued=365)
    assert fee == Decimal("10.0000")  # 0,20% de 5000 por 1 ano


def test_lft_exempt_below_threshold():
    fee = custody_fee(BondType.LFT, Decimal("8000"), days_accrued=365)
    assert fee == Decimal("0")


def test_lft_charges_only_excess_over_threshold():
    fee = custody_fee(BondType.LFT, Decimal("15000"), days_accrued=365)
    assert fee == Decimal("10.0000")  # 0,20% dos R$ 5.000 excedentes


def test_zero_days_accrued_is_zero_fee():
    assert custody_fee(BondType.LTN, Decimal("5000"), days_accrued=0) == Decimal("0")


def test_fee_scales_with_days():
    half_year = custody_fee(BondType.LTN, Decimal("10000"), days_accrued=182)
    full_year = custody_fee(BondType.LTN, Decimal("10000"), days_accrued=365)
    assert half_year < full_year
