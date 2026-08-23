"""Orquestra a explicação: guardrail → payload → (RAG opcional) → LLM →
validação numérica → fallback se qualquer etapa falhar ou divergir. A IA
nunca tem autoridade sobre número (ADR-003) — se o texto gerado citar um
valor que não bate com o payload, a resposta inteira é descartada."""

from __future__ import annotations

import json
import logging

from application.explanations.payload import build_payload, payload_to_prompt_context
from application.explanations.schemas import ExplanationOutput
from application.explanations.templates import render_fallback
from application.simulations.service import SimulationResult
from infra.ai.guardrails import GUARDRAIL_MESSAGE, is_recommendation_seeking
from infra.ai.llm_client import LlmClient
from infra.ai.numeric_validator import all_values_match_reference, extract_currency_values
from infra.ai.rag import LexicalRetriever

logger = logging.getLogger("vertice.explanations")

_SYSTEM_PROMPT = (
    "Você explica resultados de simulações de marcação a mercado de títulos "
    "públicos brasileiros para um investidor de varejo. Use SOMENTE os "
    "números fornecidos no contexto abaixo — nunca calcule, estime ou "
    "invente um valor financeiro que não esteja lá. Responda em português, "
    "tom direto, sem superlativos nem emoji. Devolva só o JSON pedido pelo "
    "schema, nada fora dele."
)


def generate_explanation(
    simulation: SimulationResult,
    llm_client: LlmClient,
    retriever: LexicalRetriever | None = None,
    question: str | None = None,
) -> ExplanationOutput:
    if question and is_recommendation_seeking(question):
        return ExplanationOutput(title="Não posso recomendar isso", body=GUARDRAIL_MESSAGE)

    payload = build_payload(simulation)

    try:
        context = payload_to_prompt_context(payload)
        if retriever is not None and question:
            chunks = retriever.search(question)
            if chunks:
                context += "\n\nDocumentação de referência:\n" + "\n\n".join(
                    f"({c.source} — {c.heading})\n{c.text}" for c in chunks
                )
        user_prompt = context + (f"\n\nPergunta do usuário: {question}" if question else "")

        raw = llm_client.generate_json(
            _SYSTEM_PROMPT, user_prompt, response_schema=ExplanationOutput.model_json_schema()
        )
        parsed = ExplanationOutput.model_validate(json.loads(raw))

        found = extract_currency_values(f"{parsed.title} {parsed.body}")
        if not all_values_match_reference(found, payload.currency_fields()):
            logger.warning("explicação descartada: número no texto não bate com o payload")
            return render_fallback(payload)

        return parsed
    except Exception:
        logger.exception("falha ao gerar explicação via LLM — usando fallback")
        return render_fallback(payload)
