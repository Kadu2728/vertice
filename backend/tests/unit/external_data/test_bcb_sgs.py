from datetime import date
from decimal import Decimal

import pytest

from infra.external_data.bcb_sgs import UnexpectedSgsResponseShape, parse_series

# amostras reais, capturadas da API do BCB em 2026-08-21
SELIC_SAMPLE = (
    '[{"data":"17/08/2026","valor":"0.051660"},{"data":"18/08/2026","valor":"0.051660"},'
    '{"data":"19/08/2026","valor":"0.051660"},{"data":"20/08/2026","valor":"0.051660"},'
    '{"data":"21/08/2026","valor":"0.051660"}]'
)

IPCA_SAMPLE = (
    '[{"data":"01/03/2026","valor":"0.88"},{"data":"01/04/2026","valor":"0.67"},'
    '{"data":"01/05/2026","valor":"0.58"},{"data":"01/06/2026","valor":"0.16"},'
    '{"data":"01/07/2026","valor":"0.07"}]'
)


def test_parses_selic_daily_series():
    rows = parse_series(SELIC_SAMPLE, indexer="SELIC", unit_period="daily")
    assert len(rows) == 5
    assert rows[0].reference_date == date(2026, 8, 17)
    assert rows[0].value == Decimal("0.051660")
    assert all(r.indexer == "SELIC" and r.unit_period == "daily" for r in rows)


def test_parses_ipca_monthly_series():
    rows = parse_series(IPCA_SAMPLE, indexer="IPCA", unit_period="monthly")
    assert len(rows) == 5
    assert rows[-1].reference_date == date(2026, 7, 1)
    assert rows[-1].value == Decimal("0.07")


def test_rejects_non_json():
    with pytest.raises(UnexpectedSgsResponseShape):
        parse_series("<html>não é json</html>", indexer="SELIC", unit_period="daily")


def test_rejects_non_list_payload():
    with pytest.raises(UnexpectedSgsResponseShape):
        parse_series('{"erro": "série não encontrada"}', indexer="SELIC", unit_period="daily")


def test_rejects_point_missing_expected_fields():
    with pytest.raises(UnexpectedSgsResponseShape):
        parse_series('[{"date":"17/08/2026","value":"0.05"}]', indexer="SELIC", unit_period="daily")
