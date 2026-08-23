import json
from uuid import uuid4

from api.dependencies import get_llm_client
from infra.ai.llm_client import FakeLlmClient
from tests.http_api.support import LTN_ID, PURCHASE_DATE, REFERENCE_DATE


def _simulate(client) -> str:
    response = client.post(
        "/api/v1/simulations",
        json={
            "bond_series_id": str(LTN_ID),
            "purchase_date": PURCHASE_DATE.isoformat(),
            "amount_invested": "1000",
            "reference_date": REFERENCE_DATE.isoformat(),
        },
    )
    return response.json()["id"]


def test_explanation_falls_back_without_llm_configured(client):
    # sem GEMINI_API_KEY neste ambiente de teste, get_llm_client devolve
    # UnavailableLlmClient de verdade — isto testa o caminho de fallback
    # ponta a ponta, não um mock do fallback.
    simulation_id = _simulate(client)
    response = client.post("/api/v1/explanations", json={"simulation_id": simulation_id})
    assert response.status_code == 200
    body = response.json()
    assert "automaticamente" in " ".join(body["warnings"]).lower()


def test_explanation_uses_llm_when_available(client):
    simulation_id = _simulate(client)
    fake_response = json.dumps(
        {"title": "Seu título valorizou", "body": "Explicação gerada pela IA.", "warnings": []}
    )
    client.app.dependency_overrides[get_llm_client] = lambda: FakeLlmClient(response=fake_response)

    response = client.post("/api/v1/explanations", json={"simulation_id": simulation_id})
    assert response.status_code == 200
    assert response.json()["title"] == "Seu título valorizou"


def test_explanation_guardrail_blocks_recommendation_question(client):
    simulation_id = _simulate(client)
    fake_response = json.dumps({"title": "x", "body": "y", "warnings": []})
    client.app.dependency_overrides[get_llm_client] = lambda: FakeLlmClient(response=fake_response)

    response = client.post(
        "/api/v1/explanations",
        json={"simulation_id": simulation_id, "question": "Devo vender meu título agora?"},
    )
    assert response.status_code == 200
    assert "recomend" in response.json()["body"].lower()


def test_explanation_for_unknown_simulation_returns_404(client):
    response = client.post("/api/v1/explanations", json={"simulation_id": str(uuid4())})
    assert response.status_code == 404


def test_explanation_rejects_question_over_max_length(client):
    simulation_id = _simulate(client)
    response = client.post(
        "/api/v1/explanations",
        json={"simulation_id": simulation_id, "question": "a" * 281},
    )
    assert response.status_code == 422
