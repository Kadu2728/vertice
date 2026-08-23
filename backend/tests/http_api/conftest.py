"""Fixtures de teste de API — sobrescrevem os providers de dependência com
fakes em memória via `app.dependency_overrides`. Nenhum teste de API
depende de Postgres estar disponível (ver docs/domain/fase-3-status.md)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from api.dependencies import get_bond_catalog, get_simulation_store
from api.main import create_app
from application.simulations.store import InMemorySimulationStore
from tests.http_api.support import FakeCatalog, build_fake_catalog


@pytest.fixture
def fake_catalog() -> FakeCatalog:
    return build_fake_catalog()


@pytest.fixture
def client(fake_catalog: FakeCatalog) -> TestClient:
    app = create_app()
    store = InMemorySimulationStore()  # uma instância por teste, compartilhada entre requests
    app.dependency_overrides[get_bond_catalog] = lambda: fake_catalog
    app.dependency_overrides[get_simulation_store] = lambda: store
    return TestClient(app)
