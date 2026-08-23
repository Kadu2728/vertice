from decimal import Decimal

from domain.shared.money import Money
from domain.shared.rate import Rate
from domain.shared.rounding import truncate

FACE_VALUE = Decimal(1000)


def price_ltn(rate: Rate, business_days: int) -> Money:
    """LTN — zero-cupom. PU = VN / (1+Taxa)^(du/252).
    Ver docs/domain/precificacao-anbima.md §7.1."""
    factor = truncate(rate.discount_factor(business_days), 14)  # Exponencial de Dias: T-14
    pu = truncate(FACE_VALUE / factor, 6)  # PU: T-6
    return Money(pu)
