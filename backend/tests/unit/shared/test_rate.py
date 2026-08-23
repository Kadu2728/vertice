from decimal import Decimal

from domain.shared.rate import Rate, RateBasis


def test_discount_factor_252_business_days_equals_one_year():
    rate = Rate(Decimal("0.10"), RateBasis.NOMINAL)
    factor = rate.discount_factor(252)
    assert abs(factor - Decimal("1.10")) < Decimal("0.0000001")


def test_discount_factor_zero_days_is_one():
    rate = Rate(Decimal("0.10"), RateBasis.NOMINAL)
    assert rate.discount_factor(0) == Decimal("1")


def test_rejects_float_input():
    import pytest

    with pytest.raises(TypeError):
        Rate(0.1, RateBasis.NOMINAL)  # type: ignore[arg-type]
