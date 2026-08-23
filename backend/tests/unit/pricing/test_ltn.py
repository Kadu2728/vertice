from decimal import Decimal

from domain.pricing.ltn import price_ltn
from domain.shared.rate import Rate, RateBasis


def test_price_ltn_one_year_at_ten_percent():
    # du=252 (1 ano útil) e taxa=10% a.a. -> fator de desconto = 1.10 exato
    # PU = 1000 / 1.10 = 909.090909090909... truncado em 6 casas (T-6)
    rate = Rate(Decimal("0.10"), RateBasis.NOMINAL)
    pu = price_ltn(rate, business_days=252)
    assert pu.amount == Decimal("909.090909")


def test_price_ltn_zero_days_equals_face_value():
    rate = Rate(Decimal("0.10"), RateBasis.NOMINAL)
    pu = price_ltn(rate, business_days=0)
    assert pu.amount == Decimal("1000.000000")


def test_price_ltn_decreases_as_rate_increases():
    low_rate = Rate(Decimal("0.08"), RateBasis.NOMINAL)
    high_rate = Rate(Decimal("0.12"), RateBasis.NOMINAL)
    pu_low = price_ltn(low_rate, business_days=252)
    pu_high = price_ltn(high_rate, business_days=252)
    assert pu_high < pu_low
