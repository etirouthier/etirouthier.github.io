---
gsd_state_version: 1.0
milestone: v1.2
milestone_name: Métadonnées d'expérience
status: Roadmap défini, prêt pour plan-phase 7
stopped_at: Checkpoint Task 3 — awaiting FAISS rebuild with MISTRAL_API_KEY
last_updated: "2026-03-16T17:27:48.930Z"
last_activity: 2026-03-16 — Milestone v1.2 démarré
progress:
  total_phases: 1
  completed_phases: 1
  total_plans: 1
  completed_plans: 1
  percent: 0
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-16)

**Core value:** Un client potentiel peut poser n'importe quelle question sur le profil professionnel et obtenir une réponse précise et contextuelle directement depuis le document.
**Current focus:** v1.2 — Métadonnées d'expérience

## Current Position

Phase: Phase 7 — Métadonnées & Contexte LLM (not started)
Plan: —
Status: Roadmap défini, prêt pour plan-phase 7
Last activity: 2026-03-16 — Milestone v1.2 démarré

Progress: [░░░░░░░░░░] 0%

## Accumulated Context

### Decisions

- [v1.2]: Metadata `experience` ajoutée via mapping dict explicite dans build_index.py — inférence fragile sur filename évitée
- [v1.2]: Contexte LLM labellisé `[Expérience]\n<chunk>` — filtrage FAISS par expérience hors périmètre
- [Phase 07-metadonnees-contexte-llm]: EXPERIENCE_MAP uses os.path.basename as key — robust to absolute paths stored by LangChain
- [Phase 07-metadonnees-contexte-llm]: Labelled RAG context f'[{experience}]\n{chunk}' format adopted — no FAISS metadata filtering needed

### Pending Todos

None.

### Blockers/Concerns

None.

## Session Continuity

Last session: 2026-03-16T17:27:48.928Z
Stopped at: Checkpoint Task 3 — awaiting FAISS rebuild with MISTRAL_API_KEY
Resume file: None
