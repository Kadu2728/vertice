from __future__ import annotations

from datetime import date
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_bond_catalog, get_simulation_store
from api.v1.schemas.simulations import (
    ScenarioCreateRequest,
    SimulationCreateRequest,
    SimulationResponse,
    TaxBreakdownResponse,
)
from application.simulations.ports import BondCatalogPort
from application.simulations.service import (
    SimulationResult,
    calculate_scenario,
    calculate_simulation,
)
from application.simulations.store import SimulationStore

router = APIRouter(prefix="/simulations", tags=["simulations"])


def _to_response(simulation_id: UUID, result: SimulationResult) -> SimulationResponse:
    return SimulationResponse(
        id=simulation_id,
        bond_series_id=result.bond_series_id,
        bond_type=result.bond_type.value,
        purchase_date=result.purchase_date,
        reference_date=result.reference_date,
        amount_invested=result.amount_invested,
        quantity=result.quantity,
        pu_purchase=result.pu_purchase,
        pu_reference=result.pu_reference,
        gross_value_today=result.gross_value_today,
        days_held=result.days_held,
        taxes=TaxBreakdownResponse.model_validate(result.taxes),
        custody_fee_amount=result.custody_fee_amount,
        net_value_today=result.net_value_today,
        calculation_engine_version=result.calculation_engine_version,
    )


@router.post("", response_model=SimulationResponse, status_code=201)
def create_simulation(
    body: SimulationCreateRequest,
    catalog: BondCatalogPort = Depends(get_bond_catalog),
    store: SimulationStore = Depends(get_simulation_store),
) -> SimulationResponse:
    reference_date = body.reference_date or date.today()
    result = calculate_simulation(
        catalog, body.bond_series_id, body.purchase_date, reference_date, body.amount_invested
    )
    simulation_id = uuid4()
    store.save(simulation_id, result)
    return _to_response(simulation_id, result)


@router.get("/{simulation_id}", response_model=SimulationResponse)
def get_simulation(
    simulation_id: UUID, store: SimulationStore = Depends(get_simulation_store)
) -> SimulationResponse:
    result = store.get(simulation_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Simulação não encontrada")
    return _to_response(simulation_id, result)


@router.post("/{simulation_id}/scenarios", response_model=SimulationResponse)
def create_scenario(
    simulation_id: UUID,
    body: ScenarioCreateRequest,
    catalog: BondCatalogPort = Depends(get_bond_catalog),
    store: SimulationStore = Depends(get_simulation_store),
) -> SimulationResponse:
    base = store.get(simulation_id)
    if base is None:
        raise HTTPException(status_code=404, detail="Simulação não encontrada")

    result = calculate_scenario(
        catalog,
        base.bond_series_id,
        base.purchase_date,
        base.reference_date,
        base.amount_invested,
        body.shock_bps,
    )
    return _to_response(simulation_id, result)
