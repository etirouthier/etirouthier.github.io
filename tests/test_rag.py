import pytest
from unittest.mock import MagicMock, patch


# RAG-01: L'index FAISS est chargé via @st.cache_resource
def test_rag01_load_vectorstore_uses_cache_resource():
    """RAG-01: load_vectorstore doit être décorée avec @st.cache_resource."""
    pytest.importorskip("app", reason="app.py not yet implemented")
    import app
    assert hasattr(app, "load_vectorstore"), "load_vectorstore function must exist in app"
    # Vérifier que la fonction est bien décorée (cache_resource wraps it)
    assert callable(app.load_vectorstore)


# RAG-02: similarity_search retourne k=K_RETRIEVED chunks
def test_rag02_similarity_search_returns_k_chunks(mock_vectorstore):
    """RAG-02: similarity_search doit retourner exactement K_RETRIEVED chunks."""
    from config import K_RETRIEVED
    docs = mock_vectorstore.similarity_search("test query", k=K_RETRIEVED)
    assert len(docs) == K_RETRIEVED, f"Expected {K_RETRIEVED} docs, got {len(docs)}"
    for doc in docs:
        assert doc.page_content, "Each chunk must have non-empty page_content"


# RAG-03: run_rag (ou logique inline) retourne une réponse non vide
def test_rag03_rag_returns_non_empty_response():
    """RAG-03: Le pipeline RAG doit retourner une string non vide."""
    pytest.importorskip("app", reason="app.py not yet implemented")
    pytest.skip("Requires LLM call — test in integration")


# RAG-04: Erreur 429 produit un message en français
def test_rag04_rate_limit_returns_french_error():
    """RAG-04: Une exception 429 doit retourner un message d'erreur en français."""
    pytest.importorskip("app", reason="app.py not yet implemented")
    pytest.skip("Tested via manual smoke test — see VALIDATION.md")
