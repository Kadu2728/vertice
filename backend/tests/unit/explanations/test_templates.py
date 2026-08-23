from decimal import Decimal

from application.explanations.payload import ExplanationPayload
from application.explanations.templates import render_fallback


def _payload(**overrides) -> ExplanationPayload:
    base = dict(
        bond_type="LTN",
        purchase_date="2025-01-02",
        reference_date="2026-08-21",
        days_held=596,
        amount_invested=Decimal("1000.00"),
        gross_value_today=Decimal("1311.68"),
        net_value_today=Decimal("1252.85"),
        tax_ir=Decimal("54.54"),
        tax_iof=Decimal("0.00"),
        custody_fee=Decimal("4.28"),
        engine_version="2026.08.1",
    )
    base.update(overrides)
    return ExplanationPayload(**base)


def test_fallback_mentions_net_value():
    output = render_fallback(_payload())
    assert "R$ 1.252,85" in output.body


def test_fallback_says_subiu_when_gain():
    output = render_fallback(_payload())
    assert "subiu" in output.body


def test_fallback_says_caiu_when_loss():
    payload = _payload(net_value_today=Decimal("800.00"))
    output = render_fallback(payload)
    assert "caiu" in output.body


def test_fallback_omits_iof_when_zero():
    output = render_fallback(_payload(tax_iof=Decimal("0.00")))
    assert "IOF" not in output.body


def test_fallback_includes_iof_when_nonzero():
    output = render_fallback(_payload(tax_iof=Decimal("15.00")))
    assert "IOF" in output.body


def test_fallback_flags_itself_as_automatic():
    output = render_fallback(_payload())
    assert output.warnings
