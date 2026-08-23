from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from application.simulations.ports import BondSeriesRecord, MarketQuoteRecord
from application.simulations.service import (
    BondSeriesNotFound,
    BondTypeNotYetSupported,
    QuoteNotFound,
    calculate_scenario,
    calculate_simulation,
)
from domain.bonds.bond_type import BondType
from domain.calendars.anbima import AnbimaCalendar
from domain.pricing.ltn import price_ltn
from domain.shared.rate import Rate, RateBasis


@dataclass
class FakeCatalog:
    """Catálogo em memória — o mesmo Protocol que a implementação real
    (SQLAlchemy) satisfaz, usado aqui para não depender de Postgres."""

    series: dict[UUID, BondSeriesRecord]
    quotes: dict[tuple[UUID, date], MarketQuoteRecord]

    def get_bond_series(self, bond_series_id: UUID) -> BondSeriesRecord | None:
        return self.series.get(bond_series_id)

    def get_quote(self, bond_series_id: UUID, quote_date: date) -> MarketQuoteRecord | None:
        return self.quotes.get((bond_series_id, quote_date))

    def get_vna(self, bond_type: BondType, reference_date: date):
        return None


def _ltn_catalog(
    rate_purchase: str,
    rate_reference: str,
    purchase_date: date = date(2026, 1, 2),
    reference_date: date = date(2027, 1, 4),
) -> tuple[FakeCatalog, UUID]:
    bond_id = uuid4()
    maturity = date(2028, 1, 1)
    catalog = FakeCatalog(
        series={
            bond_id: BondSeriesRecord(
                id=bond_id,
                bond_type=BondType.LTN,
                maturity_date=maturity,
                coupon_rate_annual=None,
                coupon_dates=(),
            )
        },
        quotes={
            (bond_id, purchase_date): MarketQuoteRecord(purchase_date, Decimal(rate_purchase)),
            (bond_id, reference_date): MarketQuoteRecord(reference_date, Decimal(rate_reference)),
        },
    )
    return catalog, bond_id


def test_ltn_simulation_matches_pricing_engine_directly():
    catalog, bond_id = _ltn_catalog("0.10", "0.10")
    purchase_date = date(2026, 1, 2)
    reference_date = date(2027, 1, 4)
    maturity = date(2028, 1, 1)
    calendar = AnbimaCalendar()

    result = calculate_simulation(catalog, bond_id, purchase_date, reference_date, Decimal("1000"))

    du_purchase = calendar.business_days_between(purchase_date, maturity)
    du_reference = calendar.business_days_between(reference_date, maturity)
    expected_pu_purchase = price_ltn(Rate(Decimal("0.10"), RateBasis.NOMINAL), du_purchase)
    expected_pu_reference = price_ltn(Rate(Decimal("0.10"), RateBasis.NOMINAL), du_reference)

    assert result.pu_purchase == expected_pu_purchase.amount
    assert result.pu_reference == expected_pu_reference.amount


def test_ltn_simulation_taxes_the_gain_when_rate_unchanged():
    # taxa igual em ambas as pontas: com o tempo passando, PU sobe rumo ao
    # valor de face -> há ganho real a tributar.
    catalog, bond_id = _ltn_catalog("0.10", "0.10")
    result = calculate_simulation(
        catalog, bond_id, date(2026, 1, 2), date(2027, 1, 4), Decimal("1000")
    )
    assert result.gross_value_today > result.amount_invested
    assert result.taxes.gross_gain > 0
    assert result.taxes.ir_amount > 0
    assert result.net_value_today < result.gross_value_today  # impostos + custódia reduzem


def test_ltn_simulation_no_tax_on_loss():
    # janela curta (poucos dias) para o efeito "pull-to-par" não mascarar o
    # salto de taxa: 10% -> 30% em 7 dias derruba o preço com folga.
    purchase_date, reference_date = date(2026, 1, 2), date(2026, 1, 9)
    catalog, bond_id = _ltn_catalog("0.10", "0.30", purchase_date, reference_date)
    result = calculate_simulation(catalog, bond_id, purchase_date, reference_date, Decimal("1000"))
    assert result.gross_value_today < result.amount_invested
    assert result.taxes.ir_amount == Decimal("0")
    assert result.taxes.iof_amount == Decimal("0")


