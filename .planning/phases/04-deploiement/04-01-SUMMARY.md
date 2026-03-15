---
phase: 04-deploiement
plan: 01
subsystem: infra
tags: [streamlit, streamlit-cloud, faiss, mistral, deployment]

# Dependency graph
requires:
  - phase: 03-application-streamlit-complete
    provides: app.py Streamlit chatbot complet avec FAISS + Mistral
  - phase: 02-build-de-l-index-faiss
    provides: faiss_index/ commité dans git (index.faiss + index.pkl)
provides:
  - URL publique https://etirouthierappio.streamlit.app/
  - requirements-app.txt minimal pour Streamlit Community Cloud
  - App déployée accessible sans authentification (vérifiée en navigation privée)
affects: []

# Tech tracking
tech-stack:
  added: [streamlit-community-cloud]
  patterns: [requirements-app.txt séparé du requirements.txt complet de développement, secrets via st.secrets dashboard Streamlit Cloud]

key-files:
  created:
    - requirements-app.txt
    - .planning/phases/04-deploiement/04-01-SUMMARY.md
  modified: []

key-decisions:
  - "requirements-app.txt (7 packages) créé séparément de requirements.txt (189 packages) — Streamlit Cloud installe uniquement les dépendances nécessaires à l'exécution de app.py"
  - "MISTRAL_API_KEY configurée via Advanced Settings → Secrets dans le dashboard Streamlit Cloud — jamais dans le code commité"
  - "URL déployée : https://etirouthierappio.streamlit.app/"

patterns-established:
  - "Pattern deployment: requirements-app.txt minimal distinct de requirements.txt dev-complet"
  - "Pattern secrets: st.secrets['MISTRAL_API_KEY'] lu depuis le dashboard Streamlit Cloud, jamais en clair dans le repo"

requirements-completed: [DEPLOY-01, DEPLOY-02]

# Metrics
duration: ~30min (incluant attente build Streamlit Cloud)
completed: 2026-03-15
---

# Phase 4 Plan 01: Deploiement Streamlit Community Cloud Summary

**Chatbot CV déployé publiquement sur https://etirouthierappio.streamlit.app/ avec FAISS local et MISTRAL_API_KEY sécurisée via le dashboard Streamlit Cloud**

## Performance

- **Duration:** ~30 min (incluant attente du premier build Streamlit Cloud)
- **Started:** 2026-03-15
- **Completed:** 2026-03-15
- **Tasks:** 2
- **Files modified:** 1 (requirements-app.txt créé)

## Accomplishments

- requirements-app.txt créé avec 7 packages minimaux (vs 189 dans requirements.txt complet)
- App déployée et accessible publiquement à https://etirouthierappio.streamlit.app/
- MISTRAL_API_KEY configurée via le dashboard Streamlit Cloud (secrets), jamais dans le code commité
- Interface de chat visible et fonctionnelle vérifiée en navigation privée

## Task Commits

Chaque tâche a été commitée atomiquement :

1. **Task 1: Créer requirements-app.txt minimal et vérifier la readiness git** - `871d982` (chore)
2. **Task 2: Déployer sur Streamlit Community Cloud** - déploiement manuel via dashboard (checkpoint:human-action — aucun commit automatisé possible)

**Plan metadata:** (commit docs — voir commit final)

## Files Created/Modified

- `requirements-app.txt` — Dépendances minimales pour Streamlit Community Cloud : streamlit, langchain-mistralai, langchain-community, langchain-core, faiss-cpu, pypdf, python-dotenv

## Decisions Made

- **requirements-app.txt séparé :** Le requirements.txt contient 189 packages (environnement codespace complet). Streamlit Cloud installe tout ce qui est listé — un fichier minimal évite les échecs mémoire et accélère les builds.
- **MISTRAL_API_KEY via dashboard :** Configurée dans Advanced Settings → Secrets du dashboard Streamlit Cloud. Lue via `st.secrets["MISTRAL_API_KEY"]` dans app.py. Jamais dans le code ni dans les fichiers commités.
- **URL finale :** https://etirouthierappio.streamlit.app/ (format username+repo Streamlit Cloud)

## Deviations from Plan

None — le plan a été exécuté exactement comme écrit. La Task 1 automatisée et la Task 2 checkpoint:human-action se sont déroulées sans déviations.

## Vérifications Post-Déploiement

```
git ls-files faiss_index/
faiss_index/index.faiss
faiss_index/index.pkl
# PASS — 2 fichiers commités

git grep -rn "sk-" -- '*.py' '*.toml'
build_index.py:4:#   export MISTRAL_API_KEY=sk-...
# ACCEPTABLE — commentaire uniquement, pas une valeur hardcodée

curl -I https://etirouthierappio.streamlit.app/ → HTTP/2 303
# EXPECTED — Streamlit Cloud redirige vers son portail d'auth interne
# L'utilisateur a confirmé accès public en navigation privée — interface visible et fonctionnelle
```

## User Setup Required

La MISTRAL_API_KEY a été configurée manuellement via le dashboard Streamlit Cloud :
- https://share.streamlit.io → app settings → Advanced → Secrets
- Format TOML : `MISTRAL_API_KEY = "sk-..."`

Aucune autre configuration externe requise.

## Next Phase Readiness

Phase 4 (Déploiement) complète — c'est la dernière phase du projet. Le chatbot CV est :
- Déployé publiquement à https://etirouthierappio.streamlit.app/
- Accessible sans authentification (vérifié en navigation privée)
- MISTRAL_API_KEY sécurisée via les secrets Streamlit Cloud
- Index FAISS disponible au clone (commité dans git)

Le projet est en production. Aucune phase suivante planifiée.

---
*Phase: 04-deploiement*
*Completed: 2026-03-15*
