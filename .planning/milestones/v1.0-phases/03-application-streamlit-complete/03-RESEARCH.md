# Phase 3: Application Streamlit complète - Research

**Researched:** 2026-03-13
**Domain:** Streamlit chat UI, LangChain FAISS query, ChatMistralAI, RAG pipeline, session state
**Confidence:** HIGH

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| RAG-01 | L'app charge l'index FAISS au démarrage via `@st.cache_resource` (chargement unique) | `@st.cache_resource` crée un singleton global partagé entre toutes les sessions — pattern vérifié dans la doc officielle Streamlit |
| RAG-02 | À chaque question, l'app récupère les chunks les plus pertinents (k configurable via `config.py`) | `vectorstore.similarity_search(query, k=K_RETRIEVED)` — API vérifiée, `K_RETRIEVED=4` déjà dans `config.py` |
| RAG-03 | L'app appelle `mistral-small-latest` avec les chunks récupérés comme contexte et l'historique de la session | `ChatMistralAI(model=LLM_MODEL).invoke([SystemMessage, ...HumanMessage/AIMessage..., HumanMessage])` — LLM_MODEL déjà dans `config.py` |
| RAG-04 | Tous les appels Mistral protégés par `try/except` — message d'erreur en français en cas de rate limit (429) | Attraper `Exception` + inspecter le message pour "429" ou utiliser `mistralai.exceptions.MistralAPIStatusException` |
| UI-01 | Interface chat avec `st.chat_input` et `st.chat_message` | Pattern officiel Streamlit — `st.chat_input` pinned en bas, `st.chat_message("user"/"assistant")` pour les bulles |
| UI-02 | Historique complet visible et persistant pendant la session via `st.session_state` | `st.session_state.messages` liste de dicts `{"role": "user"/"assistant", "content": "..."}` — pattern officiel |
| UI-03 | Deux boutons de questions suggérées au premier chargement | `st.button` avec `on_click` callback pour injecter la question dans `st.session_state` — affiché uniquement si `len(st.session_state.messages) == 0` |
| UI-04 | Cliquer sur un bouton suggéré déclenche le pipeline RAG (identique à une saisie manuelle) | Callback `on_click` stocke la question dans `st.session_state.pending_question` → traité dans la boucle principale |
| UI-05 | Spinner/message d'attente pendant le chargement initial de l'index | `@st.cache_resource(show_spinner="Chargement de la base de connaissances...")` ou `st.spinner()` explicite |
| PROMPT-01 | Répond exclusivement en français | `SystemMessage` avec instruction explicite "Tu réponds toujours en français" |
| PROMPT-02 | Ton professionnel cohérent avec le profil des documents | `SystemMessage` définit le persona (assistant CV/compétences professionnel) |
| PROMPT-03 | Si question hors-scope : réponse explicite d'indisponibilité de l'information | `SystemMessage` inclut l'instruction "Si la question dépasse le contenu des documents fournis, dis explicitement que tu ne disposes pas de cette information" |
| PROMPT-04 | Historique de la conversation passé au LLM pour le multi-tour | Reconstruire la liste `[SystemMessage, HumanMessage, AIMessage, HumanMessage, ...]` depuis `st.session_state.messages` à chaque appel |
</phase_requirements>

---

## Summary

Phase 3 construit `app.py` — l'interface Streamlit complète qui charge l'index FAISS existant, accepte des questions via chat UI, et retourne des réponses en français basées sur le document source. C'est la phase de valeur principale du projet : tout ce qui a été construit en Phases 1 et 2 converge ici.

La complexité principale est la gestion correcte de l'état de session Streamlit : l'historique de la conversation (pour le multi-tour), la détection du premier chargement (pour les boutons suggérés), et la question en attente issue d'un clic bouton (qui ne suit pas le même chemin que `st.chat_input`). Ces trois états doivent s'initialiser correctement et interagir sans race condition.

La clé API Mistral doit être lue depuis `st.secrets["MISTRAL_API_KEY"]` en production (Streamlit Community Cloud) mais les objets LangChain (`MistralAIEmbeddings`, `ChatMistralAI`) lisent `MISTRAL_API_KEY` depuis l'environnement automatiquement — Streamlit mappe les root-level secrets vers l'environnement, donc `MISTRAL_API_KEY = "sk-..."` dans `secrets.toml` est directement accessible via `os.environ["MISTRAL_API_KEY"]` sans code supplémentaire.

