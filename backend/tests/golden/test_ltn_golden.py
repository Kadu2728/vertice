"""Golden test — LTN. Ver ADR-005 e docs/domain/golden-tests-status.md.

Este é o único conjunto totalmente validado até aqui: reproduz o PU oficial
publicado pelo Tesouro Transparente com diferença de poucos milésimos de
real, dentro da tolerância de R$ 0,01. Falha aqui é sinal real de regressão
no calendário ANBIMA ou na fórmula de LTN — não relaxar a tolerância."""

from decimal import Decimal

import pytest

from domain.calendars.anbima import AnbimaCalendar
from domain.pricing.ltn import price_ltn
from domain.shared.rate import Rate, RateBasis
from tests.golden.fixtures.tesouro_transparente_2026_08_20 import LTN_CASES, SETTLEMENT

TOLERANCE = Decimal("0.01")


@pytest.mark.golden
@pytest.mark.parametrize("case", LTN_CASES, ids=lambda c: c.maturity.isoformat())
def test_ltn_matches_official_pu(case):
    calendar = AnbimaCalendar()
    du = calendar.business_days_between(SETTLEMENT, case.maturity)
    rate = Rate(case.taxa_compra_pct / 100, RateBasis.NOMINAL)

    pu = price_ltn(rate, du)

    assert abs(pu.amount - case.pu_compra_oficial) <= TOLERANCE
