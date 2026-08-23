from decimal import Decimal

from domain.shared.decimal_math import decimal_power


def test_exponent_one_returns_base():
    assert abs(decimal_power(Decimal("1.10"), Decimal(1)) - Decimal("1.10")) < Decimal("1E-20")


def test_exponent_zero_returns_one():
    assert decimal_power(Decimal("1.10"), Decimal(0)) == Decimal(1)


def test_half_exponent_matches_native_sqrt():
    base = Decimal("1.10")
    result = decimal_power(base, Decimal("0.5"))
    assert abs(result - base.sqrt()) < Decimal("1E-20")
