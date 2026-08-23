from tests.http_api.support import LTN_ID


def test_list_bonds_returns_catalog(client):
    response = client.get("/api/v1/bonds")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["bond_type"] == "LTN"


def test_get_bond_returns_series(client):
    response = client.get(f"/api/v1/bonds/{LTN_ID}")
    assert response.status_code == 200
    assert response.json()["id"] == str(LTN_ID)


def test_get_bond_404_follows_rfc7807_shape(client):
    from uuid import uuid4

    response = client.get(f"/api/v1/bonds/{uuid4()}")
    assert response.status_code == 404
    assert response.headers["content-type"] == "application/problem+json"
    body = response.json()
    assert body["type"] == "urn:vertice:error:bond-series-not-found"
    assert body["status"] == 404


def test_get_bond_quotes_returns_history(client):
    response = client.get(f"/api/v1/bonds/{LTN_ID}/quotes")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2


def test_get_bond_quotes_404_for_unknown_series(client):
    from uuid import uuid4

    response = client.get(f"/api/v1/bonds/{uuid4()}/quotes")
    assert response.status_code == 404
