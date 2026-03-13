# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-13)

**Core value:** Un client potentiel peut poser n'importe quelle question sur le profil professionnel et obtenir une réponse précise et contextuelle directement depuis le document — sans avoir à lire le PDF en entier.
**Current focus:** Phase 1 — Setup & Configuration

## Current Position

Phase: 1 of 4 (Setup & Configuration)
Plan: 0 of TBD in current phase
Status: Ready to plan
Last activity: 2026-03-13 — Roadmap created

Progress: [░░░░░░░░░░] 0%

## Performance Metrics

**Velocity:**
- Total plans completed: 0
- Average duration: —
- Total execution time: —

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| - | - | - | - |

**Recent Trend:**
- Last 5 plans: —
- Trend: —

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [Roadmap]: FAISS local commité dans le repo Git (contrainte Streamlit Community Cloud — filesystem éphémère)
- [Roadmap]: `.streamlit/secrets.toml` dans `.gitignore` dès la Phase 1 — pitfall CRITIQUE à adresser avant tout code
- [Roadmap]: `config.py` centralise les constantes partagées entre `build_index.py` et `app.py` — en particulier le modèle d'embedding (incohérence = index inutilisable)

### Pending Todos

None yet.

### Blockers/Concerns

- [Phase 2]: Qualité du PDF source à valider — si `dossier_competence.pdf` contient des tableaux ou colonnes, `pypdf` peut produire une extraction dégradée. Valider avec les logs de chunks avant de continuer.
- [Phase 3]: Format de l'historique multi-tour pour `ChatMistralAI` (HumanMessage/AIMessage) — à vérifier lors de l'implémentation PROMPT-04.

## Session Continuity

Last session: 2026-03-13
Stopped at: Roadmap créée, prêt à planifier la Phase 1
Resume file: None
