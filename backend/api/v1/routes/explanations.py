from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_llm_client, get_retriever, get_simulation_store
from api.v1.schemas.explanations import ExplanationRequest, ExplanationResponse
from application.explanations.service import generate_explanation
from application.simulations.store import SimulationStore
from infra.ai.llm_client import LlmClient
from infra.ai.rag import LexicalRetriever

router = APIRouter(prefix="/explanations", tags=["explanations"])


@router.post("", response_model=ExplanationResponse)
def create_explanation(
    body: ExplanationRequest,
    store: SimulationStore = Depends(get_simulation_store),
    llm_client: LlmClient = Depends(get_llm_client),
    retriever: LexicalRetriever = Depends(get_retriever),
) -> ExplanationResponse:
    simulation = store.get(body.simulation_id)
    if simulation is None:
        raise HTTPException(status_code=404, detail="Simulação não encontrada")

    output = generate_explanation(simulation, llm_client, retriever, body.question)
    return ExplanationResponse(title=output.title, body=output.body, warnings=output.warnings)
