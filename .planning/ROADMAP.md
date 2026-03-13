# Roadmap: Chatbot CV — Dossier de Compétences

## Overview

Quatre phases livrent un chatbot RAG fonctionnel et public : d'abord sécuriser l'infrastructure (secrets, config partagée), puis construire et valider l'index FAISS offline, ensuite assembler l'application Streamlit complète avec le pipeline RAG, le system prompt et l'interface conversationnelle, et enfin déployer publiquement sur Streamlit Community Cloud.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

- [ ] **Phase 1: Setup & Configuration** - Repo sécurisé, dépendances fixées, constantes partagées en place
- [ ] **Phase 2: Build de l'index FAISS** - Script d'indexation validé, index commité dans le repo
- [ ] **Phase 3: Application Streamlit complète** - Pipeline RAG + UI + system prompt fonctionnels en local
- [ ] **Phase 4: Déploiement** - App publique accessible sur Streamlit Community Cloud

## Phase Details

### Phase 1: Setup & Configuration
**Goal**: Le repo est structuré de façon sécurisée et la configuration partagée est en place — aucun secret ne peut être accidentellement commité, toutes les constantes critiques sont définies une seule fois
**Depends on**: Nothing (first phase)
**Requirements**: SETUP-01, SETUP-02, SETUP-03
**Success Criteria** (what must be TRUE):
  1. `.gitignore` exclut `.streamlit/secrets.toml` — un `git status` après création du fichier de secrets ne montre pas ce fichier comme "untracked"
  2. `config.py` existe et contient les constantes partagées (modèle embedding, chunk size, chunk overlap, k) importables depuis tout script
  3. `requirements.txt` liste toutes les dépendances avec versions fixées et est installable via `pip install -r requirements.txt` sans erreur
**Plans**: TBD

### Phase 2: Build de l'index FAISS
**Goal**: L'index vectoriel est construit depuis le PDF source, validé qualitativement, et commité dans le repo — prêt à être chargé par l'app Streamlit
**Depends on**: Phase 1
**Requirements**: INDEX-01, INDEX-02, INDEX-03, INDEX-04
**Success Criteria** (what must be TRUE):
  1. `python build_index.py` s'exécute sans erreur et crée le dossier `faiss_index/`
  2. Le script affiche le nombre de chunks générés et un aperçu des premiers chunks — l'utilisateur peut vérifier que le texte est lisible et bien découpé
  3. `faiss_index/` peut être commité dans Git et est présent dans le repo après commit
**Plans**: TBD

### Phase 3: Application Streamlit complète
**Goal**: L'application tourne en local — un utilisateur peut poser une question, obtenir une réponse contextualisée en français depuis le document, suivre une conversation multi-tour, et voir les questions suggérées au démarrage
**Depends on**: Phase 2
**Requirements**: RAG-01, RAG-02, RAG-03, RAG-04, UI-01, UI-02, UI-03, UI-04, UI-05, PROMPT-01, PROMPT-02, PROMPT-03, PROMPT-04
**Success Criteria** (what must be TRUE):
  1. L'app se charge sans erreur (`streamlit run app.py`) et affiche deux boutons de questions suggérées avant le premier message
  2. Cliquer sur un bouton ou saisir une question déclenche une réponse en français basée sur le contenu du PDF (pas d'hallucination hors-scope — le chatbot dit explicitement qu'il ne dispose pas de l'information)
  3. L'historique de la conversation reste visible pendant toute la session et les questions de suivi ("dis-m'en plus") obtiennent des réponses cohérentes avec le contexte précédent
  4. En cas de rate limit Mistral (HTTP 429), un message d'erreur en français s'affiche — l'app ne plante pas silencieusement
**Plans**: TBD

### Phase 4: Déploiement
**Goal**: L'app est publiquement accessible sur Streamlit Community Cloud sans authentification — n'importe qui avec le lien peut l'utiliser
**Depends on**: Phase 3
**Requirements**: DEPLOY-01, DEPLOY-02
**Success Criteria** (what must be TRUE):
  1. L'URL Streamlit Community Cloud répond sans login et affiche l'interface de chat
  2. La clé API Mistral n'apparaît pas dans le code source ni dans l'historique Git — elle est configurée exclusivement via les secrets du dashboard Streamlit
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Setup & Configuration | 0/TBD | Not started | - |
| 2. Build de l'index FAISS | 0/TBD | Not started | - |
| 3. Application Streamlit complète | 0/TBD | Not started | - |
| 4. Déploiement | 0/TBD | Not started | - |
