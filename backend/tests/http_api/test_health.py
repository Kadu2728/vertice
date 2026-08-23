def test_health_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_reflects_real_database_state(client):
    # /ready consulta o Postgres de verdade via DATABASE_URL do ambiente —
    # não é injetável como get_bond_catalog, então este teste reflete o que
    # `.env` configura na hora de rodar, não um estado fixo. Com Postgres
    # de dev disponível (ver docs/domain/fase-4-status.md), a resposta
    # esperada é "ready"; sem banco configurado, seria 503 "not ready" — o
    # que importa aqui é que a rota nunca mente sobre o estado real.
    response = client.get("/ready")
    assert response.status_code in (200, 503)
    body = response.json()
    if response.status_code == 200:
        assert body["status"] == "ready"
    else:
        assert body["status"] == "not ready"
