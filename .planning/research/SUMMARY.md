# Project Research Summary

**Project:** RAG Chatbot CV — Portfolio Professionnel
**Domain:** RAG chatbot portfolio/CV (showcase professionnel B2B)
**Researched:** 2026-03-13
**Confidence:** MEDIUM-HIGH

## Executive Summary

Ce projet est un chatbot RAG (Retrieval-Augmented Generation) déployé comme portfolio professionnel interactif. L'approche standard pour ce type d'application repose sur trois composants clairs : un vectorstore local (FAISS) construit offline depuis un PDF, un LLM hébergé (Mistral) pour la génération de réponses, et une interface conversationnelle Streamlit déployée sur Streamlit Community Cloud. La recherche confirme que ce stack est bien documenté, libre de coût, et adapté à l'échelle d'un seul document PDF.

L'approche recommandée est de séparer strictement deux chemins d'exécution : le build de l'index (offline, manuel, lancé une fois après chaque mise à jour du PDF) et la query runtime (Streamlit app). L'index FAISS doit être commité dans le repo Git — contrainte non négociable imposée par le filesystem éphémère de Streamlit Community Cloud. Le MVP est estimé à 8-12h de travail focalisé, avec une priorité claire : core RAG fonctionnel avant tout polish UI.

Le risque principal n'est pas technique mais opérationnel : plusieurs pitfalls critiques surviennent au moment du setup (clé API exposée, index absent) plutôt que pendant le développement. Ces décisions doivent être prises avant d'écrire la première ligne de code. Le free tier Mistral impose une gestion explicite des erreurs 429 — sans quoi l'app plante silencieusement en démo.

---

## Key Findings

### Recommended Stack

Le stack est homogène autour de l'écosystème LangChain >=0.2 et Mistral. LangChain Expression Language (LCEL) remplace l'ancienne `RetrievalQA` — ne pas utiliser les patterns legacy. Le SDK `mistralai` >=1.0.0 a subi une réécriture majeure mi-2024 ; utiliser cette version ou `langchain-mistralai` pour l'intégration LangChain. `PyPDF2` est déprécié — utiliser `pypdf` >=4.0.0.

**Core technologies:**
- `streamlit` >=1.35.0 : framework UI et hébergement — natif Streamlit Community Cloud, chat UI intégré
- `mistralai` >=1.0.0 + `langchain-mistralai` >=0.1.0 : LLM et embeddings — SDK officiel, free tier disponible
- `faiss-cpu` >=1.8.0 : vectorstore local — zéro coût, adapté à un seul PDF, pas besoin de service externe
- `pypdf` >=4.0.0 : parsing PDF — actif et maintenu (remplace PyPDF2 déprécié)
- `langchain` >=0.2.0 + `langchain-core` + `langchain-community` : orchestration RAG via LCEL
- Python 3.11 : version stable, compatibilité garantie avec tout le stack

### Expected Features

**Must have (table stakes) :**
- Réponses basées sur le contenu du PDF — promesse core du produit
- Réponses en français — audience B2B, enforced via system prompt
- Interface conversationnelle (`st.chat_input`) — UI de base attendue
- Historique de conversation visible (`st.session_state`) — l'utilisateur doit voir l'échange
- Questions de démarrage suggérées — réduit l'angoisse de la page blanche
- Fallback gracieux hors-scope — ne pas halluciner, system prompt géré

**Should have (différenciateurs) :**
- Suivi multi-tour (historique passé au LLM) — "dis-m'en plus" sans reformuler
- Ton persona-consistent — les réponses sonnent comme le professionnel, pas comme un AI générique
- Réponse rapide < 3s — minimiser les chunks passés au modèle
- "Je ne sais pas" honnête — plus de confiance qu'un AI qui invente

**Defer (v2+) :**
- Streaming token — complexité supplémentaire, Mistral free tier moins fiable en streaming
- Historique multi-tour passé au LLM — commencer sans, ajouter après le core fonctionnel
- Fallback rebuild FAISS au démarrage — complexité infra inutile pour un PDF stable

**Anti-features explicites (ne jamais construire) :**
- Affichage des sources/extraits — décision explicite, ajoute du bruit pour l'audience B2B
- Authentification — tue la conversion
- Multi-langue — double la complexité du prompt
- Historique persistant cross-sessions — requiert BDD, problèmes de privacy

### Architecture Approach

L'architecture repose sur deux chemins d'exécution indépendants : `build_index.py` (offline, lance manuellement) construit l'index FAISS depuis le PDF et le commit dans le repo ; `app.py` (runtime Streamlit) charge cet index via `@st.cache_resource` et orchestre la chaîne RAG à chaque message. Une `config.py` centralise les constantes partagées — en particulier le nom du modèle d'embedding qui doit être identique entre les deux scripts. La séparation offline/runtime est la décision architecturale la plus importante du projet.

