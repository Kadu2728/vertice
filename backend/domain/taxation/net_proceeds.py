"""Composição de IOF + IR sobre o resgate.

ORDEM: IOF incide primeiro sobre o rendimento bruto; IR incide depois sobre
o rendimento já líquido de IOF. Nem o Decreto 6.306/2007 nem a Lei
11.033/2004, lidos isoladamente, definem essa ordem — ela vem de prática de
mercado consolidada (documentada por múltiplas corretoras/bancos), não de
um único texto legal primário. Sinalizado aqui como premissa a validar
juridicamente antes de qualquer afirmação definitiva ao usuário (ver §38
do prompt do projeto sobre fronteira regulatória)."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from domain.taxation.income_tax import ir_rate_for_holding_period
from domain.taxation.iof import iof_rate_for_holding_period

_IOF_APPLIES_BELOW_DAYS = 30


@dataclass(frozen=True, slots=True)
class TaxBreakdown:
    gross_gain: Decimal
    iof_amount: Decimal
    ir_amount: Decimal
    net_gain: Decimal


def calculate_taxes(gross_gain: Decimal, days_held: int) -> TaxBreakdown:
    """Tributo não incide sobre prejuízo — se `gross_gain` for negativo,
    IOF e IR ficam zerados e o prejuízo passa integralmente."""
    if days_held < 0:
        raise ValueError("days_held não pode ser negativo")

    gain = max(gross_gain, Decimal("0"))
    iof_amount = Decimal("0")
    if days_held < _IOF_APPLIES_BELOW_DAYS:
        iof_amount = gain * iof_rate_for_holding_period(days_held)

    taxable_after_iof = gain - iof_amount
    ir_amount = taxable_after_iof * ir_rate_for_holding_period(days_held)
    net_gain = gain - iof_amount - ir_amount

    return TaxBreakdown(
        gross_gain=gross_gain, iof_amount=iof_amount, ir_amount=ir_amount, net_gain=net_gain
    )
