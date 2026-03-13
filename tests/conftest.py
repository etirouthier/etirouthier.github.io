import pytest
from unittest.mock import MagicMock
from langchain_core.documents import Document


@pytest.fixture
def mock_vectorstore():
    """Retourne un vectorstore simulé dont similarity_search retourne K_RETRIEVED Documents."""
    vs = MagicMock()
    vs.similarity_search.return_value = [
        Document(page_content=f"Chunk {i}: Etienne Routhier est expert en...")
        for i in range(4)
    ]
    return vs


@pytest.fixture
def mock_llm_response():
    """Retourne une réponse LLM simulée (AIMessage-like)."""
    response = MagicMock()
    response.content = "Etienne Routhier possède une expertise en développement logiciel."
    return response
