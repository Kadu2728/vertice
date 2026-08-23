from decimal import Decimal

from domain.indexers.selic import vna_selic


def test_vna_selic_no_factors_equals_base_value():
    assert vna_selic([]).amount == Decimal("1000.000000")


def test_vna_selic_accumulates_daily_factors():
    factors = [Decimal("1.0005"), Decimal("1.0005")]
    vna = vna_selic(factors)
    expected = Decimal(1000) * Decimal("1.0005") * Decimal("1.0005")
    assert abs(vna.amount - expected) < Decimal("0.000001")


def test_vna_selic_increases_with_more_factors():
    one_day = vna_selic([Decimal("1.0005")])
    two_days = vna_selic([Decimal("1.0005"), Decimal("1.0005")])
    assert two_days > one_day