**Major components:**
1. `build_index.py` — ingestion PDF, chunking, embedding, génération de `faiss_index/` (commité dans le repo)
2. `config.py` — constantes partagées (modèle, chunk size) — importé par tous les scripts
3. `app.py` — UI Streamlit + pipeline RAG complet (load index, query, call Mistral, afficher réponse)
4. `faiss_index/` — vectorstore local commité dans le repo Git (contrainte Streamlit Community Cloud)
5. `.streamlit/secrets.toml` — clé API locale uniquement, dans `.gitignore`

### Critical Pitfalls

1. **Index FAISS absent sur Streamlit Community Cloud** — commiter `faiss_index/` dans le repo, vérifier que ce dossier n'est PAS dans `.gitignore`. Décider avant tout développement.
2. **Clé API Mistral exposée dans le repo** — ajouter `.streamlit/secrets.toml` dans `.gitignore` dès l'init du repo, utiliser exclusivement `st.secrets["MISTRAL_API_KEY"]`.
3. **Modèle d'embedding différent entre build et query** — définir `EMBEDDING_MODEL = "mistral-embed"` dans `config.py` et importer depuis les deux scripts. Toute modification requiert un rebuild complet de l'index.
4. **Rate limits Mistral free tier non gérés** — wrapper tous les appels Mistral dans `try/except` avec message utilisateur FR affiché via `st.warning()`.
5. **FAISS rechargé à chaque re-run Streamlit** — utiliser `@st.cache_resource` sur la fonction de chargement de l'index, sans exception.

---

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Setup et Configuration
**Rationale:** Toutes les décisions critiques de sécurité et d'infrastructure doivent précéder tout développement. Les pitfalls les plus graves (clé API exposée, index absent) surviennent avant la première ligne de code applicatif.
**Delivers:** Repo configuré, `.gitignore` correct, structure de fichiers en place, clé API sécurisée, `config.py` avec constantes partagées.
**Addresses:** Sécurité clé API (Pitfall 2), cohérence du modèle d'embedding (Pitfall 5).
**Avoids:** Les deux pitfalls CRITIQUE du projet.

### Phase 2: Build de l'index FAISS
**Rationale:** L'index doit être validé avant d'écrire l'UI — tester en isolation évite de déboguer le pipeline entier. La qualité de l'extraction PDF et le calibrage des chunks déterminent la qualité de toutes les réponses ultérieures.
**Delivers:** `build_index.py` fonctionnel, `faiss_index/` commité dans le repo, extraction PDF validée, chunks calibrés.
**Uses:** `pypdf`, `langchain-text-splitters` (chunk_size=400-600, overlap=50-100), `MistralAIEmbeddings`, `faiss-cpu`.
**Avoids:** Pitfall extraction PDF (Pitfall 9), taille de chunks mal calibrée (Pitfall 4), modèle embedding incohérent (Pitfall 5).

### Phase 3: Core RAG (sans UI)
**Rationale:** Valider le pipeline complet en CLI avant d'ajouter la couche Streamlit. Un core fonctionnel en isolation simplifie drastiquement le débogage.
**Delivers:** Fonction de query testable en ligne de commande — charge l'index, récupère k=3-5 chunks, appelle Mistral, retourne une réponse.
**Uses:** `langchain` LCEL, `ChatMistralAI` (mistral-small-latest), `FAISS.load_local()`.
**Implements:** Pipeline RAG complet (Path 2 de ARCHITECTURE.md).
**Avoids:** Gestion 429 Mistral (Pitfall 3), `allow_dangerous_deserialization` (Pitfall 7).

### Phase 4: Interface Streamlit + System Prompt
**Rationale:** L'UI se construit sur un core validé. Le system prompt (langue, persona, fallback) est groupé ici car il conditionne la qualité perçue de l'app entière — ratio valeur/effort excellent.
**Delivers:** `app.py` avec chat UI complet, `st.session_state` pour l'historique, system prompt FR + persona + fallback hors-scope, `@st.cache_resource` sur le chargement FAISS.
**Addresses:** Toutes les features "Table Stakes" de FEATURES.md.
**Avoids:** FAISS rechargé à chaque re-run (Pitfall 6), conversation perdue sans session_state.

### Phase 5: Polish et Questions Suggérées
**Rationale:** Les différenciateurs et le polish UX s'ajoutent après que le core fonctionne. Les questions suggérées requièrent un chat de base opérationnel pour s'y connecter.
**Delivers:** Questions suggérées au démarrage (st.button + st.columns, uniquement si len(messages)==0), suivi multi-tour (historique passé au LLM), spinner cold start.
**Addresses:** Features "Différenciateurs" de FEATURES.md.
**Avoids:** Cold start UX non anticipé (Pitfall 10).

