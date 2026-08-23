"""IOF regressivo sobre resgate em renda fixa antes de 30 dias corridos —
Decreto 6.306/2007, Anexo I.

ATENÇÃO — dado pendente de validação (ver docs/domain/tributacao-fontes.md
e ambiguidade A4 do discovery): a tabela abaixo reflete os percentuais
publicamente consolidados para o IOF regressivo padrão de renda fixa, mas
não foi conferida linha a linha contra o texto oficial do Anexo I nesta
etapa. Não usar como golden reference até essa conferência acontecer —
qualquer golden test de IOF deve citar a fonte oficial no commit que o
introduz, não só importar esta tabela.
"""

from __future__ import annotations

from decimal import Decimal

# dia corrido (1 a 29) -> percentual do ganho tributado pelo IOF
_IOF_TABLE: dict[int, Decimal] = {
    1: Decimal("0.96"), 2: Decimal("0.93"), 3: Decimal("0.90"),
    4: Decimal("0.86"), 5: Decimal("0.83"), 6: Decimal("0.80"),
    7: Decimal("0.76"), 8: Decimal("0.73"), 9: Decimal("0.70"),
    10: Decimal("0.66"), 11: Decimal("0.63"), 12: Decimal("0.60"),
    13: Decimal("0.56"), 14: Decimal("0.53"), 15: Decimal("0.50"),
    16: Decimal("0.46"), 17: Decimal("0.43"), 18: Decimal("0.40"),
    19: Decimal("0.36"), 20: Decimal("0.33"), 21: Decimal("0.30"),
    22: Decimal("0.26"), 23: Decimal("0.23"), 24: Decimal("0.20"),
    25: Decimal("0.16"), 26: Decimal("0.13"), 27: Decimal("0.10"),
    28: Decimal("0.06"), 29: Decimal("0.03"),
}


def iof_rate_for_holding_period(days_held: int) -> Decimal:
    """Percentual do ganho consumido por IOF. Zero a partir de 30 dias
    corridos de permanência."""
    if days_held < 0:
        raise ValueError("days_held não pode ser negativo")
    if days_held == 0:
        return _IOF_TABLE[1]
    if days_held >= 30:
        return Decimal("0")
    return _IOF_TABLE[days_held]
