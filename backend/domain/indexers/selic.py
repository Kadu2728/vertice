from decimal import Decimal

from domain.shared.money import Money
from domain.shared.rounding import round_half_up, truncate

BASE_VALUE = Decimal(1000)


def vna_selic(daily_factors: list[Decimal]) -> Money:
    """VNA = 1.000 × fator diário da Taxa Selic acumulado desde a
    data-base (inclusive) até a data de referência (exclusive). Cada fator
    diário já deve vir arredondado conforme a regra oficial do BCB (8 casas
    no primeiro dia útil, acumulado a partir do segundo — ver
    docs/domain/precificacao-anbima.md, nota do "Fator Acumulado da Taxa
    Selic"); esta função só acumula e aplica o arredondamento final A-16."""
    accumulated = Decimal(1)
    for factor in daily_factors:
        accumulated *= factor
    accumulated = round_half_up(accumulated, 16)  # Fator Acumulado da Taxa Selic: A-16
    return Money(truncate(BASE_VALUE * accumulated, 6))
