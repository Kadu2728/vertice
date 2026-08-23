"""Taxa de custódia B3 — 0,20% a.a., isenção do Tesouro Selic até R$ 10.000
em estoque por CPF. Fonte: docs/domain/tributacao-fontes.md (B3 "Tarifas de
Tesouro Direto", modelo vigente desde 31/12/2024).

Cobrança real: provisionada diariamente pro rata a partir de D+1 da
liquidação, efetivada só em venda/vencimento/cupom. Esta função calcula o
valor acumulado a provisionar até uma data de referência — o evento de
cobrança em si é responsabilidade de quem orquestra a simulação."""

from __future__ import annotations

from decimal import Decimal

from domain.bonds.bond_type import BondType

ANNUAL_RATE = Decimal("0.0020")
SELIC_EXEMPT_THRESHOLD = Decimal("10000")
_DAYS_IN_YEAR = Decimal(365)


def custody_fee(bond_type: BondType, reference_value: Decimal, days_accrued: int) -> Decimal:
    """`reference_value`: valor sobre o qual a taxa incide (convenção:
    valor bruto atual da posição). `days_accrued`: dias corridos desde D+1
    da liquidação até a data de referência."""
    if days_accrued <= 0:
        return Decimal("0")
    taxable_base = reference_value
    if bond_type == BondType.LFT:
        taxable_base = max(reference_value - SELIC_EXEMPT_THRESHOLD, Decimal("0"))
    return taxable_base * ANNUAL_RATE * Decimal(days_accrued) / _DAYS_IN_YEAR
