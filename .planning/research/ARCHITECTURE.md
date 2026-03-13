# Architecture Research: RAG Chatbot CV — Streamlit + FAISS + Mistral

## Two Execution Paths

### Path 1 — Build Index (offline, manuel)

```
dossier_competence.pdf
  → PyPDF loader (pypdf)
    → RecursiveCharacterTextSplitter
      → MistralAIEmbeddings (mistral-embed)
        → FAISS index
          → save_local("faiss_index/")  ← commité dans le repo
```

**Script:** `build_index.py` — lancé manuellement après mise à jour du PDF.

### Path 2 — Query (runtime, Streamlit app)

```
Question utilisateur (st.chat_input)
  → MistralAIEmbeddings (même modèle que build)
    → FAISS.load_local() [@st.cache_resource]
      → similarity_search(k=3-5 chunks)
        → ChatMistralAI (mistral-small-latest)
          [system prompt: langue FR, persona, out-of-scope fallback]
          [context: chunks récupérés]
          [history: st.session_state.messages]
        → Réponse affichée (st.chat_message)
          → st.session_state.messages.append(...)
```

---

## Composants

| Composant | Rôle | Input | Output | Dépendances |
|-----------|------|-------|--------|-------------|
| `build_index.py` | Construit l'index vectoriel | PDF | `faiss_index/` | pypdf, langchain, MistralAIEmbeddings |
| `app.py` | Point d'entrée Streamlit | — | UI | tous les composants ci-dessous |
| `core.py` (ou inline) | Logique RAG (load + query) | Question + history | Réponse | FAISS, ChatMistralAI |
| FAISS index (`faiss_index/`) | Vectorstore local | — | Chunks similaires | Doit être commité dans le repo |
| `assets/dossier_competence.pdf` | Document source | — | Texte | — |
| `config.py` | Constantes partagées (modèle, chunk size) | — | Constantes | — |
| `.streamlit/secrets.toml` | Clé API Mistral (local) | — | Secrets | Ne jamais commiter |
| Streamlit Secrets (cloud) | Clé API Mistral (prod) | — | Secrets | Configuré dans le dashboard |
| Suggested questions | Boutons de démarrage | — | Pré-remplit `st.chat_input` | session_state |

---

## Structure de fichiers recommandée

```
/
├── app.py                    # Streamlit UI + pipeline RAG
├── build_index.py            # Script de build de l'index (run manuel)
├── config.py                 # Constantes partagées (MODEL_NAME, CHUNK_SIZE...)
├── requirements.txt
├── assets/
│   └── dossier_competence.pdf
├── faiss_index/              # Index buildé — commité dans le repo
│   ├── index.faiss
│   └── index.pkl
└── .streamlit/
    └── secrets.toml          # LOCAL ONLY — dans .gitignore
```

---

## Patterns à suivre

- **`@st.cache_resource`** sur le chargement FAISS — sans ça, l'index se recharge à chaque re-run Streamlit
- **`st.session_state.messages`** pour l'historique de conversation — liste de dicts `{role, content}`
- **Index buildé offline commité** dans le repo — Streamlit Community Cloud n'a pas de filesystem persistant
- **Config centralisée** dans `config.py` — le nom du modèle d'embedding doit être identique à la build et au query time
- **Suggested questions** : affichées via `st.button()` dans un `st.columns()` uniquement quand `len(messages) == 0`

---

## Anti-patterns à éviter

| Anti-pattern | Problème | Alternative |
|--------------|----------|-------------|
| Charger le modèle dans la fonction de query | Rechargement à chaque message | `@st.cache_resource` |
| Builder l'index au démarrage de l'app | Trop lent au cold start, consomme les quotas API | Index buildé offline + commité |
| Passer tout le document comme contexte | Dépasse la fenêtre de contexte, coûteux | FAISS retrieve k=3-5 chunks |
| Stocker la clé API dans le code | Fuite dans le repo public | Streamlit secrets uniquement |
| Chat sans session_state | Conversation perdue à chaque re-run | `st.session_state` obligatoire |

---

## Ordre de build (dépendances)

1. **Config** (`config.py`) — constantes partagées avant tout le reste
2. **Index build** (`build_index.py`) — valider que l'index est correct avant de coder l'UI
3. **RAG core** (query handler) — tester en isolation (CLI) avant intégration Streamlit
4. **Chat UI Streamlit** (`app.py`) — interface sur un core qui fonctionne
5. **Suggested questions** — polish UI après que le chat de base fonctionne
6. **Déploiement** — Streamlit Community Cloud en dernier

---

## Contraintes Streamlit Community Cloud

- **Mémoire** : ~800MB RAM — `faiss-cpu` + modèle Mistral rentrent dans la limite
- **Cold start** : 10-30s — l'app dort après inactivité, normal pour le free tier
- **Filesystem** : éphémère entre déploiements — FAISS doit être dans le repo Git
- **Rate limits** : pas de limite de requêtes côté Streamlit, mais Mistral free tier s'applique
