"""Template estático — usado sempre que a IA falha, diverge do payload ou
não está disponível (docs/00-discovery.md §25: a IA é aditiva, nunca
dependência crítica). Determinístico, não toca rede."""

from __future__ import annotations

from application.explanations.payload import ExplanationPayload, format_brl
from application.explanations.schemas import ExplanationOutput


def render_fallback(payload: ExplanationPayload) -> ExplanationOutput:
    direction = "subiu" if payload.net_value_today >= payload.amount_invested else "caiu"
    diff = abs(payload.net_value_today - payload.amount_invested)

    deductions = [f"{format_brl(payload.tax_ir)} de IR"]
    if payload.tax_iof > 0:
        deductions.append(f"{format_brl(payload.tax_iof)} de IOF")
    deductions.append(f"{format_brl(payload.custody_fee)} de custódia")

    body = (
        f"Você investiu {format_brl(payload.amount_invested)} em {payload.purchase_date} "
        f"e hoje ({payload.reference_date}) esse investimento vale "
        f"{format_brl(payload.net_value_today)} líquido — o valor {direction} "
        f"{format_brl(diff)} desde a compra, já descontados {', '.join(deductions)}."
    )

    return ExplanationOutput(
        title="Resultado da simulação",
        body=body,
        warnings=["Explicação gerada automaticamente a partir do resultado calculado, sem IA."],
    )
