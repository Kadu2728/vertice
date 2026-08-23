"""Orquestra domínio (calendário + pricing + tributação) para produzir o
resultado de uma simulação. Não faz nenhum cálculo financeiro por conta
própria — só chama domain/ na ordem certa e monta o resultado. Se um número
aqui estiver errado, o bug está no domínio, não aqui."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from application.simulations.ports import BondCatalogPort, BondSeriesRecord
from domain.bonds.bond_series import BondSeries
from domain.bonds.bond_type import BondType
from domain.calendars.anbima import AnbimaCalendar
from domain.pricing.ltn import price_ltn
from domain.pricing.ntnf import price_ntnf
from domain.shared.money import Money
from domain.shared.rate import Rate, RateBasis
from domain.taxation.custody import custody_fee
from domain.taxation.net_proceeds import TaxBreakdown, calculate_taxes

CALCULATION_ENGINE_VERSION = "2026.08.1"

# Tipos com precificação totalmente validada e sem dependência de VNA
# (LTN: golden test com tolerância R$ 0,01; NTN-F: golden test com gap
# documentado mas mecanismo completo — ver docs/domain/golden-tests-status.md).
# NTN-B, NTN-B Principal e LFT dependem de VNA (IPCA/Selic) — a orquestração
# de VNA a partir dos dados ingeridos ainda não existe (Fase 3 trouxe só a
# ingestão bruta), por isso ficam fora desta primeira versão da API.
_SUPPORTED_BOND_TYPES = frozenset({BondType.LTN, BondType.NTN_F})


class BondSeriesNotFound(Exception):
    def __init__(self, bond_series_id: UUID) -> None:
        self.bond_series_id = bond_series_id
        super().__init__(f"série de título não encontrada: {bond_series_id}")


class QuoteNotFound(Exception):
    def __init__(self, bond_series_id: UUID, quote_date: date) -> None:
        self.bond_series_id = bond_series_id
        self.quote_date = quote_date
        super().__init__(f"cotação não encontrada para {bond_series_id} em {quote_date}")


class BondTypeNotYetSupported(Exception):
    def __init__(self, bond_type: BondType) -> None:
        self.bond_type = bond_type
        super().__init__(
            f"{bond_type.value} depende de VNA — orquestração ainda não implementada "
            "(ver docs/domain/fase-3-status.md)"
        )


@dataclass(frozen=True, slots=True)
class SimulationResult:
    bond_series_id: UUID
    bond_type: BondType
    purchase_date: date
    reference_date: date
    amount_invested: Decimal
    quantity: Decimal
    pu_purchase: Decimal
    pu_reference: Decimal
    gross_value_today: Decimal
    days_held: int
    taxes: TaxBreakdown
    custody_fee_amount: Decimal
    net_value_today: Decimal
    calculation_engine_version: str = CALCULATION_ENGINE_VERSION


def _to_domain_bond_series(record: BondSeriesRecord) -> BondSeries:
    return BondSeries(
        id=str(record.id),
        bond_type=record.bond_type,
        maturity_date=record.maturity_date,
        coupon_rate_annual=record.coupon_rate_annual,
        coupon_dates=record.coupon_dates,
    )


def _price(bond: BondSeries, settlement: date, calendar: AnbimaCalendar, rate: Rate) -> Money:
    if bond.bond_type == BondType.LTN:
        du = calendar.business_days_between(settlement, bond.maturity_date)
        return price_ltn(rate, du)
    if bond.bond_type == BondType.NTN_F:
        return price_ntnf(bond, settlement, calendar, rate)
    raise BondTypeNotYetSupported(bond.bond_type)


def _load_bond_and_purchase_pu(
    catalog: BondCatalogPort, bond_series_id: UUID, purchase_date: date
) -> tuple[BondSeries, Money]:
    record = catalog.get_bond_series(bond_series_id)
    if record is None:
        raise BondSeriesNotFound(bond_series_id)
    if record.bond_type not in _SUPPORTED_BOND_TYPES:
        raise BondTypeNotYetSupported(record.bond_type)

    purchase_quote = catalog.get_quote(bond_series_id, purchase_date)
    if purchase_quote is None:
        raise QuoteNotFound(bond_series_id, purchase_date)

    calendar = AnbimaCalendar()
    bond = _to_domain_bond_series(record)
    purchase_rate = Rate(purchase_quote.reference_rate_annual, RateBasis.NOMINAL)
    pu_purchase = _price(bond, purchase_date, calendar, purchase_rate)
    return bond, pu_purchase


def _compute_result(
    bond: BondSeries,
    bond_series_id: UUID,
    purchase_date: date,
    reference_date: date,
    amount_invested: Decimal,
    pu_purchase: Money,
    reference_rate: Rate,
) -> SimulationResult:
    calendar = AnbimaCalendar()
    pu_reference = _price(bond, reference_date, calendar, reference_rate)

    quantity = amount_invested / pu_purchase.amount
    gross_value_today = quantity * pu_reference.amount

    days_held = (reference_date - purchase_date).days
    gross_gain = gross_value_today - amount_invested
    taxes = calculate_taxes(gross_gain, days_held)

    fee = custody_fee(bond.bond_type, gross_value_today, days_held)
    net_value_today = amount_invested + taxes.net_gain - fee

    return SimulationResult(
        bond_series_id=bond_series_id,
        bond_type=bond.bond_type,
        purchase_date=purchase_date,
        reference_date=reference_date,
        amount_invested=amount_invested,
        quantity=quantity,
        pu_purchase=pu_purchase.amount,
        pu_reference=pu_reference.amount,
        gross_value_today=gross_value_today,
        days_held=days_held,
        taxes=taxes,
        custody_fee_amount=fee,
        net_value_today=net_value_today,
    )


def calculate_simulation(
    catalog: BondCatalogPort,
    bond_series_id: UUID,
    purchase_date: date,
    reference_date: date,
    amount_invested: Decimal,
) -> SimulationResult:
    bond, pu_purchase = _load_bond_and_purchase_pu(catalog, bond_series_id, purchase_date)

    reference_quote = catalog.get_quote(bond_series_id, reference_date)
    if reference_quote is None:
        raise QuoteNotFound(bond_series_id, reference_date)
    reference_rate = Rate(reference_quote.reference_rate_annual, RateBasis.NOMINAL)

    return _compute_result(
        bond, bond_series_id, purchase_date, reference_date, amount_invested, pu_purchase, reference_rate
    )


def calculate_scenario(
    catalog: BondCatalogPort,
    bond_series_id: UUID,
    purchase_date: date,
    reference_date: date,
    amount_invested: Decimal,
    shock_bps: int,
) -> SimulationResult:
    """Mesmo cálculo de `calculate_simulation`, mas com a taxa do dia de
    referência deslocada por `shock_bps` (1 bps = 0,0001 em fração de taxa)
    — usado pelo simulador de cenário (slider -200/+200 bps, §18 da spec)."""
    bond, pu_purchase = _load_bond_and_purchase_pu(catalog, bond_series_id, purchase_date)

    reference_quote = catalog.get_quote(bond_series_id, reference_date)
    if reference_quote is None:
        raise QuoteNotFound(bond_series_id, reference_date)
    shocked_rate_value = reference_quote.reference_rate_annual + (Decimal(shock_bps) / Decimal(10000))
    reference_rate = Rate(shocked_rate_value, RateBasis.NOMINAL)

    return _compute_result(
        bond, bond_series_id, purchase_date, reference_date, amount_invested, pu_purchase, reference_rate
    )
