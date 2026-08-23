from pathlib import Path

import pytest

from infra.ai.rag import LexicalRetriever, load_corpus

CORPUS_DIR = Path(__file__).resolve().parents[4] / "docs" / "domain" / "rag-corpus"


@pytest.fixture(scope="module")
def retriever() -> LexicalRetriever:
    chunks = load_corpus(CORPUS_DIR)
    assert chunks, f"corpus vazio em {CORPUS_DIR} — verifique o caminho"
    return LexicalRetriever(chunks)


def test_corpus_loads_real_files():
    chunks = load_corpus(CORPUS_DIR)
    sources = {c.source for c in chunks}
    assert "ir-regressivo.md" in sources
    assert "iof-regressivo.md" in sources
    assert "custodia-b3.md" in sources
    assert "marcacao-a-mercado.md" in sources


def test_search_finds_relevant_chunk_for_ir(retriever: LexicalRetriever):
    results = retriever.search("qual a alíquota de imposto de renda depois de 720 dias?")
    assert results
    assert any(c.source == "ir-regressivo.md" for c in results)


def test_search_finds_relevant_chunk_for_custody(retriever: LexicalRetriever):
    results = retriever.search("como funciona a taxa de custódia da B3?")
    assert results
    assert any(c.source == "custodia-b3.md" for c in results)


def test_search_finds_relevant_chunk_for_marcacao(retriever: LexicalRetriever):
    results = retriever.search("por que o preço do meu título prefixado caiu quando a taxa subiu?")
    assert results
    assert any(c.source == "marcacao-a-mercado.md" for c in results)


def test_search_with_no_overlap_returns_empty(retriever: LexicalRetriever):
    assert retriever.search("xilofone banana paraquedas") == []


def test_search_respects_top_k(retriever: LexicalRetriever):
    results = retriever.search("título", top_k=2)
    assert len(results) <= 2
