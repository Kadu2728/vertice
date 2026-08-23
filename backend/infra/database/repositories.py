"""Upsert idempotente por chave natural — nunca INSERT cego (docs/00-discovery.md
§8: reexecutar a ingestão não duplica nem diverge)."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from infra.database.models import BondMarketQuoteModel, BondSeriesModel, IndexSeriesPointModel
from infra.external_data.bcb_sgs import IndexSeriesPointRow
from infra.external_data.tesouro_direto import TesouroDiretoQuoteRow


def upsert_bond_series(session: Session, row: TesouroDiretoQuoteRow) -> BondSeriesModel:
    """Chave natural: (bond_type, maturity_date). Cria se não existir,
    reaproveita se existir — nunca duplica a mesma série."""
    existing = session.scalar(
        select(BondSeriesModel).where(
            BondSeriesModel.bond_type == row.bond_type.value,
            BondSeriesModel.maturity_date == row.maturity_date,
        )
    )
    if existing is not None:
        return existing
    series = BondSeriesModel(bond_type=row.bond_type.value, maturity_date=row.maturity_date)
    session.add(series)
    session.flush()
    return series


def upsert_bond_market_quote(
    session: Session, bond_series_id: uuid.UUID, row: TesouroDiretoQuoteRow
) -> None:
    """Chave natural: (bond_series_id, quote_date)."""
    stmt = insert(BondMarketQuoteModel).values(
        bond_series_id=bond_series_id,
        quote_date=row.quote_date,
        buy_rate_annual=row.buy_rate_annual,
        sell_rate_annual=row.sell_rate_annual,
        buy_pu=row.buy_pu,
        sell_pu=row.sell_pu,
        base_pu=row.base_pu,
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=["bond_series_id", "quote_date"],
        set_={
            "buy_rate_annual": stmt.excluded.buy_rate_annual,
            "sell_rate_annual": stmt.excluded.sell_rate_annual,
            "buy_pu": stmt.excluded.buy_pu,
            "sell_pu": stmt.excluded.sell_pu,
            "base_pu": stmt.excluded.base_pu,
        },
    )
    session.execute(stmt)


def upsert_index_series_point(session: Session, row: IndexSeriesPointRow) -> None:
    """Chave natural: (indexer, reference_date)."""
    stmt = insert(IndexSeriesPointModel).values(
        indexer=row.indexer,
        unit_period=row.unit_period,
        reference_date=row.reference_date,
        value=row.value,
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=["indexer", "reference_date"],
        set_={"value": stmt.excluded.value, "unit_period": stmt.excluded.unit_period},
    )
    session.execute(stmt)
