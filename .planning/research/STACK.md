# Stack Research: RAG Chatbot CV — Streamlit + Mistral + FAISS

## Recommended Stack

### Core

| Layer | Library | Version | Rationale |
|-------|---------|---------|-----------|
| App framework | `streamlit` | >=1.35.0 | Hébergement natif sur Streamlit Community Cloud, chat UI intégré (`st.chat_message`) |
| Python | Python | 3.11 | Stable, compatibilité garantie avec toutes les libs ci-dessous |

### LLM

| Library | Version | Rationale |
|---------|---------|-----------|
| `mistralai` | >=1.0.0 | SDK officiel Mistral (réécriture majeure à v1.0 mi-2024) — prefer over community wrappers |
| `langchain-mistralai` | >=0.1.0 | Fournit `ChatMistralAI` + `MistralAIEmbeddings` pour intégration LangChain |

**Modèle recommandé (free tier):** `mistral-small-latest` pour les réponses, `mistral-embed` pour les embeddings.

### Vector Store

| Library | Version | Rationale |
|---------|---------|-----------|
| `faiss-cpu` | >=1.8.0 | Vectorstore local, pas de coût, adapté à un seul PDF |
| `langchain-community` | >=0.2.0 | Wrapper FAISS avec `save_local` / `load_local` |

### Document Ingestion

| Library | Version | Rationale |
|---------|---------|-----------|
| `pypdf` | >=4.0.0 | Parser PDF maintenu (PyPDF2 est déprécié — ne pas utiliser) |
| `langchain-text-splitters` | >=0.2.0 | `RecursiveCharacterTextSplitter` pour chunking du PDF |

### RAG Orchestration

| Library | Version | Rationale |
|---------|---------|-----------|
| `langchain` | >=0.2.0 | LCEL (LangChain Expression Language) préféré à `RetrievalQA` legacy |
| `langchain-core` | >=0.2.0 | Requis par LCEL |

---

## What NOT to Use

| Library | Reason |
|---------|--------|
| `PyPDF2` | Déprécié, remplacé par `pypdf` |
| `openai` SDK | On utilise Mistral |
| `chromadb` | Overhead inutile pour un seul PDF, FAISS suffit |
| `RetrievalQA` (legacy) | Remplacé par LCEL dans LangChain >=0.2 |
| `pinecone` / `weaviate` | Services payants, pas nécessaire |

---

## Constraints critiques (Streamlit Community Cloud)

1. **Pas de filesystem persistant** : Le dossier FAISS doit être commité dans le repo **ou** regénéré au démarrage depuis `assets/dossier_competence.pdf`
2. **`allow_dangerous_deserialization=True`** requis lors du chargement FAISS avec LangChain >=0.2 (pickle)
3. **Secrets Streamlit** : La clé API Mistral doit être dans `.streamlit/secrets.toml` (local) et dans les settings de l'app déployée

---

## requirements.txt Recommandé

```
streamlit>=1.35.0
mistralai>=1.0.0
langchain>=0.2.0
langchain-core>=0.2.0
langchain-community>=0.2.0
langchain-mistralai>=0.1.0
langchain-text-splitters>=0.2.0
faiss-cpu>=1.8.0
pypdf>=4.0.0
```

---

*Confidence: High — basé sur la documentation officielle LangChain, Streamlit et Mistral (août 2025)*
