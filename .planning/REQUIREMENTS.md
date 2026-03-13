# Requirements: Chatbot CV — Dossier de Compétences

**Defined:** 2026-03-13
**Core Value:** Un client potentiel peut poser n'importe quelle question sur le profil professionnel et obtenir une réponse précise et contextuelle directement depuis les documents — sans avoir à les lire en entier.

---

## v1 Requirements

### Setup & Configuration

- [x] **SETUP-01**: Le repo contient un `.gitignore` qui exclut `.streamlit/secrets.toml` et tout fichier de clé API
- [x] **SETUP-02**: Un fichier `config.py` centralise les constantes partagées entre `build_index.py` et `app.py` (nom du modèle d'embedding, chunk size, chunk overlap, nombre de chunks récupérés)
- [x] **SETUP-03**: Un fichier `requirements.txt` liste toutes les dépendances avec versions fixées (compatible Streamlit Community Cloud)

### Build de l'index

- [ ] **INDEX-01**: Le script `build_index.py` ingère tous les fichiers présents dans `assets/` (PDF et autres formats supportés) en une seule passe
- [ ] **INDEX-02**: Le script `build_index.py` génère un index FAISS local dans `faiss_index/` à partir des embeddings Mistral (`mistral-embed`)
- [ ] **INDEX-03**: L'index FAISS (`faiss_index/`) peut être commité dans le repo Git pour être disponible sur Streamlit Community Cloud
- [ ] **INDEX-04**: Le script affiche des logs de validation (nombre de chunks générés, aperçu des premiers chunks) pour permettre à l'utilisateur de vérifier la qualité de l'extraction avant de commiter l'index

### Pipeline RAG

- [ ] **RAG-01**: L'app charge l'index FAISS au démarrage et l'expose via `@st.cache_resource` (chargement unique, pas de rechargement à chaque re-run)
- [ ] **RAG-02**: À chaque question, l'app récupère les chunks les plus pertinents via similarity search FAISS (k configurable via `config.py`)
- [ ] **RAG-03**: L'app appelle le modèle Mistral (`mistral-small-latest`) avec les chunks récupérés comme contexte et l'historique de la session
- [ ] **RAG-04**: Tous les appels à l'API Mistral sont protégés par un `try/except` qui affiche un message d'erreur en français en cas de rate limit (HTTP 429) ou d'erreur réseau

### Interface Streamlit

- [ ] **UI-01**: L'interface présente une fenêtre de chat avec `st.chat_input` pour la saisie et `st.chat_message` pour l'affichage des messages
- [ ] **UI-02**: L'historique complet de la conversation est visible et persistent pendant toute la session via `st.session_state`
- [ ] **UI-03**: Au premier chargement (aucun message dans la session), deux boutons de questions suggérées sont affichés : "Quelles sont vos principales compétences ?" et "En quoi pouvez-vous m'aider sur mon projet ?"
- [ ] **UI-04**: Cliquer sur un bouton de question suggérée déclenche le pipeline RAG avec cette question (identique à une saisie manuelle)
- [ ] **UI-05**: Un spinner ou message d'attente est affiché pendant le chargement initial de l'index (cold start Streamlit Community Cloud)

### System Prompt & Comportement

- [ ] **PROMPT-01**: Le chatbot répond exclusivement en français, quelle que soit la langue de la question
- [ ] **PROMPT-02**: Le chatbot adopte un ton professionnel cohérent avec le profil présenté dans les documents
- [ ] **PROMPT-03**: Quand une question dépasse le contenu des documents, le chatbot répond explicitement qu'il ne dispose pas de cette information (pas d'hallucination)
- [ ] **PROMPT-04**: L'historique de la conversation est passé au LLM pour permettre les questions de suivi multi-tour ("dis-m'en plus", "et pour ce projet ?")

### Déploiement

- [ ] **DEPLOY-01**: L'app est déployée sur Streamlit Community Cloud et accessible publiquement sans authentification
- [ ] **DEPLOY-02**: La clé API Mistral est configurée dans les secrets du dashboard Streamlit Community Cloud (pas dans le code ni dans le repo)

---

## v2 Requirements

### Amélioration de l'index

- **INDEX-V2-01**: Support des formats non-PDF dans `assets/` (Word, Markdown, texte brut)
- **INDEX-V2-02**: Rebuild automatique de l'index au démarrage si un fichier `assets/` est plus récent que l'index (avec fallback sur l'index commité)

### UX avancée

- **UI-V2-01**: Streaming des réponses token par token (si Mistral free tier le supporte de façon fiable)
- **UI-V2-02**: Bouton "Nouvelle conversation" pour réinitialiser la session sans recharger l'app
- **UI-V2-03**: Questions suggérées supplémentaires ou personnalisables

### Observabilité

- **OBS-V2-01**: Logging des questions posées (sans données personnelles) pour améliorer le system prompt

---

## Out of Scope

| Feature | Raison |
|---------|--------|
| Affichage des sources/extraits dans les réponses | Décision explicite — ajoute du bruit pour l'audience B2B |
| Authentification / mot de passe | L'app est intentionnellement publique |
| Réponses multi-langue | Français uniquement — simplifier le system prompt |
| Historique persistant cross-sessions | Requiert une base de données, problèmes de privacy |
| PDF viewer intégré dans Streamlit | La page HTML existante le fait déjà |
| Rebuild FAISS automatique au démarrage | Complexité inutile pour des documents stables |

---

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| SETUP-01 | Phase 1 | Complete |
| SETUP-02 | Phase 1 | Complete |
| SETUP-03 | Phase 1 | Complete |
| INDEX-01 | Phase 2 | Pending |
| INDEX-02 | Phase 2 | Pending |
| INDEX-03 | Phase 2 | Pending |
| INDEX-04 | Phase 2 | Pending |
| RAG-01 | Phase 3 | Pending |
| RAG-02 | Phase 3 | Pending |
| RAG-03 | Phase 3 | Pending |
| RAG-04 | Phase 3 | Pending |
| UI-01 | Phase 3 | Pending |
| UI-02 | Phase 3 | Pending |
| UI-03 | Phase 3 | Pending |
| UI-04 | Phase 3 | Pending |
| UI-05 | Phase 3 | Pending |
| PROMPT-01 | Phase 3 | Pending |
| PROMPT-02 | Phase 3 | Pending |
| PROMPT-03 | Phase 3 | Pending |
| PROMPT-04 | Phase 3 | Pending |
| DEPLOY-01 | Phase 4 | Pending |
| DEPLOY-02 | Phase 4 | Pending |

**Coverage:**
- v1 requirements: 22 total
- Mapped to phases: 22
- Unmapped: 0

---

*Requirements defined: 2026-03-13*
*Last updated: 2026-03-13 — traceability filled after roadmap creation*
