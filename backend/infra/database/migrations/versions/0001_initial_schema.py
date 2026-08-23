"""schema inicial — catálogo, cotações, indexadores, tributação, simulações

Revision ID: 0001
Revises:
Create Date: 2026-08-21
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "bond_series",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("bond_type", sa.String(32), nullable=False),
        sa.Column("maturity_date", sa.Date(), nullable=False),
        sa.Column("coupon_rate_annual", sa.Numeric(12, 8), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("bond_type", "maturity_date", name="uq_bond_series_type_maturity"),
    )

    op.create_table(
        "bond_coupon_dates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "bond_series_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("bond_series.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("payment_date", sa.Date(), nullable=False),
        sa.UniqueConstraint("bond_series_id", "payment_date", name="uq_bond_coupon_date"),
    )
    op.create_index(
        "ix_bond_coupon_dates_series", "bond_coupon_dates", ["bond_series_id"]
    )

    op.create_table(
        "bond_market_quotes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "bond_series_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("bond_series.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("quote_date", sa.Date(), nullable=False),
        sa.Column("buy_rate_annual", sa.Numeric(12, 8), nullable=False),
        sa.Column("sell_rate_annual", sa.Numeric(12, 8), nullable=False),
        sa.Column("buy_pu", sa.Numeric(18, 6), nullable=False),
        sa.Column("sell_pu", sa.Numeric(18, 6), nullable=False),
        sa.Column("base_pu", sa.Numeric(18, 6), nullable=False),
        sa.Column("ingested_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("bond_series_id", "quote_date", name="uq_bond_quote_series_date"),
    )
    op.create_index(
        "ix_bond_market_quotes_series_date",
        "bond_market_quotes",
        ["bond_series_id", "quote_date"],
    )
    op.create_index(
        "ix_bond_market_quotes_date_brin",
        "bond_market_quotes",
        ["quote_date"],
        postgresql_using="brin",
    )

    op.create_table(
        "index_series_points",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("indexer", sa.String(16), nullable=False),
        sa.Column("unit_period", sa.String(8), nullable=False),
        sa.Column("reference_date", sa.Date(), nullable=False),
        sa.Column("value", sa.Numeric(14, 8), nullable=False),
        sa.Column("ingested_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("indexer", "reference_date", name="uq_index_series_point"),
        sa.CheckConstraint("unit_period IN ('daily', 'monthly')", name="ck_index_unit_period"),
    )
    op.create_index(
        "ix_index_series_points_indexer_date",
        "index_series_points",
        ["indexer", "reference_date"],
    )

    op.create_table(
        "tax_brackets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("min_days", sa.Integer(), nullable=False),
        sa.Column("max_days", sa.Integer(), nullable=True),
        sa.Column("rate", sa.Numeric(6, 4), nullable=False),
        sa.Column("valid_from", sa.Date(), nullable=False),
        sa.Column("valid_to", sa.Date(), nullable=True),
    )

    op.create_table(
        "custody_fee_schedules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("annual_rate", sa.Numeric(6, 4), nullable=False),
        sa.Column("exempt_bond_type", sa.String(32), nullable=True),
        sa.Column("exempt_threshold", sa.Numeric(18, 6), nullable=True),
        sa.Column("valid_from", sa.Date(), nullable=False),
        sa.Column("valid_to", sa.Date(), nullable=True),
    )

    op.create_table(
        "simulations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "bond_series_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("bond_series.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("purchase_date", sa.Date(), nullable=False),
        sa.Column("amount_invested", sa.Numeric(18, 6), nullable=False),
        sa.Column("reference_date", sa.Date(), nullable=False),
        sa.Column("calculation_engine_version", sa.String(32), nullable=False),
        sa.Column("result", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_simulations_bond_series", "simulations", ["bond_series_id"])

    op.create_table(
        "scenario_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "simulation_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("simulations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("shock_bps", sa.Integer(), nullable=False),
        sa.Column("result", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("simulation_id", "shock_bps", name="uq_scenario_simulation_shock"),
    )


def downgrade() -> None:
    op.drop_table("scenario_results")
    op.drop_table("simulations")
    op.drop_table("custody_fee_schedules")
    op.drop_table("tax_brackets")
    op.drop_table("index_series_points")
    op.drop_table("bond_market_quotes")
    op.drop_table("bond_coupon_dates")
    op.drop_table("bond_series")
