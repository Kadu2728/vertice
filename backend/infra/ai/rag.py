"""RAG restrito — só sobre documentação factual (docs/domain/rag-corpus/),
nunca sobre preço ou dado numérico de mercado (docs/00-discovery.md §22:
"não indexar preços históricos, séries numéricas ou dados de mercado").

Recuperação léxica (contagem de termos compartilhados), não embeddings —
o corpus é pequeno (5 documentos curados) e isso evita depender de uma API
de embeddings antes mesmo de ter a chave do LLM configurada. `pgvector`
fica para se o corpus crescer a ponto de precisão léxica não bastar mais
(ver ADR de Fase 6 quando essa decisão for tomada de verdade)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

_WORD_RE = re.compile(r"[a-zà-ú0-9]+", re.IGNORECASE)

# Termos genéricos demais para ajudar a distinguir um chunk do outro —
# reduzido de propósito (português, domínio financeiro) em vez de uma lista
# de stopwords genérica importada de uma lib.
_STOPWORDS = frozenset(
    {
        "a", "o", "as", "os", "de", "da", "do", "das", "dos", "e", "é", "em",
        "um", "uma", "para", "por", "com", "no", "na", "nos", "nas", "que",
        "se", "ao", "aos", "à", "às", "não", "sobre", "como", "mais", "ou",
    }
)


def _tokenize(text: str) -> set[str]:
    return {w for w in _WORD_RE.findall(text.lower()) if w not in _STOPWORDS}


@dataclass(frozen=True, slots=True)
class CorpusChunk:
    source: str
    heading: str
    text: str


def load_corpus(directory: Path) -> list[CorpusChunk]:
    """Cada `## heading` de cada .md em `directory` vira um chunk. Um
    documento sem nenhum `##` (curto demais para precisar de subseções)
    vira um chunk único, usando o título de nível 1 como heading — sem
    esse fallback, um arquivo assim desaparecia do corpus em silêncio."""
    chunks: list[CorpusChunk] = []
    for path in sorted(directory.glob("*.md")):
        content = path.read_text(encoding="utf-8")
        sections = re.split(r"^## ", content, flags=re.MULTILINE)
        if len(sections) == 1:
            title_match = re.match(r"^#\s+(.+)", content)
            heading = title_match.group(1).strip() if title_match else path.stem
            body = content[title_match.end():].strip() if title_match else content.strip()
            if body:
                chunks.append(CorpusChunk(source=path.name, heading=heading, text=body))
            continue
        for section in sections[1:]:  # sections[0] é o título de nível 1, sem corpo útil
            lines = section.split("\n", 1)
            heading = lines[0].strip()
            body = lines[1].strip() if len(lines) > 1 else ""
            if body:
                chunks.append(CorpusChunk(source=path.name, heading=heading, text=body))
    return chunks


class LexicalRetriever:
    def __init__(self, chunks: list[CorpusChunk]) -> None:
        self._chunks = chunks
        self._token_sets = [_tokenize(f"{c.heading} {c.text}") for c in chunks]

    def search(self, query: str, top_k: int = 3) -> list[CorpusChunk]:
        query_tokens = _tokenize(query)
        if not query_tokens:
            return []
        scored = [
            (len(query_tokens & tokens), chunk)
            for tokens, chunk in zip(self._token_sets, self._chunks)
        ]
        scored = [pair for pair in scored if pair[0] > 0]
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [chunk for _, chunk in scored[:top_k]]
