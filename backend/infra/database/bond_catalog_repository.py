"""Implementação real (Postgres) do BondCatalogPort. Nunca rodou contra um
banco de verdade neste ambiente (sem Postgres disponível — ver
docs/domain/fase-3-status.md); estruturalmente correta e com o mesmo
Protocol exercitado pelos testes de API com fake em memória, mas não
validada ao vivo.

Usa o lado "Compra" (Tesouro compra do investidor) das cotações — é o
único validado contra dado oficial nos golden tests (ver
docs/domain/golden-tests-status.md); o lado "Venda" tem uma divergência
sistemática ainda não compreendida."""

from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from application.simulations.ports import BondSeriesRecord, MarketQuoteRecord
from domain.bonds.bond_type import BondType
from domain.shared.money import Money
from infra.database.models import BondCouponDateModel, BondMarketQuoteModel, BondSeriesModel


class SqlAlchemyBondCatalog:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_bond_series(self) -> list[BondSeriesRecord]:
        rows = self._session.scalars(
            select(BondSeriesModel).order_by(BondSeriesModel.bond_type, BondSeriesModel.maturity_date)
        ).all()
        return [self._to_record(row) for row in rows]

    def get_bond_series(self, bond_series_id: UUID) -> BondSeriesRecord | None:
        series = self._session.get(BondSeriesModel, bond_series_id)
        if series is None:
            return None
        return self._to_record(series)

    def _to_record(self, series: BondSeriesModel) -> BondSeriesRecord:
        coupon_dates = self._session.scalars(
            select(BondCouponDateModel.payment_date)
            .where(BondCouponDateModel.bond_series_id == series.id)
            .order_by(BondCouponDateModel.payment_date)
        ).all()
        return BondSeriesRecord(
            id=series.id,
            bond_type=BondType(series.bond_type),
            maturity_date=series.maturity_date,
            coupon_rate_annual=series.coupon_rate_annual,
            coupon_dates=tuple(coupon_dates),
        )

    def get_quote(self, bond_series_id: UUID, quote_date: date) -> MarketQuoteRecord | None:
        quote = self._session.scalar(
            select(BondMarketQuoteModel).where(
                BondMarketQuoteModel.bond_series_id == bond_series_id,
                BondMarketQuoteModel.quote_date == quote_date,
            )
        )
        if quote is None:
            return None
        return MarketQuoteRecord(quote_date=quote.quote_date, reference_rate_annual=quote.buy_rate_annual)

    def list_quotes(self, bond_series_id: UUID, limit: int) -> list[MarketQuoteRecord]:
        rows = self._session.scalars(
            select(BondMarketQuoteModel)
            .where(BondMarketQuoteModel.bond_series_id == bond_series_id)
            .order_by(BondMarketQuoteModel.quote_date.desc())
            .limit(limit)
        ).all()
        return [
            MarketQuoteRecord(quote_date=row.quote_date, reference_rate_annual=row.buy_rate_annual)
            for row in rows
        ]

    def get_vna(self, bond_type: BondType, reference_date: date) -> Money | None:
        return None  # VNA ainda não orquestrado — ver BondTypeNotYetSupported
