from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

# NUMERIC(18,6) na borda de persistência — ver ADR-004. A quantização aqui é a
# precisão de cálculo interna, não a de apresentação.
_INTERNAL_QUANTUM = Decimal("0.000001")
_DISPLAY_QUANTUM = Decimal("0.01")


@dataclass(frozen=True, slots=True)
class Money:
    """Valor monetário em BRL. Nunca aceita float — só Decimal ou algo
    exato o suficiente para virar Decimal sem passar por binário (str, int).
    """

    amount: Decimal
    currency: str = "BRL"

    def __post_init__(self) -> None:
        if isinstance(self.amount, float):
            raise TypeError(
                "Money não aceita float — passe Decimal ou str para preservar precisão"
            )
        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, "amount", Decimal(str(self.amount)))
        object.__setattr__(
            self, "amount", self.amount.quantize(_INTERNAL_QUANTUM, rounding=ROUND_HALF_UP)
        )

    def _check_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise ValueError(f"não é possível operar {self.currency} com {other.currency}")

    def __add__(self, other: "Money") -> "Money":
        self._check_currency(other)
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        self._check_currency(other)
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, factor: Decimal) -> "Money":
        if isinstance(factor, float):
            raise TypeError("multiplique Money apenas por Decimal")
        return Money(self.amount * Decimal(factor), self.currency)

    def __neg__(self) -> "Money":
        return Money(-self.amount, self.currency)

    def __lt__(self, other: "Money") -> bool:
        self._check_currency(other)
        return self.amount < other.amount

    def __le__(self, other: "Money") -> bool:
        self._check_currency(other)
        return self.amount <= other.amount

    def is_zero(self) -> bool:
        return self.amount == 0

    def to_display(self) -> Decimal:
        """Arredondamento de apresentação (2 casas). Nunca usar em cálculo
        intermediário — só na borda de serialização para o usuário."""
        return self.amount.quantize(_DISPLAY_QUANTUM, rounding=ROUND_HALF_UP)

    @classmethod
    def zero(cls, currency: str = "BRL") -> "Money":
        return cls(Decimal("0"), currency)
