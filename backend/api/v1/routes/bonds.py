from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query

from api.dependencies import get_bond_catalog
from api.v1.schemas.bonds import BondQuoteResponse, BondSeriesResponse
from application.simulations.ports import BondCatalogPort
from application.simulations.service import BondSeriesNotFound

router = APIRouter(prefix="/bonds", tags=["bonds"])


@router.get("", response_model=list[BondSeriesResponse])
def list_bonds(catalog: BondCatalogPort = Depends(get_bond_catalog)) -> list[BondSeriesResponse]:
    return [BondSeriesResponse.model_validate(record) for record in catalog.list_bond_series()]


@router.get("/{bond_series_id}", response_model=BondSeriesResponse)
def get_bond(
    bond_series_id: UUID, catalog: BondCatalogPort = Depends(get_bond_catalog)
) -> BondSeriesResponse:
    record = catalog.get_bond_series(bond_series_id)
    if record is None:
        raise BondSeriesNotFound(bond_series_id)
    return BondSeriesResponse.model_validate(record)


@router.get("/{bond_series_id}/quotes", response_model=list[BondQuoteResponse])
def get_bond_quotes(
    bond_series_id: UUID,
    limit: int = Query(default=30, ge=1, le=365),
    catalog: BondCatalogPort = Depends(get_bond_catalog),
) -> list[BondQuoteResponse]:
    if catalog.get_bond_series(bond_series_id) is None:
        raise BondSeriesNotFound(bond_series_id)
    quotes = catalog.list_quotes(bond_series_id, limit)
    return [BondQuoteResponse.model_validate(q) for q in quotes]