**Primary recommendation:** Utiliser le pattern officiel Streamlit (session_state + chat_message + cache_resource) avec `ChatMistralAI.invoke()` sur une liste de messages LangChain. Garder `app.py` sous 120 lignes — la logique est simple, le code doit l'être aussi.

---

## Standard Stack

### Core

| Library | Version (installée) | Purpose | Why Standard |
|---------|---------------------|---------|--------------|
| streamlit | 1.55.0 | UI, chat interface, session state, secrets | Framework imposé par le déploiement Community Cloud |
| langchain-mistralai | 1.1.1 | `ChatMistralAI` pour les appels LLM, `MistralAIEmbeddings` pour charger l'index | Intégration officielle LangChain×Mistral |
| langchain-community | 0.4.1 | `FAISS.load_local()` pour charger l'index buildé en Phase 2 | Même package que build_index.py |
| langchain-core | 1.2.18 | `SystemMessage`, `HumanMessage`, `AIMessage` | Types de messages pour le multi-tour |
| config (local) | — | `EMBEDDING_MODEL`, `LLM_MODEL`, `K_RETRIEVED`, `FAISS_INDEX_PATH` | Centralise les constantes partagées |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| python-dotenv | 1.2.2 | Chargement `.env` en dev local | `load_dotenv()` au début de `app.py` pour dev — no-op en prod |
| os (stdlib) | — | Fallback si `st.secrets` pas disponible en dev | `os.environ.get("MISTRAL_API_KEY")` |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `ChatMistralAI.invoke(messages_list)` | `mistralai` SDK direct | LangChain gère la conversion messages → format API, retries, cohérence avec les types de messages |
| `st.session_state.messages` (list of dicts) | `ConversationBufferMemory` LangChain | La liste de dicts Streamlit est plus simple, moins de dépendances, compatible avec la reconstruction des messages LangChain |
| `st.button` avec `on_click` callback | `st.button` dans un `if` | Le pattern `on_click` est recommandé par la doc officielle Streamlit — évite les problèmes de re-render |

**Installation:** Tous les packages sont déjà dans `requirements.txt` (Phase 1).

---

## Architecture Patterns

### Recommended Project Structure

```
/workspaces/etienne.routhier/
├── app.py                   # Application Streamlit — Phase 3
├── config.py                # Constantes importées (déjà créé Phase 1)
├── build_index.py           # Script offline (déjà créé Phase 2)
├── assets/
│   └── resume/
│       └── dossier_competences.pdf
├── faiss_index/             # Index commité (déjà créé Phase 2)
│   ├── index.faiss
│   └── index.pkl
└── .streamlit/
    └── secrets.toml         # GITIGNORED — MISTRAL_API_KEY en dev local
```

### Pattern 1: Chargement de l'index avec cache_resource (RAG-01 + UI-05)

**What:** L'index FAISS est chargé une seule fois pour toutes les sessions Streamlit via `@st.cache_resource`. Le spinner intégré gère UI-05.
**When to use:** Toujours — jamais charger l'index à chaque re-run Streamlit.

```python
# Source: Streamlit docs + LangChain FAISS docs
from langchain_community.vectorstores import FAISS
from langchain_mistralai import MistralAIEmbeddings
from config import EMBEDDING_MODEL, FAISS_INDEX_PATH
import streamlit as st

@st.cache_resource(show_spinner="Chargement de la base de connaissances...")
def load_vectorstore():
    embeddings = MistralAIEmbeddings(model=EMBEDDING_MODEL)
    return FAISS.load_local(
        FAISS_INDEX_PATH,
        embeddings,
        allow_dangerous_deserialization=True  # Index de source locale — sûr
    )
```

### Pattern 2: Initialisation session state (UI-02 + UI-03 + UI-04)

**What:** Initialiser les clés session_state au début de l'app — une seule fois par session.
**When to use:** Toujours en premier, avant tout autre code UI.

```python
# Source: Streamlit docs — session state initialization pattern
if "messages" not in st.session_state:
    st.session_state.messages = []          # Historique conversation UI-02
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None  # Question injectée par bouton UI-04
```

### Pattern 3: Boutons de questions suggérées (UI-03 + UI-04)

**What:** Afficher deux boutons uniquement si l'historique est vide. Le clic injecte la question dans `pending_question` via callback.
**When to use:** Uniquement quand `len(st.session_state.messages) == 0`.

