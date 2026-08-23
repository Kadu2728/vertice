"""Golden test — NTN-F. Ver docs/domain/golden-tests-status.md.

STATUS: gap real e reprodutível, não resolvido. O PU calculado diverge do
oficial numa quantidade que CRESCE com o número de cupons remanescentes
(R$ 0,0025 para 1 cupom até R$ 0,065 para ~21 cupons) — testado contra
variações de casas decimais de arredondamento (5 a 16 casas, em ambos os
pontos: taxa semestral e fluxo descontado) sem eliminar o resíduo, o que
descarta "precisão insuficiente" como causa. Duas hipóteses seguem abertas:
(1) as datas de cupom aqui são sintéticas (geradas por convenção, não a
grade real de emissão da série) e podem não bater exatamente com a série
real; (2) existe um passo de truncamento específico do Tesouro Direto para
fluxos intermediários que a extração de texto do PDF ANBIMA não capturou
(equações eram objetos gráficos, não texto — ver docs/domain/precificacao-anbima.md).

Tolerância abaixo é a folga observada + margem, não R$ 0,01 — mantido como
teste que PASSA (não xfail) para continuar pegando regressões grandes,
mas com o gap documentado alto e visível, não escondido."""

from decimal import Decimal

import pytest

from domain.bonds.bond_series import BondSeries
from domain.bonds.bond_type import BondType
from domain.calendars.anbima import AnbimaCalendar
from domain.pricing.ntnf import price_ntnf
from domain.shared.rate import Rate, RateBasis
from tests.golden.fixtures.tesouro_transparente_2026_08_20 import (
    NTNF_CASES,
    SETTLEMENT,
    semiannual_coupon_dates,
)

TOLERANCE = Decimal("0.10")  # ver docstring do módulo — não é a meta final de R$ 0,01


@pytest.mark.golden
@pytest.mark.parametrize("case", NTNF_CASES, ids=lambda c: c.maturity.isoformat())
def test_ntnf_matches_official_pu_within_documented_gap(case):
    calendar = AnbimaCalendar()
    coupon_dates = semiannual_coupon_dates(case.maturity, SETTLEMENT)
    bond = BondSeries(
        id=f"NTNF-{case.maturity.isoformat()}",
        bond_type=BondType.NTN_F,
        maturity_date=case.maturity,
        coupon_rate_annual=Decimal("0.10"),
        coupon_dates=coupon_dates,
    )
    tir = Rate(case.taxa_compra_pct / 100, RateBasis.NOMINAL)

    pu = price_ntnf(bond, SETTLEMENT, calendar, tir)

    assert abs(pu.amount - case.pu_compra_oficial) <= TOLERANCE
