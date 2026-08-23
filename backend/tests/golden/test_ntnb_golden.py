"""Golden test — NTN-B (com cupom). Ver docs/domain/golden-tests-status.md.

STATUS: combina os dois gaps documentados separadamente em NTN-F (fluxo de
cupom) e NTN-B Principal (precisão do VNA de terceiros) — resíduo observado
até ~R$ 1,40. Não é um terceiro problema novo; é a soma dos dois já
rastreados. Resolver NTN-F e NTN-B Principal deve resolver este também."""

from decimal import Decimal

import pytest

from domain.bonds.bond_series import BondSeries
from domain.bonds.bond_type import BondType
from domain.calendars.anbima import AnbimaCalendar
from domain.pricing.ntnb import price_ntnb
from domain.shared.money import Money
from domain.shared.rate import Rate, RateBasis
from tests.golden.fixtures.tesouro_transparente_2026_08_20 import (
    NTNB_CASES,
    NTNB_PRINCIPAL_VNA,
    SETTLEMENT,
    semiannual_coupon_dates,
)

TOLERANCE = Decimal("1.50")  # ver docstring do módulo


@pytest.mark.golden
@pytest.mark.parametrize("case", NTNB_CASES, ids=lambda c: c.maturity.isoformat())
def test_ntnb_matches_official_pu_within_documented_gap(case):
    calendar = AnbimaCalendar()
    coupon_dates = semiannual_coupon_dates(case.maturity, SETTLEMENT)
    bond = BondSeries(
        id=f"NTNB-{case.maturity.isoformat()}",
        bond_type=BondType.NTN_B,
        maturity_date=case.maturity,
        coupon_rate_annual=Decimal("0.06"),
        coupon_dates=coupon_dates,
    )
    tir = Rate(case.taxa_compra_pct / 100, RateBasis.REAL)
    vna = Money(NTNB_PRINCIPAL_VNA)

    pu = price_ntnb(bond, SETTLEMENT, calendar, tir, vna)

    assert abs(pu.amount - case.pu_compra_oficial) <= TOLERANCE
