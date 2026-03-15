---
phase: 02-build-de-l-index-faiss
plan: "01"
subsystem: infra
tags: [faiss, langchain, mistral, embeddings, rag, pdf, vector-store]

# Dependency graph
requires:
  - phase: 01-setup-configuration
    provides: config.py with EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP, FAISS_INDEX_PATH constants
provides:
  - build_index.py — offline script to build FAISS index from PDF source
  - faiss_index/index.faiss — binary FAISS vector index (20 chunks, mistral-embed)
  - faiss_index/index.pkl — chunk metadata (page_content + source metadata)
affects: [03-app-rag, app.py]

# Tech tracking
tech-stack:
  added: [langchain-community, langchain-mistralai, langchain-text-splitters, faiss-cpu, python-dotenv, pypdf]
  patterns: [offline index build script, load_dotenv before API client init, PyPDFDirectoryLoader with recursive=True, FAISS.save_local/load_local pattern]

key-files:
  created: [build_index.py, faiss_index/index.faiss, faiss_index/index.pkl]
  modified: []

key-decisions:
  - "build_index.py est un script offline — jamais importé par Streamlit, pas d'import streamlit"
  - "EMBEDDING_MODEL importé depuis config.py — valeur 'mistral-embed' jamais dupliquée dans build_index.py"
  - "faiss_index/ commité dans Git — requis pour Streamlit Community Cloud (filesystem éphémère)"
  - "load_dotenv() appelé avant MistralAIEmbeddings() — charge .env en dev local, no-op en prod"
  - "Guard 'if not raw_docs' avec message d'erreur explicite — évite des erreurs silencieuses"

patterns-established:
  - "Phase 3 (app.py) doit charger l'index avec allow_dangerous_deserialization=True (pickle)"
  - "Validation qualitative des chunks via logs avant tout commit de l'index"

requirements-completed: [INDEX-01, INDEX-02, INDEX-03, INDEX-04]

# Metrics
duration: 10min
completed: 2026-03-13
---

# Phase 2 Plan 01: Build FAISS Index Summary

**Pipeline offline load→split→embed→save avec PyPDFDirectoryLoader + mistral-embed + FAISS, produisant 20 chunks de texte français cohérent commités dans Git**

## Performance

- **Duration:** ~10 min
- **Started:** 2026-03-13T08:09:45Z
- **Completed:** 2026-03-13T09:53:00Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments

- Script `build_index.py` avec 4 étapes numérotées et logs de validation qualitatifs
- Index FAISS de 20 vecteurs (embeddings mistral-embed) depuis `assets/resume/dossier_competences.pdf`
- `faiss_index/` commité dans Git — prêt pour chargement par `app.py` en Phase 3

## Task Commits

Each task was committed atomically:

1. **Task 1: Créer build_index.py — pipeline complet load→split→embed→save** - `65f44e9` (feat)
2. **Task 2: Valider les chunks et commiter faiss_index/ dans Git** - `74ebed4` (feat)

## Files Created/Modified

- `build_index.py` — Script offline qui charge assets/, découpe en chunks, génère embeddings via mistral-embed, sauvegarde faiss_index/
- `faiss_index/index.faiss` — Index vectoriel binaire FAISS (81965 bytes, 20 vecteurs)
- `faiss_index/index.pkl` — Métadonnées des chunks (page_content + source metadata, 12589 bytes)

## Decisions Made

- `build_index.py` importe `EMBEDDING_MODEL` depuis `config.py` — garantit la cohérence entre build et query (divergence = résultats FAISS silencieusement invalides)
- `faiss_index/` intentionnellement absent de `.gitignore` — doit être commité pour Streamlit Community Cloud
- Validation qualitative des chunks via logs avant commit — texte français lisible confirmé (20 chunks, ~500 chars chacun)

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None — le PDF source `assets/resume/dossier_competences.pdf` produit une extraction pypdf de bonne qualité (texte français lisible, pas de mélange de colonnes). Les 20 chunks sont cohérents et dans les limites attendues (15-30).

## User Setup Required

**External services require manual configuration.**

- `MISTRAL_API_KEY` must be set in environment before running `build_index.py`
  - Source: console.mistral.ai → API Keys
  - Command: `export MISTRAL_API_KEY=sk-...`

This key is also required for Phase 3 (`app.py`) at runtime.

## Next Phase Readiness

- `faiss_index/index.faiss` et `faiss_index/index.pkl` présents et commités — Phase 3 peut charger l'index avec `FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)`
- `EMBEDDING_MODEL` dans `config.py` doit rester `"mistral-embed"` — identique entre build et query
- Aucun bloqueur pour Phase 3

## Self-Check: PASSED

- build_index.py: FOUND
- faiss_index/index.faiss: FOUND
- faiss_index/index.pkl: FOUND
- Commit 65f44e9 (build_index.py): FOUND
- Commit 74ebed4 (faiss_index/): FOUND

---
*Phase: 02-build-de-l-index-faiss*
*Completed: 2026-03-13*