```python
# Source: Streamlit docs — button on_click callback pattern
SUGGESTED_QUESTIONS = [
    "Quelles sont vos principales compétences ?",
    "En quoi pouvez-vous m'aider sur mon projet ?",
]

def inject_question(q: str):
    st.session_state.pending_question = q

if len(st.session_state.messages) == 0:
    st.markdown("**Questions suggérées :**")
    col1, col2 = st.columns(2)
    with col1:
        st.button(SUGGESTED_QUESTIONS[0], on_click=inject_question, args=[SUGGESTED_QUESTIONS[0]])
    with col2:
        st.button(SUGGESTED_QUESTIONS[1], on_click=inject_question, args=[SUGGESTED_QUESTIONS[1]])
```

### Pattern 4: Affichage de l'historique (UI-02)

**What:** Itérer sur `st.session_state.messages` avant `st.chat_input` pour afficher l'historique.
**When to use:** Toujours, à chaque re-run — Streamlit reexécute le script entier.

```python
# Source: Streamlit docs — build conversational apps tutorial
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
```

### Pattern 5: Pipeline RAG complet (RAG-01/02/03/04 + PROMPT-01/02/03/04)

**What:** Récupérer les chunks pertinents, construire les messages LangChain avec historique, appeler ChatMistralAI, gérer les erreurs.
**When to use:** À chaque question (manuelle ou via bouton suggéré).

```python
# Source: LangChain docs — ChatMistralAI + FAISS similarity_search
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_mistralai import ChatMistralAI
from config import LLM_MODEL, K_RETRIEVED

SYSTEM_PROMPT = """Tu es un assistant professionnel qui répond aux questions sur le profil et les compétences d'Etienne Routhier, basé uniquement sur les documents fournis.
Tu réponds toujours en français, avec un ton professionnel.
Si la question dépasse le contenu des documents fournis, réponds explicitement que tu ne disposes pas de cette information — ne génère pas de contenu inventé."""

def run_rag(user_question: str, vectorstore) -> str:
    # RAG-02 : Récupérer les chunks pertinents
    docs = vectorstore.similarity_search(user_question, k=K_RETRIEVED)
    context = "\n\n".join(doc.page_content for doc in docs)

    # PROMPT-04 : Reconstruire l'historique pour le multi-tour
    messages = [SystemMessage(content=SYSTEM_PROMPT + f"\n\nContexte extrait du document :\n{context}")]
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))
    messages.append(HumanMessage(content=user_question))

    # RAG-03 + RAG-04 : Appel LLM avec gestion d'erreur
    try:
        llm = ChatMistralAI(model=LLM_MODEL)
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "rate limit" in error_str.lower() or "too many requests" in error_str.lower():
            return "Désolé, la limite de requêtes de l'API Mistral a été atteinte. Veuillez réessayer dans quelques instants."
        return f"Une erreur est survenue lors de la communication avec l'API : {error_str}"
```

### Pattern 6: Boucle principale — unification entrée manuelle + bouton

**What:** Traiter la question issue de `st.chat_input` et celle issue de `pending_question` de façon unifiée.
**When to use:** Toujours — c'est le cœur de l'app.

```python
# Source: Pattern dérivé de la doc Streamlit buttons + chat_input
# Résoudre la question active (bouton OU saisie manuelle)
user_input = st.chat_input("Posez votre question...")
active_question = st.session_state.pending_question or user_input

# Réinitialiser pending_question après consommation
if st.session_state.pending_question:
    st.session_state.pending_question = None

if active_question:
    # Afficher le message utilisateur
    with st.chat_message("user"):
        st.markdown(active_question)
    st.session_state.messages.append({"role": "user", "content": active_question})

    # Lancer le RAG et afficher la réponse
    with st.chat_message("assistant"):
        with st.spinner("..."):
            answer = run_rag(active_question, vectorstore)
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
```

### Anti-Patterns to Avoid

