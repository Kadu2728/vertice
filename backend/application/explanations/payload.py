"""Payload estruturado que sai do motor determinístico — o único contexto
numérico que a camada de IA enxerga. Ela nunca calcula nada, só recebe
esses números já prontos (ADR-003) e os usa para explicar em texto."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from application.simulations.service import SimulationResult

_CENTS = Decimal("0.01")


def _money(value: Decimal) -> Decimal:
    return value.quantize(_CENTS, rounding=ROUND_HALF_UP)


@dataclass(frozen=True, slots=True)
class ExplanationPayload:
    bond_type: str
    purchase_date: str
    reference_date: str
    days_held: int
    amount_invested: Decimal
    gross_value_today: Decimal
    net_value_today: Decimal
    tax_ir: Decimal
    tax_iof: Decimal
    custody_fee: Decimal
    engine_version: str

    def currency_fields(self) -> list[Decimal]:
        """Referência para o validador numérico conferir o que a IA
        escreveu — todo valor monetário do texto precisa bater com um
        destes."""
        return [
            self.amount_invested,
            self.gross_value_today,
            self.net_value_today,
            self.tax_ir,
            self.tax_iof,
            self.custody_fee,
        ]


def build_payload(simulation: SimulationResult) -> ExplanationPayload:
    return ExplanationPayload(
        bond_type=simulation.bond_type.value,
        purchase_date=simulation.purchase_date.isoformat(),
        reference_date=simulation.reference_date.isoformat(),
        days_held=simulation.days_held,
        amount_invested=_money(simulation.amount_invested),
        gross_value_today=_money(simulation.gross_value_today),
        net_value_today=_money(simulation.net_value_today),
        tax_ir=_money(simulation.taxes.ir_amount),
        tax_iof=_money(simulation.taxes.iof_amount),
        custody_fee=_money(simulation.custody_fee_amount),
        engine_version=simulation.calculation_engine_version,
    )


def format_brl(value: Decimal) -> str:
    text = f"{value:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
    return f"R$ {text}"


def payload_to_prompt_context(payload: ExplanationPayload) -> str:
    return (
        f"Título: {payload.bond_type}\n"
        f"Data da compra: {payload.purchase_date}\n"
        f"Data de referência: {payload.reference_date}\n"
        f"Dias em carteira: {payload.days_held}\n"
        f"Valor investido: {format_brl(payload.amount_invested)}\n"
        f"Valor bruto hoje: {format_brl(payload.gross_value_today)}\n"
        f"Valor líquido hoje: {format_brl(payload.net_value_today)}\n"
        f"IR retido: {format_brl(payload.tax_ir)}\n"
        f"IOF retido: {format_brl(payload.tax_iof)}\n"
        f"Custódia B3: {format_brl(payload.custody_fee)}\n"
        f"Versão do motor: {payload.engine_version}\n"
    )
