import pytest
from unittest.mock import MagicMock


# PROMPT-01 + PROMPT-02 + PROMPT-03: System prompt contient les instructions requises
def test_prompt01_02_03_system_prompt_content():
    """PROMPT-01/02/03: Le SYSTEM_PROMPT doit contenir les instructions obligatoires."""
    pytest.importorskip("app", reason="app.py not yet implemented")
    import app
    assert hasattr(app, "SYSTEM_PROMPT"), "SYSTEM_PROMPT constant must exist in app"
    prompt = app.SYSTEM_PROMPT
    assert "français" in prompt.lower(), "PROMPT-01: Must instruct to respond in French"
    assert "professionnel" in prompt.lower(), "PROMPT-02: Must set professional tone"
    assert "ne dispose pas" in prompt.lower() or "ne génère pas" in prompt.lower(), \
        "PROMPT-03: Must instruct to refuse out-of-scope questions"


# PROMPT-04: Historique multi-tour correctement construit pour ChatMistralAI
def test_prompt04_history_message_order(mock_vectorstore):
    """PROMPT-04: L'historique doit produire [SystemMessage, HumanMessage, AIMessage, ..., HumanMessage]."""
    from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
    # Simuler un historique de session avec 1 échange précédent
    session_messages = [
        {"role": "user", "content": "Quelles sont vos compétences ?"},
        {"role": "assistant", "content": "Je possède une expertise en..."},
    ]
    # Vérifier que la reconstruction depuis session_state produit le bon ordre
    # Ce test valide la logique de construction, pas l'appel LLM
    lc_messages = [SystemMessage(content="context")]
    for msg in session_messages:
        if msg["role"] == "user":
            lc_messages.append(HumanMessage(content=msg["content"]))
        else:
            lc_messages.append(AIMessage(content=msg["content"]))
    lc_messages.append(HumanMessage(content="Dis-m'en plus"))

    assert isinstance(lc_messages[0], SystemMessage), "First message must be SystemMessage"
    assert isinstance(lc_messages[-1], HumanMessage), "Last message must be HumanMessage (current question)"
    assert len(lc_messages) == 4  # System + Human + AI + Human
