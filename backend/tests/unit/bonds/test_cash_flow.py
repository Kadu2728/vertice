from datetime import date
from decimal import Decimal

from domain.bonds.bond_series import BondSeries
from domain.bonds.bond_type import BondType
from domain.bonds.cash_flow import CashFlowKind, build_cash_flow_schedule
from domain.calendars.anbima import AnbimaCalendar


def test_ltn_has_single_principal_flow():
    bond = BondSeries(id="LTN-2027", bond_type=BondType.LTN, maturity_date=date(2027, 1, 4))
    calendar = AnbimaCalendar()
    flows = build_cash_flow_schedule(bond, date(2026, 1, 2), calendar)
    assert len(flows) == 1
    assert flows[0].kind == CashFlowKind.PRINCIPAL
    assert flows[0].face_value_fraction == Decimal(1)


def test_ntnf_has_coupon_flows_plus_final_principal():
    bond = BondSeries(
        id="NTNF-2027",
        bond_type=BondType.NTN_F,
        maturity_date=date(2027, 1, 4),
        coupon_rate_annual=Decimal("0.10"),
        coupon_dates=(date(2026, 7, 1), date(2027, 1, 4)),
    )
    calendar = AnbimaCalendar()
    semiannual_rate = Decimal("0.04881")
    flows = build_cash_flow_schedule(bond, date(2026, 1, 2), calendar, semiannual_rate)
    # 2 fluxos de cupom (jul/2026 e jan/2027) + 1 fluxo de principal separado no vencimento
    assert len(flows) == 3
    assert [f.kind for f in flows] == [
        CashFlowKind.COUPON,
        CashFlowKind.COUPON,
        CashFlowKind.PRINCIPAL,
    ]
    assert flows[0].face_value_fraction == semiannual_rate
    assert flows[-1].face_value_fraction == Decimal(1)
    assert flows[-1].business_days_to_payment == flows[1].business_days_to_payment


def test_past_coupon_dates_are_excluded():
    bond = BondSeries(
        id="NTNF-2027",
        bond_type=BondType.NTN_F,
        maturity_date=date(2027, 1, 4),
        coupon_rate_annual=Decimal("0.10"),
        coupon_dates=(date(2025, 7, 1), date(2026, 1, 2), date(2026, 7, 1), date(2027, 1, 4)),
    )
    calendar = AnbimaCalendar()
    flows = build_cash_flow_schedule(bond, date(2026, 1, 2), calendar, Decimal("0.04881"))
    # datas em ou antes da liquidação (2025-07-01, 2026-01-02) não entram
    assert len(flows) == 3
