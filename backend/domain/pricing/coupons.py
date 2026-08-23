from decimal import Decimal

from domain.shared.decimal_math import decimal_power
from domain.shared.rounding import round_half_up

_HALF = Decimal("0.5")


def semiannual_coupon_rate(annual_rate: Decimal, places: int) -> Decimal:
    """Converte cupom anual do edital em taxa semestral equivalente:
    (1 + i)^0.5 - 1. `places` é a casa de arredondamento da tabela ANBIMA —
    A-5 para NTN-F, A-6 para NTN-B (docs/domain/precificacao-anbima.md)."""
    rate = decimal_power(Decimal(1) + annual_rate, _HALF) - Decimal(1)
    return round_half_up(rate, places)
