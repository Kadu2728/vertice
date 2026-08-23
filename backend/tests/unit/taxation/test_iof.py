from decimal import Decimal

import pytest

from domain.taxation.iof import iof_rate_for_holding_period


def test_first_day_is_96_percent():
    assert iof_rate_for_holding_period(1) == Decimal("0.96")


def test_day_29_is_3_percent():
    assert iof_rate_for_holding_period(29) == Decimal("0.03")


def test_day_30_and_beyond_is_zero():
    assert iof_rate_for_holding_period(30) == Decimal("0")
    assert iof_rate_for_holding_period(31) == Decimal("0")
    assert iof_rate_for_holding_period(365) == Decimal("0")


def test_rejects_negative_days():
    with pytest.raises(ValueError):
        iof_rate_for_holding_period(-1)
