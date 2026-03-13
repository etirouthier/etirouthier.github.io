---
phase: 3
slug: application-streamlit-complete
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-13
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | none — Wave 0 installs |
| **Quick run command** | `python -m pytest tests/ -x -q 2>/dev/null` |
| **Full suite command** | `python -m pytest tests/ -v` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest tests/ -x -q 2>/dev/null`
- **After every plan wave:** Run `python -m pytest tests/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 3-01-01 | 01 | 0 | RAG-01 | unit | `pytest tests/test_rag.py -x -q` | ❌ W0 | ⬜ pending |
| 3-01-02 | 01 | 1 | RAG-01, RAG-02 | unit | `pytest tests/test_rag.py -x -q` | ❌ W0 | ⬜ pending |
| 3-01-03 | 01 | 1 | RAG-03, RAG-04 | unit | `pytest tests/test_rag.py::test_history -x -q` | ❌ W0 | ⬜ pending |
| 3-02-01 | 02 | 2 | UI-01, UI-02 | manual | see Manual-Only | N/A | ⬜ pending |
| 3-02-02 | 02 | 2 | UI-03, UI-04, UI-05 | manual | see Manual-Only | N/A | ⬜ pending |
| 3-03-01 | 03 | 3 | PROMPT-01, PROMPT-02 | unit | `pytest tests/test_prompt.py -x -q` | ❌ W0 | ⬜ pending |
| 3-03-02 | 03 | 3 | PROMPT-03, PROMPT-04 | unit | `pytest tests/test_prompt.py -x -q` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_rag.py` — stubs for RAG-01, RAG-02, RAG-03, RAG-04
- [ ] `tests/test_prompt.py` — stubs for PROMPT-01, PROMPT-02, PROMPT-03, PROMPT-04
- [ ] `tests/conftest.py` — shared fixtures (mock vectorstore, mock Mistral responses)

*UI tests are manual-only (Streamlit rendering cannot be easily unit tested without a browser).*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Deux boutons de questions suggérées visibles au démarrage | UI-01 | Rendu Streamlit navigateur requis | `streamlit run app.py` → vérifier 2 boutons avant tout message |
| Cliquer bouton déclenche réponse RAG | UI-02 | Interaction navigateur | Cliquer bouton → vérifier réponse en français basée sur PDF |
| Historique visible toute la session | UI-03 | État visuel navigateur | Poser 3 questions → vérifier historique scrollable |
| Question de suivi cohérente | UI-04 | Jugement sémantique | "dis-m'en plus" après une réponse → vérifier cohérence contexte |
| Spinner pendant chargement | UI-05 | Rendu temporel | Poser question → vérifier spinner visible pendant réponse |
| Message erreur 429 en français | RAG-04 | Nécessite rate limit réel | Simuler 429 ou désactiver clé → vérifier message d'erreur affiché |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
