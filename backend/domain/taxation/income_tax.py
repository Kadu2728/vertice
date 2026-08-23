"""IR regressivo sobre renda fixa — Lei 11.033/2004, art. 1º.

Tabela estável desde 2005, sem alteração legislativa conhecida. Ainda assim,
tratada como dado versionável (não constante espalhada): se um dia mudar,
a mudança entra aqui e só aqui — nenhuma outra parte do domínio conhece
esses percentuais diretamente.
"""

from __future__ import annotations

from decimal import Decimal

# (dias_corridos_min, dias_corridos_max_inclusive_ou_None, alíquota)
_IR_BRACKETS: tuple[tuple[int, int | None, Decimal], ...] = (
    (0, 180, Decimal("0.225")),
    (181, 360, Decimal("0.20")),
    (361, 720, Decimal("0.175")),
    (721, None, Decimal("0.15")),
)


def ir_rate_for_holding_period(days_held: int) -> Decimal:
    """Alíquota de IR aplicável dado o prazo de permanência em dias
    corridos (a lei conta em dias corridos, não úteis — diferente do
    cálculo de PU, que é em du/252)."""
    if days_held < 0:
        raise ValueError("days_held não pode ser negativo")
    for min_days, max_days, rate in _IR_BRACKETS:
        if max_days is None or days_held <= max_days:
            if days_held >= min_days:
                return rate
    raise AssertionError("tabela de IR não cobre o prazo informado — bug na tabela")