### Phase 6: Déploiement Streamlit Community Cloud
**Rationale:** Déployer en dernier, une fois que l'app est stable en local. Vérifier que l'index est commité et que les secrets sont configurés dans le dashboard avant le premier deploy.
**Delivers:** App publique accessible sans login, secrets configurés dans le dashboard Streamlit.
**Avoids:** Index absent sur le cloud (Pitfall 1), cold start non documenté (Pitfall 10).

### Phase Ordering Rationale

- **Setup avant tout** : deux pitfalls CRITIQUE surviennent au niveau Git/config, pas dans le code. Impossible de les corriger après coup sans risque.
- **Index avant l'app** : la qualité des chunks détermine la qualité des réponses — valider en isolation avant d'intégrer avec Streamlit.
- **Core RAG en CLI d'abord** : séparer les problèmes — un bug dans le pipeline ne doit pas être masqué par des bugs UI.
- **System prompt groupé avec l'UI** : la langue et le persona sont des paramètres de prompt, pas d'architecture — leur intégration est immédiate.
- **Polish en dernier** : les questions suggérées et le multi-tour sont des améliorations sur un core stable.

### Research Flags

Phases avec patterns bien documentés (skip research-phase) :
- **Phase 1 (Setup)** : décisions standard de sécurité Git, documentation officielle Streamlit.
- **Phase 2 (Build index)** : pipeline LangChain PDF→FAISS documenté officiellement, validation manuelle suffisante.
- **Phase 3 (Core RAG)** : LCEL bien documenté, patterns stables.
- **Phase 4 (UI Streamlit)** : `st.chat_message`, `st.session_state` — documentation officielle Streamlit complète.

Phases pouvant nécessiter un research-phase pendant le planning :
- **Phase 5 (Multi-tour)** : le passage de l'historique au prompt Mistral peut nécessiter des ajustements selon le format attendu par `ChatMistralAI` (HumanMessage/AIMessage vs dicts).
- **Phase 6 (Déploiement)** : si le cold start devient problématique, des solutions de "keep-alive" peuvent nécessiter recherche.

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Basé sur documentation officielle LangChain, Streamlit et Mistral (août 2025). Versions précises, rationale claire. |
| Features | MEDIUM | Basé sur des patterns communs de chatbots portfolio — pas de benchmark direct. Priorités logiques mais non validées par retour utilisateur. |
| Architecture | HIGH | Patterns FAISS+LangChain+Streamlit bien documentés, deux chemins d'exécution clairement séparés. Contraintes Streamlit Community Cloud vérifiées. |
| Pitfalls | MEDIUM-HIGH | Patterns stables et récurrents dans ce stack. La plupart sont documentés officiellement ou issus de problèmes LangChain connus. |

**Overall confidence:** MEDIUM-HIGH

### Gaps to Address

- **Qualité du PDF source** : si `dossier_competence.pdf` contient des tableaux complexes ou du texte multi-colonne, `pypdf` peut produire une extraction dégradée. Valider impérativement lors du build de l'index (Phase 2) avant de continuer.
- **Chunk size optimal** : 400-600 chars est une recommandation générale pour des documents courts et denses. La valeur exacte doit être calibrée empiriquement sur le PDF réel lors du build.
- **Format historique multi-tour Mistral** : le passage de l'historique de conversation au format `ChatMistralAI` (LangChain) n'a pas été testé en pratique — valider lors de la Phase 5.
- **Quota Mistral free tier** : les limites exactes (requêtes/minute, tokens/jour) sont sujettes à changement — surveiller lors des tests de charge.

---

## Sources

### Primary (HIGH confidence)
- Documentation officielle LangChain (langchain.com) — LCEL, FAISS wrapper, text splitters, MistralAI integration
- Documentation officielle Streamlit (docs.streamlit.io) — `st.chat_message`, `st.session_state`, `@st.cache_resource`, secrets management, Community Cloud constraints
- Documentation officielle Mistral AI (docs.mistral.ai) — modèles disponibles, SDK v1.0, mistral-embed

### Secondary (MEDIUM confidence)
- Patterns communautaires LangChain — chunk size recommandations pour documents courts
- Retours d'expérience Streamlit Community Cloud — comportement filesystem éphémère, cold start

### Tertiary (LOW confidence)
- Estimation MVP 8-12h — basée sur la complexité des composants, non validée empiriquement
- Chunk size 400-600 chars — recommandation générale, doit être validée sur le PDF réel

---

*Research completed: 2026-03-13*
*Ready for roadmap: yes*
