---
phase: 01-setup-configuration
plan: 01
subsystem: infra
tags: [python, streamlit, mistral, langchain, faiss, gitignore, config, requirements]

# Dependency graph
requires: []
provides:
  - .gitignore avec exclusion .streamlit/secrets.toml (sécurité clé API)
  - config.py avec constantes partagées (EMBEDDING_MODEL, LLM_MODEL, CHUNK_SIZE, CHUNK_OVERLAP, K_RETRIEVED, FAISS_INDEX_PATH)
  - requirements.txt avec 189 dépendances fixées via pip freeze
affects:
  - 02-build-index (uses config.py + requirements.txt)
  - 03-app (uses config.py + requirements.txt)
  - 04-deploy (uses requirements.txt for Streamlit Community Cloud)

# Tech tracking
tech-stack:
  added: [streamlit==1.55.0, mistralai==2.0.1, langchain==1.2.12, langchain-core==1.2.18, langchain-community==0.4.1, langchain-mistralai==1.1.1, langchain-text-splitters==1.1.1, faiss-cpu==1.13.2, pypdf==6.8.0, numpy==2.4.3]
  patterns: [centralized config module, pip freeze for reproducibility, .streamlit/secrets.toml for API key management]

key-files:
  created:
    - .gitignore
    - config.py
    - requirements.txt
  modified: []

key-decisions:
  - "EMBEDDING_MODEL = mistral-embed dans config.py — doit être identique entre build_index.py et app.py (divergence = résultats FAISS silencieusement invalides)"
  - "faiss_index/ intentionnellement absent de .gitignore — doit être commité pour Streamlit Community Cloud (filesystem éphémère)"
  - "pip freeze complet (189 packages) plutôt que liste minimale — reproductibilité garantie sur Streamlit Community Cloud"
  - "CHUNK_SIZE=500, CHUNK_OVERLAP=50 — calibrés pour document court et dense, ajustables en Phase 2 selon qualité des chunks"

patterns-established:
  - "Import pattern: from config import EMBEDDING_MODEL, ... — centralise les constantes, évite la duplication"
  - "Secrets pattern: .streamlit/secrets.toml (jamais commité) + st.secrets en runtime"

requirements-completed: [SETUP-01, SETUP-02, SETUP-03]

# Metrics
duration: 3min
completed: 2026-03-13
---

# Phase 1 Plan 01: Setup & Configuration Summary

**Socle de configuration complet: .gitignore (secrets exclus), config.py (constantes FAISS/Mistral partagées), requirements.txt (189 packages fixés via pip freeze)**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-13T08:00:32Z
- **Completed:** 2026-03-13T08:03:34Z
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments

- `.gitignore` exclut `.streamlit/secrets.toml` — clé API Mistral ne peut pas être commitée accidentellement. `faiss_index/` intentionnellement absent pour rester commitable.
- `config.py` centralise 6 constantes critiques: `EMBEDDING_MODEL`, `LLM_MODEL`, `CHUNK_SIZE`, `CHUNK_OVERLAP`, `K_RETRIEVED`, `FAISS_INDEX_PATH` — importable depuis `build_index.py` et `app.py` sans modification du PYTHONPATH.
- `requirements.txt` généré via `pip freeze` avec 189 packages et versions exactes (opérateur `==`) — reproductible sur Streamlit Community Cloud.

## Task Commits

Each task was committed atomically:

1. **Task 1: Créer .gitignore** — `3b0c1d5` (chore)
2. **Task 2: Créer config.py** — `05e6a95` (feat)
3. **Task 3: Créer requirements.txt** — `645ff16` (chore)

## Files Created/Modified

- `.gitignore` — Exclusion `.streamlit/secrets.toml`, artefacts Python, venv, IDE. `faiss_index/` absent intentionnellement.
- `config.py` — 6 constantes partagées: `EMBEDDING_MODEL="mistral-embed"`, `LLM_MODEL="mistral-small-latest"`, `CHUNK_SIZE=500`, `CHUNK_OVERLAP=50`, `K_RETRIEVED=4`, `FAISS_INDEX_PATH="faiss_index"`
- `requirements.txt` — 189 packages avec versions exactes. Top 10: `streamlit==1.55.0`, `mistralai==2.0.1`, `langchain==1.2.12`, `langchain-core==1.2.18`, `langchain-community==0.4.1`, `langchain-mistralai==1.1.1`, `langchain-text-splitters==1.1.1`, `faiss-cpu==1.13.2`, `pypdf==6.8.0`, `numpy==2.4.3`

## Decisions Made

- `EMBEDDING_MODEL = "mistral-embed"` dans `config.py` — valeur critique qui doit être identique entre build (Phase 2) et query (Phase 3). Une divergence produirait des résultats FAISS silencieusement invalides.
- `faiss_index/` absent de `.gitignore` — l'index FAISS doit pouvoir être commité pour être disponible sur Streamlit Community Cloud (filesystem éphémère).
- `pip freeze` complet (189 packages) retenu plutôt qu'une liste minimale — garantit la reproductibilité exacte sur Streamlit Community Cloud.
- `CHUNK_SIZE=500`, `CHUNK_OVERLAP=50` — calibrés pour un document court et dense. Ajustable en Phase 2 après validation de la qualité des chunks via les logs.

## Verification Results

1. **Sécurité secrets:** `git check-ignore -v .streamlit/secrets.toml` → `.gitignore:5:.streamlit/secrets.toml` (PASS)
2. **Importabilité config:** `from config import EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP, K_RETRIEVED, FAISS_INDEX_PATH` → `config OK` (PASS)
3. **Intégrité requirements:** `pip install -r requirements.txt --quiet` → `requirements OK` (PASS)
4. **Contre-vérification gitignore:** `faiss_index/` créé temporairement → visible dans `git status` comme untracked (PASS — non exclu, commitable)

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None — la configuration des secrets (`MISTRAL_API_KEY`) sera nécessaire lors du déploiement sur Streamlit Community Cloud (Phase 4), pas dans cette phase.

## Next Phase Readiness

- Phase 2 (`build_index.py`) peut importer directement depuis `config.py` via `from config import EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP, K_RETRIEVED, FAISS_INDEX_PATH`
- Phase 3 (`app.py`) peut importer identiquement
- Toutes les dépendances sont installées et testées dans l'environnement courant
- Blocker Phase 2 documenté dans STATE.md: qualité du PDF `dossier_competence.pdf` à valider (tableaux/colonnes peuvent dégrader l'extraction pypdf)

---
*Phase: 01-setup-configuration*
*Completed: 2026-03-13*

## Self-Check: PASSED

- FOUND: .gitignore
- FOUND: config.py
- FOUND: requirements.txt
- FOUND: .planning/phases/01-setup-configuration/01-01-SUMMARY.md
- FOUND commit 3b0c1d5 (Task 1: .gitignore)
- FOUND commit 05e6a95 (Task 2: config.py)
- FOUND commit 645ff16 (Task 3: requirements.txt)
