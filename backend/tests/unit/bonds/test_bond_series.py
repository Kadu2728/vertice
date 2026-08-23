from datetime import date
from decimal import Decimal

import pytest

from domain.bonds.bond_series import BondSeries
from domain.bonds.bond_type import BondType


def test_ltn_accepts_no_coupon_fields():
    bond = BondSeries(id="LTN-2027", bond_type=BondType.LTN, maturity_date=date(2027, 1, 1))
    assert bond.coupon_rate_annual is None


def test_ltn_rejects_coupon_fields():
    with pytest.raises(ValueError):
        BondSeries(
            id="LTN-2027",
            bond_type=BondType.LTN,
            maturity_date=date(2027, 1, 1),
            coupon_rate_annual=Decimal("0.10"),
        )


def test_ntnf_requires_coupon_rate():
    with pytest.raises(ValueError):
        BondSeries(
            id="NTNF-2027",
            bond_type=BondType.NTN_F,
            maturity_date=date(2027, 1, 1),
            coupon_dates=(date(2027, 1, 1),),
        )


def test_ntnf_requires_coupon_dates_ending_at_maturity():
    with pytest.raises(ValueError):
        BondSeries(
            id="NTNF-2027",
            bond_type=BondType.NTN_F,
            maturity_date=date(2027, 1, 1),
            coupon_rate_annual=Decimal("0.10"),
            coupon_dates=(date(2026, 7, 1),),
        )


def test_ntnf_valid_series():
    bond = BondSeries(
        id="NTNF-2027",
        bond_type=BondType.NTN_F,
        maturity_date=date(2027, 1, 1),
        coupon_rate_annual=Decimal("0.10"),
        coupon_dates=(date(2026, 7, 1), date(2027, 1, 1)),
    )
    assert bond.coupon_dates[-1] == bond.maturity_date
