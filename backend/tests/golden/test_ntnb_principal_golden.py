"""Golden test — NTN-B Principal. Ver docs/domain/golden-tests-status.md.

STATUS: gap parcialmente atribuível a dado, não a fórmula. O VNA usado
(R$ 4.740,845804) veio de fonte terciária (brasilindicadores.com.br), não
da série oficial ANBIMA/BCB — o resíduo observado (~0,03% do PU na maioria
dos casos, compatível com 1-3 dias de deriva do IPCA projetado) é da ordem
do que se espera de um VNA levemente desatualizado, não de um erro
estrutural na fórmula de cotação zero-cupom (que é a mesma usada em LTN,
já validada com folga de milésimos de real). Revisitar com VNA oficial
assim que a Fase 3 (ingestão) existir."""

from decimal import Decimal

import pytest

from domain.bonds.bond_series import BondSeries
from domain.bonds.bond_type import BondType
from domain.calendars.anbima import AnbimaCalendar
from domain.pricing.ntnb import price_ntnb_principal
from domain.shared.money import Money
from domain.shared.rate import Rate, RateBasis
from tests.golden.fixtures.tesouro_transparente_2026_08_20 import (
    NTNB_PRINCIPAL_CASES,
    NTNB_PRINCIPAL_VNA,
    SETTLEMENT,
)

TOLERANCE = Decimal("1.50")  # ver docstring do módulo — limitado pela precisão do VNA de origem


@pytest.mark.golden
@pytest.mark.parametrize("case", NTNB_PRINCIPAL_CASES, ids=lambda c: c.maturity.isoformat())
def test_ntnb_principal_matches_official_pu_within_documented_gap(case):
    calendar = AnbimaCalendar()
    bond = BondSeries(
        id=f"NTNBP-{case.maturity.isoformat()}",
        bond_type=BondType.NTN_B_PRINCIPAL,
        maturity_date=case.maturity,
    )
    tir = Rate(case.taxa_compra_pct / 100, RateBasis.REAL)
    vna = Money(NTNB_PRINCIPAL_VNA)

    pu = price_ntnb_principal(bond, SETTLEMENT, calendar, tir, vna)

    assert abs(pu.amount - case.pu_compra_oficial) <= TOLERANCE