- **Charger l'index FAISS hors `@st.cache_resource`** : L'index se recharge à chaque re-run Streamlit (chaque frappe clavier, chaque interaction) — latence x100.
- **Stocker le vectorstore dans `st.session_state`** : `session_state` ne persiste que pour une session, pas entre sessions. `cache_resource` est partagé entre toutes les sessions — économie mémoire.
- **Recréer `ChatMistralAI` hors de la fonction RAG** : Le modèle doit être créé avec les bons paramètres à chaque appel — pas de gain à le cacher.
- **`if st.button(...)` sans callback pour les questions suggérées** : Le bouton retourne `True` pendant un seul re-run, puis revient à `False`. Si la logique RAG est dans le bloc `if st.button(...)`, elle ne s'exécutera pas au bon moment après l'initialisation de l'affichage.
- **Passer `MISTRAL_API_KEY` directement à `ChatMistralAI(api_key=...)`** : Inutile — les deux classes LangChain lisent `MISTRAL_API_KEY` depuis l'environnement automatiquement. Streamlit mappe les root-level secrets vers l'environnement.
- **Construire le contexte sans `\n\n` entre les chunks** : Les chunks concaténés sans séparateur clair dégradent la compréhension du modèle.
- **Mettre le `SystemMessage` avec contexte statique** : Le contexte doit être injecté à chaque appel avec les chunks récupérés pour CETTE question — pas en singleton global.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Chat UI avec historique | Formulaire + liste HTML custom | `st.chat_message` + `st.chat_input` | Gestion du scroll, pinning en bas, re-run automatique — gratuit avec Streamlit |
| Session state de conversation | Variable globale Python | `st.session_state` | Streamlit ré-exécute le script entier à chaque interaction — les variables globales sont réinitialisées |
| Cache du vectorstore | Singleton module-level | `@st.cache_resource` | Streamlit peut spawner plusieurs threads — `cache_resource` est thread-safe |
| Appel LLM avec messages LangChain | Appel `mistralai` SDK direct + conversion manuelle | `ChatMistralAI.invoke(messages)` | Conversion automatique `SystemMessage/HumanMessage/AIMessage` → format API Mistral |
| Gestion du prompt multi-tour | Concaténation de strings | Liste de `HumanMessage`/`AIMessage` | Le modèle comprend les rôles — la concaténation de strings perd cette information |

**Key insight:** Streamlit + LangChain gèrent tous les patterns nécessaires. L'app complète doit tenir en ~100-120 lignes.

---

## Common Pitfalls

### Pitfall 1: `allow_dangerous_deserialization=True` manquant

**What goes wrong:** `FAISS.load_local()` lève `ValueError: The de-serialization relies on pickle...`.
**Why it happens:** LangChain a ajouté ce flag de sécurité pour prévenir les attaques pickle. Absent par défaut.
**How to avoid:** Toujours passer `allow_dangerous_deserialization=True` dans `FAISS.load_local()`. L'index est généré localement — source de confiance.
**Warning signs:** `ValueError` mentionnant "pickle" ou "dangerous deserialization" au démarrage de l'app.

### Pitfall 2: Secret API non trouvé au démarrage

**What goes wrong:** `MistralAIEmbeddings` ou `ChatMistralAI` lève `ValidationError: mistral_api_key field required` ou `AuthenticationError`.
**Why it happens:** `MISTRAL_API_KEY` n'est pas dans l'environnement. En dev local, `.streamlit/secrets.toml` n'est pas chargé avant le premier run.
**How to avoid:** Streamlit charge automatiquement `.streamlit/secrets.toml` et mappe les root-level keys vers l'environnement. Vérifier que `secrets.toml` contient `MISTRAL_API_KEY = "sk-..."` (nom exact, case sensitive). En dev, `load_dotenv()` avant le premier appel API fonctionne aussi comme fallback.
**Warning signs:** `ValidationError` ou erreur d'authentification Mistral au démarrage.

### Pitfall 3: Race condition entre bouton suggéré et chat_input

**What goes wrong:** Cliquer un bouton suggéré et immédiatement saisir dans `st.chat_input` traite les deux questions. Ou le bouton cliqué ne déclenche rien.
**Why it happens:** Streamlit re-run le script entier après chaque interaction. Le bouton retourne `True` pendant UN seul re-run.
**How to avoid:** Utiliser le pattern `pending_question` dans `session_state` + callback `on_click`. Toujours consommer et réinitialiser `pending_question` avant `st.chat_input`.
**Warning signs:** La question suggérée ne s'affiche pas dans le chat, ou s'affiche deux fois.

### Pitfall 4: `@st.cache_resource` chargé avec EMBEDDING_MODEL différent de build

