from decimal import Decimal

import pytest

from domain.shared.money import Money


def test_addition_preserves_precision():
    a = Money(Decimal("1000.123456"))
    b = Money(Decimal("0.000001"))
    assert (a + b).amount == Decimal("1000.123457")


def test_rejects_float_input():
    with pytest.raises(TypeError):
        Money(1000.5)  # type: ignore[arg-type]


def test_rejects_mixed_currency():
    with pytest.raises(ValueError):
        Money(Decimal("10"), "BRL") + Money(Decimal("10"), "USD")


def test_to_display_rounds_half_up_to_two_places():
    assert Money(Decimal("10.005")).to_display() == Decimal("10.01")
    assert Money(Decimal("10.004")).to_display() == Decimal("10.00")


def test_zero_is_zero():
    assert Money.zero().is_zero()
