# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v1.0 — MVP

**Shipped:** 2026-03-15
**Phases:** 4 | **Plans:** 5 | **Sessions:** ~3

### What Was Built
- Infrastructure sécurisée : `config.py` centralisé, `.gitignore` API-safe, `requirements.txt` 189 packages fixés
- Pipeline RAG offline : `build_index.py` + `faiss_index/` (20 chunks, mistral-embed) commité dans git
- App Streamlit `app.py` (102 lignes) — chat multi-tour, questions suggérées, gestion erreur 429
- Déploiement public sur Streamlit Community Cloud avec `requirements-app.txt` minimal (7 packages)

### What Worked
- Séparation claire build offline / app runtime — aucune dépendance Streamlit dans `build_index.py`
- `config.py` centralisé a évité une classe de bugs silencieux (EMBEDDING_MODEL divergence)
- `requirements-app.txt` séparé de `requirements.txt` : déploiement propre sans friction
- Le plan "Wave 0 tests first" (Phase 3-01) a rendu l'implémentation de `app.py` guidée et rapide
- Checkpoint humain pour le déploiement bien géré — les étapes manuelles Streamlit Cloud étaient claires

### What Was Inefficient
- Les SUMMARY.md des phases 01, 02 et 04 n'ont pas de `one_liner` parsable par gsd-tools (champ manquant) — MILESTONES.md généré automatiquement était vide
- Le `curl -sI` de vérification post-déploiement a retourné 303 (redirect Streamlit normal) ce qui a créé une fausse alerte — le comportement est attendu pour les apps Streamlit publiques

### Patterns Established
- **`requirements-app.txt` minimal** : toujours séparer les dépendances prod des dépendances dev pour Streamlit Cloud
- **faiss_index/ dans git** : obligatoire pour tout hébergement à filesystem éphémère
- **EMBEDDING_MODEL dans config.py** : un seul endroit pour éviter la divergence silencieuse build/app
- **Checkpoint humain pour déploiement** : les étapes qui nécessitent un dashboard web tiers sont correctement modélisées comme `autonomous: false`

### Key Lessons
1. Streamlit Community Cloud retourne HTTP 303 (redirect session) même pour les apps publiques — ne pas interpréter ça comme un mur d'auth, vérifier en navigation privée
2. Les champs `one_liner` dans les SUMMARY.md sont importants pour que gsd-tools puisse extraire automatiquement les accomplishments — s'assurer que les agents les remplissent

### Cost Observations
- Model mix: 100% sonnet
- Sessions: ~3 sessions
- Notable: Pipeline très linéaire (4 phases séquentielles), peu de retravail — bonne définition initiale des requirements

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Phases | Plans | Key Change |
|-----------|--------|-------|------------|
| v1.0 | 4 | 5 | Premier projet GSD — workflow établi |

### Cumulative Quality

| Milestone | Tests | Coverage | Notes |
|-----------|-------|----------|-------|
| v1.0 | 8 stubs pytest | — | Tests infrastructure Wave 0 (RAG + PROMPT) |

### Top Lessons (Verified Across Milestones)

1. Séparer les dépendances prod/dev dès le début évite les frictions au déploiement
2. Centraliser les constantes critiques (ex: EMBEDDING_MODEL) dans un seul fichier prévient les bugs silencieux