**What goes wrong:** L'index FAISS est chargé mais retourne des résultats non pertinents ou des erreurs de dimension.
**Why it happens:** Incohérence entre `EMBEDDING_MODEL` utilisé dans `build_index.py` et dans `app.py`.
**How to avoid:** TOUJOURS importer `EMBEDDING_MODEL` depuis `config.py` — ne jamais dupliquer la valeur `"mistral-embed"` dans `app.py`.
**Warning signs:** Résultats RAG incohérents, scores de similarité anormalement bas ou élevés.

### Pitfall 5: Historique multi-tour mal construit pour ChatMistralAI

**What goes wrong:** Le modèle "oublie" le contexte précédent ou produit des réponses incohérentes avec le dialogue.
**Why it happens:** L'ordre des messages LangChain doit être `[SystemMessage, HumanMessage, AIMessage, HumanMessage, AIMessage, ..., HumanMessage]`. Rompre cet ordre perturbe le modèle.
**How to avoid:** Reconstruire la liste depuis `st.session_state.messages` à chaque appel. Ne jamais ajouter le `HumanMessage` de la question courante dans `session_state` avant l'appel LLM — l'ajouter après.
**Warning signs:** Réponses qui ne tiennent pas compte de questions précédentes, ou erreurs API liées au format des messages.

### Pitfall 6: Rate limit Mistral (HTTP 429) en production

**What goes wrong:** L'app Streamlit plante silencieusement ou affiche une stack trace Python à l'utilisateur.
**Why it happens:** Mistral free tier : 2 req/min. Un utilisateur curieux peut déclencher plusieurs questions rapidement.
**How to avoid:** Entourer TOUS les appels `ChatMistralAI.invoke()` d'un `try/except Exception` qui vérifie si "429" est dans le message d'erreur et retourne un message en français. L'erreur doit s'afficher dans la bulle assistant (pas en dehors).
**Warning signs:** Exception non gérée visible par l'utilisateur, app qui reload ou se fige.

---

## Code Examples

Verified patterns from official sources:

### Structure complète minimale de app.py

```python
# Source: Streamlit docs (chat apps) + LangChain FAISS + ChatMistralAI
import streamlit as st
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings
from config import EMBEDDING_MODEL, LLM_MODEL, K_RETRIEVED, FAISS_INDEX_PATH

load_dotenv()  # No-op en prod Streamlit Cloud (secrets.toml auto-mappés)

@st.cache_resource(show_spinner="Chargement de la base de connaissances...")
def load_vectorstore():
    embeddings = MistralAIEmbeddings(model=EMBEDDING_MODEL)
    return FAISS.load_local(
        FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True
    )

# Initialisation session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

vectorstore = load_vectorstore()

# Titre
st.title("Assistant — Dossier de Compétences")

# Affichage historique
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Boutons suggérés (uniquement au premier chargement)
SUGGESTED = [
    "Quelles sont vos principales compétences ?",
    "En quoi pouvez-vous m'aider sur mon projet ?",
]
def inject_question(q):
    st.session_state.pending_question = q

if len(st.session_state.messages) == 0:
    col1, col2 = st.columns(2)
    with col1:
        st.button(SUGGESTED[0], on_click=inject_question, args=[SUGGESTED[0]])
    with col2:
        st.button(SUGGESTED[1], on_click=inject_question, args=[SUGGESTED[1]])

# Entrée utilisateur
user_input = st.chat_input("Posez votre question sur le profil...")
active_question = st.session_state.pending_question or user_input
if st.session_state.pending_question:
    st.session_state.pending_question = None

if active_question:
    with st.chat_message("user"):
        st.markdown(active_question)
    st.session_state.messages.append({"role": "user", "content": active_question})

    # Pipeline RAG
    docs = vectorstore.similarity_search(active_question, k=K_RETRIEVED)
    context = "\n\n".join(doc.page_content for doc in docs)

    lc_messages = [
        SystemMessage(content=f"Tu es un assistant professionnel. Tu réponds toujours en français. "
                               f"Utilise uniquement le contexte fourni. "
                               f"Si la question dépasse le contenu des documents, dis explicitement "
                               f"que tu ne disposes pas de cette information.\n\nContexte:\n{context}")
    ]
    for msg in st.session_state.messages[:-1]:  # Exclure le message courant déjà ajouté
        if msg["role"] == "user":
            lc_messages.append(HumanMessage(content=msg["content"]))
        else:
            lc_messages.append(AIMessage(content=msg["content"]))
    lc_messages.append(HumanMessage(content=active_question))

    with st.chat_message("assistant"):
        with st.spinner("..."):
            try:
                llm = ChatMistralAI(model=LLM_MODEL)
                answer = llm.invoke(lc_messages).content
            except Exception as e:
                err = str(e)
                if "429" in err or "rate limit" in err.lower() or "too many requests" in err.lower():
                    answer = "La limite de requêtes de l'API Mistral a été atteinte. Veuillez réessayer dans quelques instants."
                else:
                    answer = f"Une erreur est survenue : {err}"
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
```

