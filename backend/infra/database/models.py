"""Schema de persistência — ver docs/00-discovery.md §4/§5 para a decisão
por trás de cada tabela e índice.

NUMERIC em toda coluna financeira, nunca FLOAT (ADR-004). `bond_series` e
`tax_brackets`/`custody_fee_schedules` usam ON DELETE RESTRICT — histórico
financeiro não pode perder a série/regra que referencia. `scenario_results`
usa CASCADE a partir de `simulations`: um cenário só existe em função de
uma simulação, apagar a simulação apaga os cenários derivados dela."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import CheckConstraint, Date, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime, Numeric


class Base(DeclarativeBase):
    pass


def _uuid_pk() -> Mapped[uuid.UUID]:
    return mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


class BondSeriesModel(Base):
    """Catálogo de séries — fonte: ingestão do Tesouro Transparente."""

    __tablename__ = "bond_series"

    id: Mapped[uuid.UUID] = _uuid_pk()
    bond_type: Mapped[str] = mapped_column(String(32), nullable=False)
    maturity_date: Mapped[date] = mapped_column(Date, nullable=False)
    coupon_rate_annual: Mapped[Decimal | None] = mapped_column(Numeric(12, 8), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("bond_type", "maturity_date", name="uq_bond_series_type_maturity"),
    )


class BondCouponDateModel(Base):
    """Datas de pagamento de cupom semestral (NTN-F, NTN-B). Tabela própria
    em vez de array/JSON na `bond_series` — cada data é uma linha
    consultável e a integridade referencial (RESTRICT) se aplica igual."""

    __tablename__ = "bond_coupon_dates"

    id: Mapped[uuid.UUID] = _uuid_pk()
    bond_series_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("bond_series.id", ondelete="RESTRICT"), nullable=False
    )
    payment_date: Mapped[date] = mapped_column(Date, nullable=False)

    __table_args__ = (
        UniqueConstraint("bond_series_id", "payment_date", name="uq_bond_coupon_date"),
        Index("ix_bond_coupon_dates_series", "bond_series_id"),
    )


class BondMarketQuoteModel(Base):
    """Cotação diária oficial — append-only, correlacionada com data (ver
    discovery §11 sobre BRIN)."""

    __tablename__ = "bond_market_quotes"

    id: Mapped[uuid.UUID] = _uuid_pk()
    bond_series_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("bond_series.id", ondelete="RESTRICT"), nullable=False
    )
    quote_date: Mapped[date] = mapped_column(Date, nullable=False)
    buy_rate_annual: Mapped[Decimal] = mapped_column(Numeric(12, 8), nullable=False)
    sell_rate_annual: Mapped[Decimal] = mapped_column(Numeric(12, 8), nullable=False)
    buy_pu: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    sell_pu: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    base_pu: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("bond_series_id", "quote_date", name="uq_bond_quote_series_date"),
        Index("ix_bond_market_quotes_series_date", "bond_series_id", "quote_date"),
        Index("ix_bond_market_quotes_date_brin", "quote_date", postgresql_using="brin"),
    )


class IndexSeriesPointModel(Base):
    """Valor publicado de um indexador numa data de referência. `unit_period`
    distingue granularidade — SELIC é diária, IPCA é mensal — para não
    confundir as duas sob a mesma coluna `value` sem contexto."""

    __tablename__ = "index_series_points"

    id: Mapped[uuid.UUID] = _uuid_pk()
    indexer: Mapped[str] = mapped_column(String(16), nullable=False)  # "SELIC", "IPCA", "CDI"
    unit_period: Mapped[str] = mapped_column(String(8), nullable=False)  # "daily" | "monthly"
    reference_date: Mapped[date] = mapped_column(Date, nullable=False)
    value: Mapped[Decimal] = mapped_column(Numeric(14, 8), nullable=False)  # percentual do período
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("indexer", "reference_date", name="uq_index_series_point"),
        Index("ix_index_series_points_indexer_date", "indexer", "reference_date"),
        CheckConstraint("unit_period IN ('daily', 'monthly')", name="ck_index_unit_period"),
    )


class TaxBracketModel(Base):
    """IR regressivo, versionado no tempo — ver domain/taxation/income_tax.py
    para os valores atuais; esta tabela existe para o dia em que a lei
    mudar sem exigir deploy de código para refletir a mudança."""

    __tablename__ = "tax_brackets"

    id: Mapped[uuid.UUID] = _uuid_pk()
    min_days: Mapped[int] = mapped_column(Integer, nullable=False)
    max_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rate: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False)
    valid_from: Mapped[date] = mapped_column(Date, nullable=False)
    valid_to: Mapped[date | None] = mapped_column(Date, nullable=True)


class CustodyFeeScheduleModel(Base):
    """Taxa de custódia B3, versionada — 0,20% a.a. com isenção do Tesouro
    Selic até R$ 10.000, vigente desde 31/12/2024 (ver docs/domain/tributacao-fontes.md)."""

    __tablename__ = "custody_fee_schedules"

    id: Mapped[uuid.UUID] = _uuid_pk()
    annual_rate: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False)
    exempt_bond_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    exempt_threshold: Mapped[Decimal | None] = mapped_column(Numeric(18, 6), nullable=True)
    valid_from: Mapped[date] = mapped_column(Date, nullable=False)
    valid_to: Mapped[date | None] = mapped_column(Date, nullable=True)


class SimulationModel(Base):
    """Snapshot de uma simulação — entrada + resultado calculado, versionado
    por engine. `id` é UUID v4 não sequencial porque também é o
    identificador da URL pública de compartilhamento (discovery §4)."""

    __tablename__ = "simulations"

    id: Mapped[uuid.UUID] = _uuid_pk()
    bond_series_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("bond_series.id", ondelete="RESTRICT"), nullable=False
    )
    purchase_date: Mapped[date] = mapped_column(Date, nullable=False)
    amount_invested: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    reference_date: Mapped[date] = mapped_column(Date, nullable=False)
    calculation_engine_version: Mapped[str] = mapped_column(String(32), nullable=False)
    result: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_simulations_bond_series", "bond_series_id"),
    )


class ScenarioResultModel(Base):
    """Resultado de um choque de taxa sobre uma simulação — CASCADE porque
    não tem sentido sem a simulação que o originou."""

    __tablename__ = "scenario_results"

    id: Mapped[uuid.UUID] = _uuid_pk()
    simulation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("simulations.id", ondelete="CASCADE"), nullable=False
    )
    shock_bps: Mapped[int] = mapped_column(Integer, nullable=False)
    result: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("simulation_id", "shock_bps", name="uq_scenario_simulation_shock"),
    )
