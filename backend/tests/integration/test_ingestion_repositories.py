from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import select

from domain.bonds.bond_type import BondType
from infra.database.models import BondMarketQuoteModel, BondSeriesModel
from infra.database.repositories import upsert_bond_market_quote, upsert_bond_series
from infra.external_data.tesouro_direto import TesouroDiretoQuoteRow

from .conftest import requires_database

pytestmark = pytest.mark.integration


def _row(buy_pu: str = "955.84") -> TesouroDiretoQuoteRow:
    return TesouroDiretoQuoteRow(
        bond_type=BondType.LTN,
        maturity_date=date(2027, 1, 1),
        quote_date=date(2026, 8, 20),
        buy_rate_annual=Decimal("0.1348"),
        sell_rate_annual=Decimal("0.1360"),
        buy_pu=Decimal(buy_pu),
        sell_pu=Decimal("954.99"),
        base_pu=Decimal("954.99"),
    )


@requires_database
def test_upsert_bond_series_does_not_duplicate(db_session):
    upsert_bond_series(db_session, _row())
    upsert_bond_series(db_session, _row())
    db_session.commit()

    all_series = db_session.scalars(
        select(BondSeriesModel).where(BondSeriesModel.bond_type == BondType.LTN.value)
    ).all()
    assert len(all_series) == 1


@requires_database
def test_upsert_bond_market_quote_reruns_idempotently(db_session):
    series = upsert_bond_series(db_session, _row())
    upsert_bond_market_quote(db_session, series.id, _row())
    upsert_bond_market_quote(db_session, series.id, _row())  # reexecução, mesmo dia
    db_session.commit()

    quotes = db_session.scalars(
        select(BondMarketQuoteModel).where(BondMarketQuoteModel.bond_series_id == series.id)
    ).all()
    assert len(quotes) == 1
    assert quotes[0].buy_pu == Decimal("955.840000")


@requires_database
def test_upsert_bond_market_quote_updates_value_on_conflict(db_session):
    series = upsert_bond_series(db_session, _row())
    upsert_bond_market_quote(db_session, series.id, _row(buy_pu="955.84"))
    upsert_bond_market_quote(db_session, series.id, _row(buy_pu="960.00"))  # dado revisado
    db_session.commit()

    quotes = db_session.scalars(
        select(BondMarketQuoteModel).where(BondMarketQuoteModel.bond_series_id == series.id)
    ).all()
    assert len(quotes) == 1
    assert quotes[0].buy_pu == Decimal("960.000000")
