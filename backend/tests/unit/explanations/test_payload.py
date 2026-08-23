from datetime import date
from decimal import Decimal
from uuid import UUID

from application.explanations.payload import build_payload, format_brl, payload_to_prompt_context
from application.simulations.service import SimulationResult
from domain.bonds.bond_type import BondType
from domain.taxation.net_proceeds import TaxBreakdown


def _simulation() -> SimulationResult:
    return SimulationResult(
        bond_series_id=UUID("11111111-1111-1111-1111-111111111111"),
        bond_type=BondType.LTN,
        purchase_date=date(2025, 1, 2),
        reference_date=date(2026, 8, 21),
        amount_invested=Decimal("1000"),
        quantity=Decimal("1.788788244844963"),
        pu_purchase=Decimal("559.037663"),
        pu_reference=Decimal("733.277405"),
        gross_value_today=Decimal("1311.678002274419210284942823"),
        days_held=596,
        taxes=TaxBreakdown(
            gross_gain=Decimal("311.678002274419210284942823"),
            iof_amount=Decimal("0"),
            ir_amount=Decimal("54.54365039802336179986499402"),
            net_gain=Decimal("257.1343518763958484850778290"),
        ),
        custody_fee_amount=Decimal("4.283616927975637530574388616"),
        net_value_today=Decimal("1252.850734948420210954503440"),
    )


def test_build_payload_rounds_to_cents():
    payload = build_payload(_simulation())
    assert payload.net_value_today == Decimal("1252.85")
    assert payload.tax_ir == Decimal("54.54")
    assert payload.custody_fee == Decimal("4.28")


def test_format_brl_positive():
    assert format_brl(Decimal("1252.85")) == "R$ 1.252,85"


def test_format_brl_negative():
    assert format_brl(Decimal("-54.54")) == "R$ -54,54"


def test_format_brl_zero():
    assert format_brl(Decimal("0.00")) == "R$ 0,00"


def test_prompt_context_contains_all_key_fields():
    payload = build_payload(_simulation())
    context = payload_to_prompt_context(payload)
    assert "LTN" in context
    assert "R$ 1.252,85" in context
    assert "596" in context
    assert payload.engine_version in context


def test_currency_fields_list_length():
    payload = build_payload(_simulation())
    assert len(payload.currency_fields()) == 6
