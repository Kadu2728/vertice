from datetime import date
from decimal import Decimal

import pytest

from domain.bonds.bond_type import BondType
from infra.external_data.tesouro_direto import (
    IngestionValidationError,
    TesouroDiretoQuoteRow,
    filter_by_quote_date,
    latest_quote_date,
    validate_daily_batch,
)


def _row(bond_type: BondType, quote_date: date) -> TesouroDiretoQuoteRow:
    return TesouroDiretoQuoteRow(
        bond_type=bond_type,
        maturity_date=date(2030, 1, 1),
        quote_date=quote_date,
        buy_rate_annual=Decimal("0.10"),
        sell_rate_annual=Decimal("0.11"),
        buy_pu=Decimal("900"),
        sell_pu=Decimal("895"),
        base_pu=Decimal("895"),
    )


def _full_coverage_batch(quote_date: date, extra: int = 20) -> list[TesouroDiretoQuoteRow]:
    rows = [_row(bond_type, quote_date) for bond_type in BondType]
    rows += [_row(BondType.LTN, quote_date) for _ in range(extra)]
    return rows


def test_latest_quote_date_picks_max():
    rows = [_row(BondType.LTN, date(2026, 8, 18)), _row(BondType.LTN, date(2026, 8, 20))]
    assert latest_quote_date(rows) == date(2026, 8, 20)


def test_latest_quote_date_raises_on_empty():
    with pytest.raises(IngestionValidationError):
        latest_quote_date([])


def test_filter_by_quote_date_keeps_only_matching_rows():
    rows = [_row(BondType.LTN, date(2026, 8, 18)), _row(BondType.LTN, date(2026, 8, 20))]
    filtered = filter_by_quote_date(rows, date(2026, 8, 20))
    assert len(filtered) == 1
    assert filtered[0].quote_date == date(2026, 8, 20)


def test_validate_daily_batch_accepts_full_coverage():
    validate_daily_batch(_full_coverage_batch(date(2026, 8, 20)))  # não deve levantar


def test_validate_daily_batch_rejects_too_few_rows():
    with pytest.raises(IngestionValidationError):
        validate_daily_batch([_row(BondType.LTN, date(2026, 8, 20))])


def test_validate_daily_batch_rejects_missing_bond_type():
    rows = _full_coverage_batch(date(2026, 8, 20))
    rows = [r for r in rows if r.bond_type != BondType.LFT]
    with pytest.raises(IngestionValidationError):
        validate_daily_batch(rows)
