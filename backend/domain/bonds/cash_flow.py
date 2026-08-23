from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum

from domain.bonds.bond_series import BondSeries
from domain.bonds.bond_type import ZERO_COUPON_TYPES
from domain.calendars.anbima import AnbimaCalendar


class CashFlowKind(str, Enum):
    COUPON = "coupon"
    PRINCIPAL = "principal"


@dataclass(frozen=True, slots=True)
class CashFlow:
    """Um fluxo do título, em fração do valor de face (1 = 100% do VN, para
    LTN/NTN-F, ou 100% da base de cotação, para NTN-B/NTN-B Principal/LFT).
    `business_days_to_payment`: dias úteis entre a liquidação (inclusive) e
    o pagamento (exclusive) — convenção ANBIMA, ver docs/domain/precificacao-anbima.md."""

    business_days_to_payment: int
    kind: CashFlowKind
    face_value_fraction: Decimal


def build_cash_flow_schedule(
    bond: BondSeries,
    settlement: date,
    calendar: AnbimaCalendar,
    semiannual_coupon_rate: Decimal | None = None,
) -> list[CashFlow]:
    """Monta o cronograma de fluxos a partir da liquidação. Títulos com
    cupom recebem `semiannual_coupon_rate` já calculado e arredondado pela
    convenção do tipo (A-5 para NTN-F, A-6 para NTN-B — ver domain/pricing/coupons.py),
    porque a regra de arredondamento é responsabilidade de quem conhece o
    tipo de título, não desta função de montagem."""
    if bond.bond_type in ZERO_COUPON_TYPES:
        du = calendar.business_days_between(settlement, bond.maturity_date)
        return [CashFlow(du, CashFlowKind.PRINCIPAL, Decimal(1))]

    if semiannual_coupon_rate is None:
        raise ValueError(f"{bond.bond_type.value} exige semiannual_coupon_rate")

    flows: list[CashFlow] = []
    for payment_date in bond.coupon_dates:
        if payment_date <= settlement:
            continue
        du = calendar.business_days_between(settlement, payment_date)
        flows.append(CashFlow(du, CashFlowKind.COUPON, semiannual_coupon_rate))

    du_maturity = calendar.business_days_between(settlement, bond.maturity_date)
    flows.append(CashFlow(du_maturity, CashFlowKind.PRINCIPAL, Decimal(1)))
    return flows
