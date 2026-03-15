# Milestones

## v1.0 MVP (Shipped: 2026-03-15)

**Phases completed:** 4 phases, 5 plans, 0 tasks

**Key accomplishments:**
- Config centralisée (`config.py`), secrets sécurisés (`.gitignore`), stack fixée (189 deps)
- Index FAISS construit offline depuis `dossier_competence.pdf` — 20 chunks mistral-embed, commité dans git
- Infrastructure de tests pytest (conftest, fixtures mock LangChain) pour le pipeline RAG
- `app.py` (102 lignes) — chat multi-tour, questions suggérées, RAG pipeline, gestion erreur 429
- Déployé publiquement sur https://etirouthierappio.streamlit.app/ avec `requirements-app.txt` minimal (7 packages)

---