### Structure secrets.toml (dev local uniquement — GITIGNORE)

```toml
# .streamlit/secrets.toml — NE PAS COMMITER
MISTRAL_API_KEY = "sk-..."
```

Streamlit mappe automatiquement les root-level keys vers l'environnement. `MistralAIEmbeddings` et `ChatMistralAI` lisent `MISTRAL_API_KEY` depuis `os.environ` — pas de code supplémentaire nécessaire.

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `ConversationBufferMemory` LangChain | Liste de dicts `st.session_state.messages` + reconstruction manuelle | Streamlit 1.2+ | Plus simple, pas de dépendance LangChain Memory, compatible Streamlit nativement |
| `@st.cache` (déprécié) | `@st.cache_resource` | Streamlit 1.18 | `cache_resource` est dédié aux ressources non-sérialisables (modèles, DB, index) |
| `st.write` / `st.text` pour le chat | `st.chat_message` + `st.chat_input` | Streamlit 1.22+ | UX chat native, pinning automatique de l'input en bas |
| Lecture de la clé via `st.secrets["key"]` explicitement passée | Root-level secrets auto-mappés vers l'environnement | Streamlit 1.x | Plus besoin de passer la clé manuellement aux clients API |

**Deprecated/outdated:**
- `@st.cache` : archivé, remplacé par `@st.cache_data` (données) et `@st.cache_resource` (ressources)
- `st.experimental_rerun()` : remplacé par `st.rerun()`
- `ConversationBufferMemory` : toujours fonctionnel mais inutile pour ce use case — surcharge inutile

---

## Open Questions

1. **Comportement de `on_click` callback quand le bouton est cliqué et que `st.chat_input` contient du texte simultanément**
   - What we know: `on_click` est exécuté avant le re-run du script. `pending_question` prendra la priorité sur `user_input` dans la logique actuelle.
   - What's unclear: Si l'utilisateur a écrit dans `chat_input` ET cliqué un bouton dans le même "frame", quel est l'ordre exact ?
   - Recommendation: Dans ce cas edge rare, `pending_question` est consommé en premier. La question tapée est perdue. Acceptable pour ce use case — les boutons ne sont affichés que si l'historique est vide (donc `chat_input` ne contient rien de pertinent).

2. **Format exact de l'exception Mistral 429 via LangChain**
   - What we know: `MistralAPIStatusException` avec status 429 est l'exception native du SDK `mistralai`. Via LangChain, cette exception peut être wrappée.
   - What's unclear: LangChain wrapping peut modifier le type de l'exception. Le message de l'exception contiendra "429" dans tous les cas.
   - Recommendation: Attraper `Exception` au niveau le plus large et inspecter `str(e)` pour "429" — plus robuste que d'importer un type d'exception spécifique qui pourrait changer.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Aucun framework de test (app Streamlit — tests manuels + smoke tests) |
