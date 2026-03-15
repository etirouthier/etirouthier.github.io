---
phase: 04-deploiement
verified: 2026-03-15T00:00:00Z
status: human_needed
score: 3/4 must-haves verified (1 requires human confirmation)
re_verification: false
human_verification:
  - test: "Visiter https://etirouthierappio.streamlit.app/ en navigation privée"
    expected: "L'interface de chat 'Assistant — Dossier de Compétences' est visible, les deux boutons de questions suggérées apparaissent, et poser une question génère une réponse en français cohérente avec le profil"
    why_human: "L'accès public sans authentification et la fonctionnalité complète du pipeline RAG (FAISS + Mistral) ne peuvent être confirmés que via un navigateur — curl retourne HTTP 303 (redirect de session init Streamlit, non un blocage d'auth), et l'utilisateur a déjà confirmé l'accès en incognito"
---

# Phase 4 — Déploiement: Verification Report

**Phase Goal:** Déployer l'application Streamlit sur Streamlit Community Cloud et la rendre publiquement accessible.
**Verified:** 2026-03-15
**Status:** human_needed — tous les checks automatisés passent, confirmation humaine déjà fournie pour l'accès public
**Re-verification:** Non — vérification initiale

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | L'URL Streamlit Community Cloud répond sans authentification | ? HUMAN | curl retourne HTTP 303 (session init normale Streamlit) — utilisateur a confirmé accès public en navigation privée |
| 2 | L'interface de chat est visible et fonctionnelle via navigateur | ? HUMAN | Confirmé par l'utilisateur en navigation privée — vérification programmatique impossible (browser-only) |
| 3 | MISTRAL_API_KEY n'apparaît pas comme valeur dans aucun fichier commité | VERIFIED | `build_index.py:4` contient uniquement un commentaire shell `#   export MISTRAL_API_KEY=sk-...` — jamais une valeur hardcodée. Aucune occurrence dans `*.py` ni `*.toml` autres que commentaires. |
| 4 | faiss_index/ est commité dans git et disponible au clone | VERIFIED | `git ls-files faiss_index/` retourne `faiss_index/index.faiss` et `faiss_index/index.pkl` — 2 fichiers présents et trackés |

**Score:** 2/4 vérifiés automatiquement + 2/4 confirmés humainement = 4/4 objectifs atteints selon la confirmation utilisateur

---

## Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `requirements-app.txt` | Dépendances minimales pour Streamlit Community Cloud | VERIFIED | 7 packages : `streamlit==1.55.0`, `langchain-mistralai==1.1.1`, `langchain-community==0.4.1`, `langchain-core==1.2.18`, `faiss-cpu==1.13.2`, `pypdf==6.8.0`, `python-dotenv==1.2.2` — contenu exact conforme au plan |
| `faiss_index/index.faiss` | Index FAISS binaire | VERIFIED | Présent sur disque (81965 bytes) et tracké dans git |
| `faiss_index/index.pkl` | Métadonnées FAISS | VERIFIED | Présent sur disque (12589 bytes) et tracké dans git |

---

## Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `requirements-app.txt` | Streamlit Cloud installer | `pip install -r requirements-app.txt` au build | VERIFIED | Pattern `streamlit\|langchain\|faiss` présent — toutes les dépendances nécessaires listées avec versions fixées |
| `app.py` | `MISTRAL_API_KEY` secret | Streamlit Cloud dashboard → env var → LangChain | VERIFIED (avec note) | `app.py` ne contient pas `st.secrets["MISTRAL_API_KEY"]` explicitement — `MistralAIEmbeddings` et `ChatMistralAI` (LangChain) lisent `MISTRAL_API_KEY` directement depuis l'environnement. Streamlit Cloud injecte automatiquement les secrets du dashboard dans l'environnement du process. Résultat fonctionnel identique — la clé n'est jamais dans le code. Note: la RESEARCH.md anticipait un pattern `st.secrets["MISTRAL_API_KEY"]` explicite qui n'a pas été implémenté, mais le mécanisme alternatif est équivalent et plus idiomatique pour LangChain. |

---

## Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| DEPLOY-01 | 04-01-PLAN.md | L'app est déployée sur Streamlit Community Cloud et accessible publiquement sans authentification | VERIFIED (human) | URL https://etirouthierappio.streamlit.app/ accessible en navigation privée — confirmé par l'utilisateur. Commit `871d982` + `a249ae7` dans git. |
| DEPLOY-02 | 04-01-PLAN.md | La clé API Mistral est configurée dans les secrets du dashboard Streamlit Community Cloud (pas dans le code ni dans le repo) | VERIFIED | `git grep -rn "sk-" -- '*.py' '*.toml'` retourne uniquement un commentaire shell dans `build_index.py:4`. `app.py` utilise LangChain qui lit `MISTRAL_API_KEY` depuis l'env — injectée par Streamlit Cloud depuis le dashboard. `.streamlit/secrets.toml` exclu par `.gitignore`. |

**Requirements orphelins:** Aucun — DEPLOY-01 et DEPLOY-02 sont les seuls requirements Phase 4 dans REQUIREMENTS.md et les deux sont couverts par 04-01-PLAN.md.

---

## Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `build_index.py` | 4 | `# export MISTRAL_API_KEY=sk-...` | ℹ️ Info | Commentaire de documentation shell — valeur fictive (`sk-...`), pas une vraie clé. Acceptable. |

Aucun blocker ni warning identifié.

---

## Human Verification Required

### 1. Accès public et fonctionnalité de l'app déployée

**Test:** Ouvrir https://etirouthierappio.streamlit.app/ dans un navigateur en navigation privée (incognito). Vérifier :
1. Le titre "Assistant — Dossier de Compétences" est visible
2. Les deux boutons apparaissent : "Quelles sont vos principales compétences ?" et "En quoi pouvez-vous m'aider sur mon projet ?"
3. Cliquer sur l'un des boutons déclenche le pipeline RAG et génère une réponse en français
4. Aucun écran de login ou authentification requis

**Expected:** Accès immédiat à l'interface de chat, réponse cohérente avec le profil basée sur le FAISS index.

**Why human:** curl retourne HTTP 303 (redirect de session init Streamlit — comportement normal, pas un blocage d'auth). La vérification de l'interface et du pipeline RAG complet nécessite un navigateur. L'utilisateur a déjà confirmé cet accès en navigation privée lors de l'exécution de la phase — cette section documente le besoin de re-confirmation formelle si nécessaire.

---

## Gaps Summary

Aucun gap bloquant identifié. Tous les artefacts existent, sont substantiels, et correctement connectés :

- `requirements-app.txt` créé avec exactement les 7 packages nécessaires
- `faiss_index/` (index.faiss + index.pkl) commité et disponible au clone
- `.streamlit/secrets.toml` exclu du repo par `.gitignore`
- MISTRAL_API_KEY jamais présente en clair dans les fichiers commités
- App déployée et accessible publiquement selon confirmation utilisateur

La seule nuance technique : `app.py` ne contient pas `st.secrets["MISTRAL_API_KEY"]` explicitement (tel qu'anticipé dans la RESEARCH.md et le plan), mais délègue la lecture de la clé à LangChain via la variable d'environnement, ce que Streamlit Cloud peuple depuis les secrets du dashboard. Ce pattern est fonctionnellement équivalent et ne constitue pas un gap — DEPLOY-02 est satisfait.

---

_Verified: 2026-03-15_
_Verifier: Claude (gsd-verifier)_
