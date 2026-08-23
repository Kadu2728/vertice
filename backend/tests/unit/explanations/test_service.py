import json
from datetime import date
from decimal import Decimal
from uuid import UUID

from application.explanations.service import generate_explanation
from application.simulations.service import SimulationResult
from domain.bonds.bond_type import BondType
from domain.taxation.net_proceeds import TaxBreakdown
from infra.ai.llm_client import FakeLlmClient


def _simulation() -> SimulationResult:
    return SimulationResult(
        bond_series_id=UUID("11111111-1111-1111-1111-111111111111"),
        bond_type=BondType.LTN,
        purchase_date=date(2025, 1, 2),
        reference_date=date(2026, 8, 21),
        amount_invested=Decimal("1000"),
        quantity=Decimal("1.788788244844963"),
        pu_purchase=Decimal("559.037663"),
        pu_reference=Decimal("733.277405"),
        gross_value_today=Decimal("1311.68"),
        days_held=596,
        taxes=TaxBreakdown(
            gross_gain=Decimal("311.68"),
            iof_amount=Decimal("0"),
            ir_amount=Decimal("54.54"),
            net_gain=Decimal("257.13"),
        ),
        custody_fee_amount=Decimal("4.28"),
        net_value_today=Decimal("1252.85"),
    )


def _valid_response() -> str:
    return json.dumps(
        {
            "title": "Seu título valorizou",
            "body": "O valor líquido hoje é R$ 1.252,85, um ganho frente aos R$ 1.000,00 investidos.",
            "warnings": [],
        }
    )


def test_happy_path_returns_llm_response():
    client = FakeLlmClient(response=_valid_response())
    output = generate_explanation(_simulation(), client)
    assert output.title == "Seu título valorizou"
    assert "1.252,85" in output.body


def test_guardrail_blocks_before_calling_llm():
    client = FakeLlmClient(response=_valid_response())
    output = generate_explanation(_simulation(), client, question="Devo vender agora?")
    assert client.last_user_prompt is None  # LLM nunca foi chamada
    assert "não posso recomendar" in output.title.lower() or "recomendar" in output.body.lower()


def test_llm_error_falls_back():
    client = FakeLlmClient(error=RuntimeError("provider indisponível"))
    output = generate_explanation(_simulation(), client)
    assert "automaticamente" in " ".join(output.warnings).lower()


def test_malformed_json_falls_back():
    client = FakeLlmClient(response="isto não é json")
    output = generate_explanation(_simulation(), client)
    assert "automaticamente" in " ".join(output.warnings).lower()


def test_missing_schema_field_falls_back():
    client = FakeLlmClient(response=json.dumps({"title": "Só título, sem body"}))
    output = generate_explanation(_simulation(), client)
    assert "automaticamente" in " ".join(output.warnings).lower()


def test_hallucinated_number_falls_back():
    bad_response = json.dumps(
        {
            "title": "Resultado",
            "body": "Seu título vale R$ 99.999,00 hoje.",  # não bate com o payload
            "warnings": [],
        }
    )
    client = FakeLlmClient(response=bad_response)
    output = generate_explanation(_simulation(), client)
    assert "automaticamente" in " ".join(output.warnings).lower()


def test_prompt_never_contains_a_calculation_instruction_bypass():
    # sanity check de que o contexto realmente carrega os números prontos,
    # não instruções pra IA calcular algo
    client = FakeLlmClient(response=_valid_response())
    generate_explanation(_simulation(), client)
    assert "R$ 1.252,85" in client.last_user_prompt
    assert "R$ 1.000,00" in client.last_user_prompt