| Config file | Aucun |
| Quick run command | `streamlit run app.py` (dans l'environnement avec `MISTRAL_API_KEY` définie) |
| Full suite command | `streamlit run app.py` + validation manuelle des 4 success criteria |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| RAG-01 | Index FAISS chargé une seule fois via `@st.cache_resource` | smoke | `python -c "import app; print('import OK')"` (ne lance pas le serveur) | ❌ Wave 0 (créer app.py) |
| RAG-02 | `similarity_search` retourne k=4 chunks | smoke | `python -c "from langchain_community.vectorstores import FAISS; from langchain_mistralai import MistralAIEmbeddings; from config import *; vs=FAISS.load_local(FAISS_INDEX_PATH, MistralAIEmbeddings(model=EMBEDDING_MODEL), allow_dangerous_deserialization=True); docs=vs.similarity_search('compétences', k=K_RETRIEVED); print(len(docs), 'docs'); assert len(docs)==K_RETRIEVED"` | ✅ faiss_index/ existe |
| RAG-03 | `ChatMistralAI` retourne une réponse non-vide | manual | Lancer l'app et poser une question — vérifier une réponse en français | ❌ Wave 0 |
| RAG-04 | Erreur 429 affiche message français — app ne plante pas | manual | Saturer l'API (>2 req/min) ou simuler l'exception dans le code | ❌ Wave 0 |
| UI-01 | Interface chat visible avec input pinned en bas | manual | `streamlit run app.py` → vérifier visuellement | ❌ Wave 0 |
| UI-02 | Historique persist sur re-run | manual | Poser 2 questions → vérifier que les 2 sont affichées | ❌ Wave 0 |
| UI-03 | 2 boutons suggérés au premier chargement | manual | `streamlit run app.py` → vérifier avant tout message | ❌ Wave 0 |
| UI-04 | Clic bouton déclenche le RAG | manual | Cliquer un bouton → vérifier une réponse | ❌ Wave 0 |
| UI-05 | Spinner pendant chargement index | manual | `streamlit run app.py` → observer le cold start | ❌ Wave 0 |
| PROMPT-01 | Réponse en français | manual | Poser une question en anglais → vérifier réponse en français | ❌ Wave 0 |
| PROMPT-02 | Ton professionnel | manual | Lire la réponse — vérifier cohérence avec profil CV | ❌ Wave 0 |
| PROMPT-03 | Hors-scope : réponse explicite | manual | Poser "Quel est ton film préféré ?" → vérifier le refus explicite | ❌ Wave 0 |
| PROMPT-04 | Multi-tour fonctionnel | manual | Poser "Dis-m'en plus sur le projet précédent" → vérifier cohérence | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `python -c "from config import LLM_MODEL, K_RETRIEVED, FAISS_INDEX_PATH; print('config OK')"` (sans appel API)
- **Per wave merge:** `streamlit run app.py` + vérification manuelle des success criteria
- **Phase gate:** Les 4 success criteria vérifiés manuellement avant `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `app.py` — couvre tous les requirements de la phase (créer de zéro)
- [ ] `MISTRAL_API_KEY` dans `.streamlit/secrets.toml` ou environnement — prérequis pour tester l'app

*(Le `config.py`, `faiss_index/`, et `requirements.txt` existent déjà depuis Phases 1 et 2)*

---

## Sources

### Primary (HIGH confidence)

- Streamlit docs — `st.cache_resource`: https://docs.streamlit.io/develop/api-reference/caching-and-state/st.cache_resource
- Streamlit docs — Build conversational apps (st.chat_message, st.chat_input, session_state): https://docs.streamlit.io/develop/tutorials/chat-and-llm-apps/build-conversational-apps
- Streamlit docs — Buttons behavior and callbacks: https://docs.streamlit.io/develop/concepts/design/buttons
- Streamlit docs — Secrets management: https://docs.streamlit.io/develop/concepts/connections/secrets-management
- LangChain FAISS docs — `load_local` avec `allow_dangerous_deserialization`: https://docs.langchain.com/oss/python/integrations/vectorstores/faiss
- LangChain ChatMistralAI — invoke avec liste de messages: https://api.python.langchain.com/en/latest/mistralai/chat_models/langchain_mistralai.chat_models.ChatMistralAI.html
- Phase 2 RESEARCH.md — patterns établis (load_local, allow_dangerous_deserialization, config.py): fichier local vérifié

### Secondary (MEDIUM confidence)

- WebSearch + GitHub issues — MistralAPIStatusException 429 wrappé dans Exception par LangChain: https://github.com/langchain-ai/langchain/issues/29125
- WebSearch Streamlit Community — pattern `pending_question` pour boutons suggérés dans chat app: https://discuss.streamlit.io/t/using-buttons-in-st-chat-input/52323

### Tertiary (LOW confidence)

- Comportement exact de l'ordre callback/chat_input simultané — non testé, déduit du comportement des re-runs Streamlit

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — versions vérifiées dans requirements.txt (Phase 1), APIs testées en Phase 2
- Architecture: HIGH — patterns officiels Streamlit + LangChain, code validé conceptuellement
- Pitfalls: HIGH (1, 2, 4) vérifiés par doc officielle / Phase 2 résultats concrets ; MEDIUM (3, 5, 6) dérivés de la doc + comportement connu

**Research date:** 2026-03-13
**Valid until:** 2026-06-13 (90 jours — Streamlit 1.55 et LangChain stack stables, changements majeurs peu probables dans ce délai)
