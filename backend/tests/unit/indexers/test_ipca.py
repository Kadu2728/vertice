from decimal import Decimal

from domain.indexers.ipca import vna_month_closed, vna_pro_rata_official, vna_pro_rata_projected
from domain.shared.money import Money


def test_vna_month_closed_equal_indices_returns_base_value():
    vna = vna_month_closed(ipca_index_prev_month=Decimal("1000"), ipca_index_base_month=Decimal("1000"))
    assert vna.amount == Decimal("1000.000000")


def test_vna_month_closed_scales_with_index_ratio():
    vna = vna_month_closed(ipca_index_prev_month=Decimal("1100"), ipca_index_base_month=Decimal("1000"))
    assert vna.amount == Decimal("1100.000000")


def test_vna_pro_rata_official_no_elapsed_days_keeps_previous_vna():
    vna_prev = Money(Decimal("1234.567891"))
    vna = vna_pro_rata_official(
        vna_prev_month=vna_prev,
        ipca_index_t1=Decimal("1050"),
        ipca_index_t2=Decimal("1000"),
        business_days_elapsed=0,
        business_days_in_reference_window=21,
    )
    assert vna.amount == vna_prev.amount


def test_vna_pro_rata_projected_no_elapsed_days_keeps_previous_vna():
    vna_prev = Money(Decimal("1234.567891"))
    vna = vna_pro_rata_projected(
        vna_prev_month=vna_prev,
        ipca_projection=Decimal("0.004"),
        business_days_elapsed=0,
        business_days_in_reference_window=21,
    )
    assert vna.amount == vna_prev.amount


def test_vna_pro_rata_projected_full_window_applies_full_projection():
    vna_prev = Money(Decimal("1000.000000"))
    vna = vna_pro_rata_projected(
        vna_prev_month=vna_prev,
        ipca_projection=Decimal("0.01"),
        business_days_elapsed=21,
        business_days_in_reference_window=21,
    )
    assert vna.amount == Decimal("1010.000000")
