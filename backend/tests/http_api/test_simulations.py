from decimal import Decimal
from uuid import uuid4

from tests.http_api.support import LTN_ID, PURCHASE_DATE, REFERENCE_DATE


def _create_payload(**overrides):
    payload = {
        "bond_series_id": str(LTN_ID),
        "purchase_date": PURCHASE_DATE.isoformat(),
        "amount_invested": "1000",
        "reference_date": REFERENCE_DATE.isoformat(),
    }
    payload.update(overrides)
    return payload


def test_create_simulation_returns_full_decomposition(client):
    response = client.post("/api/v1/simulations", json=_create_payload())
    assert response.status_code == 201
    body = response.json()
    assert body["bond_type"] == "LTN"
    assert Decimal(body["amount_invested"]) == Decimal("1000")
    assert "taxes" in body
    assert set(body["taxes"]) == {"gross_gain", "iof_amount", "ir_amount", "net_gain"}
    assert "id" in body


def test_get_simulation_after_creation(client):
    created = client.post("/api/v1/simulations", json=_create_payload()).json()
    response = client.get(f"/api/v1/simulations/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_unknown_simulation_returns_404(client):
    response = client.get(f"/api/v1/simulations/{uuid4()}")
    assert response.status_code == 404


def test_create_simulation_unknown_bond_returns_404_rfc7807(client):
    response = client.post("/api/v1/simulations", json=_create_payload(bond_series_id=str(uuid4())))
    assert response.status_code == 404
    assert response.json()["type"] == "urn:vertice:error:bond-series-not-found"


def test_create_simulation_rejects_non_positive_amount(client):
    response = client.post("/api/v1/simulations", json=_create_payload(amount_invested="0"))
    assert response.status_code == 422
    assert response.json()["type"] == "urn:vertice:error:validation-error"


def test_scenario_recalculates_with_shock(client):
    created = client.post("/api/v1/simulations", json=_create_payload()).json()

    up = client.post(
        f"/api/v1/simulations/{created['id']}/scenarios", json={"shock_bps": 200}
    ).json()
    down = client.post(
        f"/api/v1/simulations/{created['id']}/scenarios", json={"shock_bps": -200}
    ).json()

    assert Decimal(up["pu_reference"]) < Decimal(created["pu_reference"])
    assert Decimal(down["pu_reference"]) > Decimal(created["pu_reference"])


def test_scenario_rejects_shock_outside_step(client):
    created = client.post("/api/v1/simulations", json=_create_payload()).json()
    response = client.post(
        f"/api/v1/simulations/{created['id']}/scenarios", json={"shock_bps": 37}
    )
    assert response.status_code == 422


def test_scenario_for_unknown_simulation_returns_404(client):
    response = client.post(f"/api/v1/simulations/{uuid4()}/scenarios", json={"shock_bps": 50})
    assert response.status_code == 404