def test_bond_series_not_found_raises():
    catalog = FakeCatalog(series={}, quotes={})
    with pytest.raises(BondSeriesNotFound):
        calculate_simulation(catalog, uuid4(), date(2026, 1, 2), date(2027, 1, 4), Decimal("1000"))


def test_missing_quote_raises():
    bond_id = uuid4()
    catalog = FakeCatalog(
        series={
            bond_id: BondSeriesRecord(
                id=bond_id,
                bond_type=BondType.LTN,
                maturity_date=date(2028, 1, 1),
                coupon_rate_annual=None,
                coupon_dates=(),
            )
        },
        quotes={},
    )
    with pytest.raises(QuoteNotFound):
        calculate_simulation(catalog, bond_id, date(2026, 1, 2), date(2027, 1, 4), Decimal("1000"))


def test_unsupported_bond_type_raises():
    bond_id = uuid4()
    catalog = FakeCatalog(
        series={
            bond_id: BondSeriesRecord(
                id=bond_id,
                bond_type=BondType.LFT,
                maturity_date=date(2028, 1, 1),
                coupon_rate_annual=None,
                coupon_dates=(),
            )
        },
        quotes={},
    )
    with pytest.raises(BondTypeNotYetSupported):
        calculate_simulation(catalog, bond_id, date(2026, 1, 2), date(2027, 1, 4), Decimal("1000"))


def test_scenario_positive_shock_lowers_price():
    purchase_date, reference_date = date(2026, 1, 2), date(2027, 1, 4)
    catalog, bond_id = _ltn_catalog("0.10", "0.10", purchase_date, reference_date)

    base = calculate_simulation(catalog, bond_id, purchase_date, reference_date, Decimal("1000"))
    shocked_up = calculate_scenario(
        catalog, bond_id, purchase_date, reference_date, Decimal("1000"), shock_bps=200
    )
    shocked_down = calculate_scenario(
        catalog, bond_id, purchase_date, reference_date, Decimal("1000"), shock_bps=-200
    )

    assert shocked_up.pu_reference < base.pu_reference < shocked_down.pu_reference


def test_scenario_zero_shock_matches_base_simulation():
    purchase_date, reference_date = date(2026, 1, 2), date(2027, 1, 4)
    catalog, bond_id = _ltn_catalog("0.10", "0.10", purchase_date, reference_date)

    base = calculate_simulation(catalog, bond_id, purchase_date, reference_date, Decimal("1000"))
    zero_shock = calculate_scenario(
        catalog, bond_id, purchase_date, reference_date, Decimal("1000"), shock_bps=0
    )
    assert zero_shock.pu_reference == base.pu_reference


def test_ntnf_simulation_runs_end_to_end():
    bond_id = uuid4()
    maturity = date(2029, 1, 1)
    purchase_date = date(2026, 1, 2)
    reference_date = date(2027, 1, 4)
    coupon_dates = (date(2026, 7, 1), date(2027, 1, 1), date(2027, 7, 1), date(2028, 1, 1), maturity)
    catalog = FakeCatalog(
        series={
            bond_id: BondSeriesRecord(
                id=bond_id,
                bond_type=BondType.NTN_F,
                maturity_date=maturity,
                coupon_rate_annual=Decimal("0.10"),
                coupon_dates=coupon_dates,
            )
        },
        quotes={
            (bond_id, purchase_date): MarketQuoteRecord(purchase_date, Decimal("0.11")),
            (bond_id, reference_date): MarketQuoteRecord(reference_date, Decimal("0.11")),
        },
    )
    result = calculate_simulation(catalog, bond_id, purchase_date, reference_date, Decimal("1000"))
    assert result.pu_purchase > 0
    assert result.quantity > 0
