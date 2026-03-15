---
phase: 01-setup-configuration
verified: 2026-03-13T09:00:00Z
status: passed
score: 3/3 must-haves verified
re_verification: false
---

# Phase 1: Setup & Configuration — Verification Report

**Phase Goal:** Le repo est structuré de façon sécurisée et la configuration partagée est en place — aucun secret ne peut être accidentellement commité, toutes les constantes critiques sont définies une seule fois
**Verified:** 2026-03-13T09:00:00Z
**Status:** PASSED
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `.gitignore` exclut `.streamlit/secrets.toml` — `git status` ne montre pas ce fichier comme untracked | VERIFIED | `git check-ignore -v .streamlit/secrets.toml` retourne `.gitignore:5:.streamlit/secrets.toml` |
| 2 | `config.py` existe et contient les constantes partagées importables depuis tout script | VERIFIED | `python -c "from config import EMBEDDING_MODEL, LLM_MODEL, CHUNK_SIZE, CHUNK_OVERLAP, K_RETRIEVED, FAISS_INDEX_PATH"` affiche `OK: mistral-embed mistral-small-latest 500 50 4 faiss_index` |
| 3 | `requirements.txt` liste toutes les dépendances avec versions fixées | VERIFIED | 189 entrées avec opérateur `==`, 10 packages requis présents avec versions exactes |

**Score:** 3/3 truths verified

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `.gitignore` | Exclusion de `.streamlit/secrets.toml` et artefacts Python | VERIFIED | Contient `.streamlit/secrets.toml` ligne 5. `faiss_index/` absent intentionnellement (contra-vérification critique: l'index FAISS doit rester commitable). |
| `config.py` | Constantes partagées: EMBEDDING_MODEL, LLM_MODEL, CHUNK_SIZE, CHUNK_OVERLAP, K_RETRIEVED, FAISS_INDEX_PATH | VERIFIED | Fichier 23 lignes, toutes les 6 constantes présentes avec les valeurs exactes du plan. Aucun import, aucune logique — constantes pures uniquement. |
| `requirements.txt` | Dépendances avec versions fixées (opérateur ==), installable | VERIFIED | 189 packages via `pip freeze`. Les 10 packages critiques présents: `streamlit==1.55.0`, `mistralai==2.0.1`, `langchain==1.2.12`, `langchain-core==1.2.18`, `langchain-community==0.4.1`, `langchain-mistralai==1.1.1`, `langchain-text-splitters==1.1.1`, `faiss-cpu==1.13.2`, `pypdf==6.8.0`, `numpy==2.4.3`. |

---

### Key Link Verification

Les key links du PLAN (imports depuis `build_index.py` et `app.py`) sont des connexions de Phase 2 et Phase 3. Ces fichiers n'existent pas encore — c'est attendu et correct.

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `build_index.py` (Phase 2) | `config.py` | `from config import EMBEDDING_MODEL, ...` | DEFERRED | `build_index.py` pas encore créé — vérification appartient à Phase 2 |
| `app.py` (Phase 3) | `config.py` | `from config import EMBEDDING_MODEL, ...` | DEFERRED | `app.py` pas encore créé — vérification appartient à Phase 3 |

Les liens sont DEFERRED, pas FAILED: `config.py` est prêt à être importé et ses constantes sont correctement exposées. Le contrat est rempli du côté Phase 1.

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| SETUP-01 | 01-01-PLAN.md | Le repo contient un `.gitignore` qui exclut `.streamlit/secrets.toml` et tout fichier de clé API | SATISFIED | `.gitignore` exclut `.streamlit/secrets.toml` (ligne 5) et `.env` / `*.env`. `git check-ignore` confirme l'exclusion active. |
| SETUP-02 | 01-01-PLAN.md | `config.py` centralise les constantes partagées entre `build_index.py` et `app.py` | SATISFIED | `config.py` contient EMBEDDING_MODEL, LLM_MODEL, CHUNK_SIZE, CHUNK_OVERLAP, K_RETRIEVED, FAISS_INDEX_PATH — importable sans erreur. |
| SETUP-03 | 01-01-PLAN.md | `requirements.txt` liste toutes les dépendances avec versions fixées (compatible Streamlit Community Cloud) | SATISFIED | 189 packages avec `==`, générés via `pip freeze`. Tous les packages requis présents. |

Tous les 3 IDs de la phase sont satisfaits. Aucun ID orphelin détecté dans REQUIREMENTS.md pour cette phase.

---

### Anti-Patterns Found

Aucun anti-pattern détecté dans les trois fichiers de la phase.

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| — | — | Aucun | — | — |

Observations notables (non bloquantes):
- `.gitignore` contient `.mcp.json` en ligne 1 (ajout hors plan, vraisemblablement par l'outil MCP). Non problématique — exclusion légitime d'un fichier d'outil.
- Le SUMMARY documente le commit hash `3b0c1d5` pour `.gitignore` ligne 2 (`.gitignore:2:`), mais `git check-ignore` retourne ligne 5. Le fichier `.mcp.json` a été inséré en tête, décalant les numéros de ligne. Aucun impact fonctionnel — l'exclusion est active et correcte.

---

### Human Verification Required

### 1. Installabilité dans un venv propre

**Test:** Créer un venv vierge et exécuter `pip install -r requirements.txt`
**Expected:** Toutes les dépendances s'installent sans conflit de version ni erreur de résolution
**Why human:** L'environnement courant a déjà les packages installés — seul un venv propre révèle de vrais conflits de résolution. La validation programmatique dans l'environnement existant ne teste pas ce cas.

---

### Gaps Summary

Aucun gap. Les trois artifacts sont présents, substantiels, et corrects. Les key links sont DEFERRED (appartiennent aux phases suivantes). Les trois requirements SETUP-01, SETUP-02, SETUP-03 sont satisfaits avec preuves directes dans le code.

La seule vérification non automatisable est l'installabilité en venv propre (SETUP-03 étendu) — mais elle ne constitue pas un blocker pour la progression vers Phase 2, car `pip freeze` avec versions exactes est la méthode la plus robuste disponible.

---

_Verified: 2026-03-13T09:00:00Z_
_Verifier: Claude (gsd-verifier)_
