from decimal import Decimal

import pytest

from domain.taxation.net_proceeds import calculate_taxes


def test_no_iof_after_30_days():
    result = calculate_taxes(Decimal("100"), days_held=31)
    assert result.iof_amount == Decimal("0")


def test_iof_and_ir_both_apply_within_30_days():
    result = calculate_taxes(Decimal("100"), days_held=1)
    # dia 1: IOF = 96% do ganho; IR (22,5%, prazo <=180d) incide sobre o restante
    assert result.iof_amount == Decimal("96")
    assert result.ir_amount == Decimal("0.9")  # 22,5% de (100-96)=4
    assert result.net_gain == Decimal("3.1")


def test_ir_calculated_on_gain_net_of_iof_not_on_gross():
    result = calculate_taxes(Decimal("100"), days_held=1)
    naive_ir_on_gross = Decimal("100") * Decimal("0.225")
    assert result.ir_amount < naive_ir_on_gross


def test_ir_only_after_30_days_uses_bracket_for_holding_period():
    result = calculate_taxes(Decimal("1000"), days_held=200)  # faixa 20%
    assert result.iof_amount == Decimal("0")
    assert result.ir_amount == Decimal("200.00")
    assert result.net_gain == Decimal("800.00")


def test_loss_is_never_taxed():
    result = calculate_taxes(Decimal("-50"), days_held=100)
    assert result.iof_amount == Decimal("0")
    assert result.ir_amount == Decimal("0")
    assert result.net_gain == Decimal("0")
    assert result.gross_gain == Decimal("-50")  # preservado para exibição, não zerado


def test_rejects_negative_days():
    with pytest.raises(ValueError):
        calculate_taxes(Decimal("100"), days_held=-1)
