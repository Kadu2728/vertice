"""Bloqueio de recomendação individualizada — roda ANTES de qualquer
chamada ao LLM, não depende do modelo se autocensurar (docs/00-discovery.md
§23, prompt do projeto §23/§38: o produto não recomenda compra/venda nem
determina perfil de investidor).

Baseado em padrão, não em classificação por modelo — mais barato, mais
previsível, e não precisa da API key para funcionar nem ser testado."""

from __future__ import annotations

import re

_RECOMMENDATION_PATTERNS = [
    r"\bdevo\b.*\b(vender|comprar|resgatar|manter)\b",
    r"\bo que (você|voce) (faria|recomenda|sugere)\b",
    r"\bqual (título|titulo) (devo|eu devo) comprar\b",
    r"\bvale a pena\b",
    r"\b(é|e) uma boa (ideia|hora)\b",
    r"\bmelhor (título|titulo|opção|opcao) para mim\b",
    r"\bcompensa\b.*\b(vender|resgatar|comprar)\b",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in _RECOMMENDATION_PATTERNS]

GUARDRAIL_MESSAGE = (
    "Não recomendamos comprar, vender ou manter nenhum título — isso depende "
    "do seu perfil e objetivos, que só você (ou um assessor licenciado) pode "
    "avaliar. Posso mostrar cenários e explicar os números da sua simulação."
)


def is_recommendation_seeking(question: str) -> bool:
    return any(pattern.search(question) for pattern in _COMPILED)
