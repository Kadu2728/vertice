from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

from domain.shared.decimal_math import decimal_power

_QUANTUM = Decimal("0.00000001")  # NUMERIC(12,8) — ver ADR-004 e discovery §5


class RateBasis(str, Enum):
    """Distingue taxa nominal (prefixado) de taxa real (IPCA+), para nunca
    misturar as duas por engano em uma composição."""

    NOMINAL = "nominal"
    REAL = "real"


@dataclass(frozen=True, slots=True)
class Rate:
    """Taxa anualizada, convenção 252 dias úteis, expressa como fração
    (0.1045 == 10.45% a.a.), nunca como percentual inteiro."""

    annual_rate: Decimal
    basis: RateBasis

    def __post_init__(self) -> None:
        if isinstance(self.annual_rate, float):
            raise TypeError("Rate não aceita float — passe Decimal ou str")
        if not isinstance(self.annual_rate, Decimal):
            object.__setattr__(self, "annual_rate", Decimal(str(self.annual_rate)))
        object.__setattr__(
            self, "annual_rate", self.annual_rate.quantize(_QUANTUM)
        )

    def discount_factor(self, business_days: int) -> Decimal:
        """Fator de desconto (1 + taxa)^(du/252). `business_days` deve vir
        de BusinessDate.business_days_until — nunca de diferença de datas
        corridas (ver domain/calendars)."""
        exponent = Decimal(business_days) / Decimal(252)
        base = Decimal(1) + self.annual_rate
        return decimal_power(base, exponent)
