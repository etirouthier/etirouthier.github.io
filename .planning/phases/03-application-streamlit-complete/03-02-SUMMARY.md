---
phase: 03-application-streamlit-complete
plan: 02
subsystem: rag-app
tags: [streamlit, rag, faiss, mistral, langchain]
dependency_graph:
  requires:
    - 02-01 (faiss_index/ committed)
    - 03-01 (test infrastructure with conftest.py, test_rag.py, test_prompt.py)
  provides:
    - app.py (Streamlit RAG application, full pipeline)
  affects:
    - requirements.txt (no change — all deps already present)
tech_stack:
  added: []
  patterns:
    - st.cache_resource for vectorstore singleton
    - inject_question callback pattern for suggested buttons (avoids race condition)
    - LangChain message list [SystemMessage, HumanMessage*, AIMessage*...HumanMessage] for multi-turn
key_files:
  created:
    - app.py
  modified: []
decisions:
  - allow_dangerous_deserialization=True required for FAISS.load_local (pickle deserialization)
  - Suggested buttons only shown when len(messages)==0 per UI-03 spec
  - active_question resolved before pending_question cleared to avoid re-render issues
  - Error message for 429 displayed inside assistant chat bubble (not st.error outside)
requirements-completed: [RAG-01, RAG-02, RAG-03, RAG-04, UI-01, UI-02, UI-03, UI-04, UI-05, PROMPT-01, PROMPT-02, PROMPT-03, PROMPT-04]

metrics:
  duration: ~8min
  completed_date: "2026-03-13"
  tasks_completed: 2/2
  files_created: 1
  files_modified: 0
---

# Phase 03 Plan 02: Implement app.py — Streamlit RAG Application Summary

**One-liner:** Streamlit chat app with FAISS/Mistral RAG pipeline, session history, suggested question buttons, and French error handling for rate limits.

## What Was Built

`app.py` (102 lines) — the main deliverable of the project. A Streamlit chat interface that:

1. Loads the FAISS index at startup via `@st.cache_resource` (RAG-01)
2. Retrieves K_RETRIEVED=4 relevant chunks per query via `similarity_search` (RAG-02)
3. Builds a LangChain message list with full session history for multi-turn context (PROMPT-04)
4. Invokes `ChatMistralAI(model="mistral-small-latest")` for response generation (RAG-03)
5. Handles HTTP 429 / rate limit errors with a French-language message in the assistant bubble (RAG-04)
6. Displays two suggested question buttons before the first message (UI-03, UI-04)
7. Maintains conversation history throughout the session (UI-01, UI-02)
8. Uses `SYSTEM_PROMPT` constant that enforces French responses, professional tone, and scope limitation (PROMPT-01/02/03)

## Test Results

```
tests/test_prompt.py::test_prompt01_02_03_system_prompt_content PASSED
tests/test_prompt.py::test_prompt04_history_message_order PASSED
tests/test_rag.py::test_rag01_load_vectorstore_uses_cache_resource PASSED
tests/test_rag.py::test_rag02_similarity_search_returns_k_chunks PASSED
tests/test_rag.py::test_rag03_rag_returns_non_empty_response SKIPPED (requires LLM call)
tests/test_rag.py::test_rag04_rate_limit_returns_french_error SKIPPED (manual smoke test)
4 passed, 2 skipped
```

## Task Commits

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Implémenter app.py — pipeline RAG complet | b4a6224 | app.py (created, 102 lines) |
| 2 | Vérification manuelle | approved | checkpoint:human-verify — user approved |

## Deviations from Plan

None — plan executed exactly as written.

## Self-Check

- [x] app.py exists at `/workspaces/etienne.routhier/app.py`
- [x] app.py is 102 lines (< 120 limit)
- [x] Commit b4a6224 verified
- [x] 4 tests pass, 2 skip (as expected per plan)
- [x] SYSTEM_PROMPT contains "français", "professionnel", "ne dispose pas"
- [x] load_vectorstore decorated with @st.cache_resource
- [x] from config import used (no constant duplication)

## Self-Check: PASSED
