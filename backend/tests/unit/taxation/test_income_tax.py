from decimal import Decimal

import pytest

from domain.taxation.income_tax import ir_rate_for_holding_period


@pytest.mark.parametrize(
    "days_held,expected_rate",
    [
        (0, Decimal("0.225")),
        (180, Decimal("0.225")),
        (181, Decimal("0.20")),
        (360, Decimal("0.20")),
        (361, Decimal("0.175")),
        (720, Decimal("0.175")),
        (721, Decimal("0.15")),
        (5000, Decimal("0.15")),
    ],
)
def test_ir_rate_brackets(days_held, expected_rate):
    assert ir_rate_for_holding_period(days_held) == expected_rate


def test_rejects_negative_days():
    with pytest.raises(ValueError):
        ir_rate_for_holding_period(-1)
