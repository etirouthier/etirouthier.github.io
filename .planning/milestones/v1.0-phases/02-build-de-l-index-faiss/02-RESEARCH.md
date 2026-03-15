# Phase 2: Build de l'index FAISS - Research

**Researched:** 2026-03-13
**Domain:** LangChain FAISS vectorstore, PDF loading, Mistral embeddings, offline indexing script
**Confidence:** HIGH

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| INDEX-01 | `build_index.py` ingère tous les fichiers présents dans `assets/` en une seule passe | `PyPDFDirectoryLoader` avec `recursive=True` — testé localement, charge 4 pages depuis `assets/resume/dossier_competences.pdf` |
| INDEX-02 | `build_index.py` génère un index FAISS local dans `faiss_index/` via embeddings Mistral (`mistral-embed`) | `FAISS.from_documents()` + `MistralAIEmbeddings(model="mistral-embed")` + `save_local("faiss_index")` — API vérifiée localement |
| INDEX-03 | L'index FAISS (`faiss_index/`) peut être commité dans Git | `save_local()` crée `faiss_index/index.faiss` + `faiss_index/index.pkl` — aucun de ces fichiers n'est exclu par le `.gitignore` existant (vérifié Phase 1) |
| INDEX-04 | Le script affiche des logs de validation (nb chunks, aperçu des premiers chunks) | Pattern `print()` standard — afficher `len(chunks)` et `chunks[0].page_content[:200]` pour les N premiers chunks |
</phase_requirements>

---

## Summary

Phase 2 construit le script offline `build_index.py` qui ingère le PDF source, le découpe en chunks, génère les embeddings via l'API Mistral, et sauvegarde l'index FAISS dans `faiss_index/`. Ce script tourne une seule fois (ou à chaque mise à jour du document) en dehors de Streamlit — il ne doit pas importer `streamlit`.

Le PDF source (`assets/resume/dossier_competences.pdf`) a été testé directement : 4 pages, ~8700 caractères au total, extraction pypdf de bonne qualité. Le texte est lisible et bien structuré malgré la mise en page en colonnes. Avec `CHUNK_SIZE=500` et `CHUNK_OVERLAP=50` (valeurs déjà dans `config.py`), on obtient 20 chunks — c'est un nombre raisonnable pour ce document. L'aperçu des premiers chunks confirme que le contenu est cohérent.

La clé API Mistral est nécessaire pour appeler `mistral-embed`. Comme `build_index.py` est un script offline (pas une app Streamlit), `st.secrets` ne s'applique pas ici — la clé doit être lue depuis la variable d'environnement `MISTRAL_API_KEY`. `MistralAIEmbeddings` la lit automatiquement depuis l'environnement si elle n'est pas passée explicitement.

**Primary recommendation:** Utiliser `PyPDFDirectoryLoader` + `RecursiveCharacterTextSplitter` + `FAISS.from_documents()` + `save_local()`. Garder le script linéaire, bien commenté, avec des prints de validation clairs.

---

## Standard Stack

### Core

| Library | Version (installée) | Purpose | Why Standard |
|---------|---------------------|---------|--------------|
| langchain-community | 0.4.1 | `PyPDFDirectoryLoader`, `FAISS` vectorstore | Seul package contenant ces deux composants |
| langchain-mistralai | 1.1.1 | `MistralAIEmbeddings(model="mistral-embed")` | Intégration officielle LangChain×Mistral |
| langchain-text-splitters | 1.1.1 | `RecursiveCharacterTextSplitter` | Séparé de `langchain` depuis 0.2 — package dédié |
| faiss-cpu | 1.13.2 | Vectorstore local, sauvegarde/chargement binaire | Pas de service externe, commitable dans Git |
| pypdf | 6.8.0 | Parsing PDF (dépendance de `PyPDFDirectoryLoader`) | Activement maintenu, remplace PyPDF2 archivé |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| python-dotenv | 1.2.2 | Chargement `MISTRAL_API_KEY` depuis `.env` en dev local | Optionnel — si clé pas dans l'env système |
| os (stdlib) | — | `os.path.exists()` pour vérifier si l'index existe déjà | Toujours |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `PyPDFDirectoryLoader` | glob + `PyPDFLoader` manuel | `PyPDFDirectoryLoader(recursive=True)` est plus concis — gère le glob automatiquement |
| `RecursiveCharacterTextSplitter` | `CharacterTextSplitter` | `RecursiveCharacterTextSplitter` est plus robuste pour le texte structuré (paragraphes, listes) |
| print() natif | logging module | Pour un script offline simple, `print()` est suffisant — logging ajoute de la complexité sans valeur |

**Installation:** Tous les packages sont déjà dans `requirements.txt` (Phase 1).

---

## Architecture Patterns

### Recommended Project Structure

```
/workspaces/etienne.routhier/
├── build_index.py           # Ce script — Phase 2
├── config.py                # Constantes importées (EMBEDDING_MODEL, CHUNK_SIZE, etc.)
├── assets/
│   └── resume/
│       └── dossier_competences.pdf   # Document source
└── faiss_index/             # Créé par build_index.py — commité dans Git
    ├── index.faiss          # Index vectoriel binaire
    └── index.pkl            # Métadonnées (textes, metadata)
```

### Pattern 1: Pipeline de build FAISS complet

**What:** Script linéaire en 4 étapes : charger → découper → embedder → sauvegarder.
**When to use:** Toujours — c'est le seul pattern pour construire un index FAISS offline.

```python
# build_index.py
# Source: LangChain docs FAISS + PyPDFDirectoryLoader
import os
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.vectorstores import FAISS
from langchain_mistralai import MistralAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP, FAISS_INDEX_PATH

# Étape 1 : Charger tous les PDFs depuis assets/
loader = PyPDFDirectoryLoader("assets/", recursive=True)
raw_docs = loader.load()
print(f"[1/4] Chargé : {len(raw_docs)} page(s) depuis assets/")

# Étape 2 : Découper en chunks
splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
)
chunks = splitter.split_documents(raw_docs)
print(f"[2/4] Découpé : {len(chunks)} chunks (taille={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")

# Étape 3 : Générer les embeddings et construire l'index
# MistralAIEmbeddings lit MISTRAL_API_KEY depuis l'environnement automatiquement
embeddings = MistralAIEmbeddings(model=EMBEDDING_MODEL)
vectorstore = FAISS.from_documents(chunks, embeddings)
print(f"[3/4] Index FAISS construit ({len(chunks)} vecteurs, modèle={EMBEDDING_MODEL})")

# Étape 4 : Sauvegarder l'index
vectorstore.save_local(FAISS_INDEX_PATH)
print(f"[4/4] Index sauvegardé dans {FAISS_INDEX_PATH}/")

# Logs de validation (INDEX-04)
print("\n=== Validation des chunks ===")
print(f"Nombre total de chunks : {len(chunks)}")
n_preview = min(3, len(chunks))
for i in range(n_preview):
    print(f"\n--- Chunk {i+1} ({len(chunks[i].page_content)} chars) ---")
    print(chunks[i].page_content[:200])
print("\nIndex prêt. Verifier que le texte est lisible avant de commiter.")
```

### Pattern 2: Clé API pour script offline

**What:** `build_index.py` n'est pas une app Streamlit — `st.secrets` n'est pas disponible.
**When to use:** Toujours pour les scripts exécutés en dehors de Streamlit.

```python
# Option A : Variable d'environnement système (recommandé pour CI/CD)
# export MISTRAL_API_KEY="sk-..."
# MistralAIEmbeddings() la lit automatiquement

# Option B : .env local + python-dotenv (recommandé pour dev local)
from dotenv import load_dotenv
load_dotenv()  # Charge .env si présent, sinon no-op
embeddings = MistralAIEmbeddings(model=EMBEDDING_MODEL)
# Note : .env doit contenir MISTRAL_API_KEY=sk-...
# Note : .env est dans .gitignore (*.env)
```

### Pattern 3: Vérification de l'index existant (optionnel)

**What:** Skip le rebuild si l'index est déjà présent.
**When to use:** Utile si le script est relancé plusieurs fois, mais pas obligatoire pour Phase 2.

```python
# Pattern optionnel — peut simplifier les itérations de dev
import os
if os.path.exists(FAISS_INDEX_PATH):
    print(f"Index déjà présent dans {FAISS_INDEX_PATH}/ — skip rebuild")
else:
    # ... pipeline de build
```

### Anti-Patterns to Avoid

- **Importer `streamlit` dans `build_index.py`** : Ce script tourne en dehors de Streamlit. `st.secrets` lève une erreur hors contexte Streamlit.
- **Dupliquer `EMBEDDING_MODEL` dans `build_index.py`** : Importer depuis `config.py` — une divergence avec `app.py` rend l'index silencieusement invalide.
- **Ajouter `faiss_index/` au `.gitignore`** : L'index DOIT être commité — Streamlit Community Cloud a un filesystem éphémère.
- **`FAISS.load_local()` sans `allow_dangerous_deserialization=True`** : Nécessaire pour charger un index depuis un `.pkl` (Phase 3 sera affectée).
- **Lancer `build_index.py` sans clé API définie** : `MistralAIEmbeddings` lèvera une erreur `ValidationError` ou `AuthenticationError`. Valider avec `echo $MISTRAL_API_KEY` avant le lancement.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Chargement PDF récursif depuis un dossier | `glob.glob() + for loop + PyPDFLoader` | `PyPDFDirectoryLoader(recursive=True)` | Gère le glob, la gestion d'erreurs, les métadonnées source automatiquement |
| Découpage en chunks | Split naïf sur `\n` ou longueur fixe | `RecursiveCharacterTextSplitter` | Préserve les paragraphes, gère les séparateurs hiérarchiques, évite les coupures au milieu d'une phrase |
| Index vectoriel + similarité cosinus | Calcul NumPy custom | `FAISS.from_documents()` | FAISS optimise le stockage et la recherche pour des milliers de vecteurs, gère la sérialisation |
| Appels d'embedding par batch | Boucle `for doc in chunks` | `FAISS.from_documents()` | Gère le batching automatiquement, respecte les limites de taux API |

**Key insight:** Le pipeline entier (load → split → embed → index → save) est couvert par 5 lignes de LangChain. Tout code custom serait plus fragile et moins maintenu.

---

## Common Pitfalls

### Pitfall 1: `st.secrets` dans un script offline

**What goes wrong:** `build_index.py` importe streamlit pour lire la clé API → `streamlit.errors.NoSessionContext` ou erreur similaire.
**Why it happens:** Confusion entre le contexte Streamlit (app Streamlit live) et le script offline.
**How to avoid:** Utiliser `os.environ.get("MISTRAL_API_KEY")` ou `python-dotenv` dans `build_index.py`. `st.secrets` uniquement dans `app.py`.
**Warning signs:** `AttributeError: module 'streamlit' has no attribute 'secrets'` ou `StreamlitAPIException`.

### Pitfall 2: `allow_dangerous_deserialization` manquant au chargement

**What goes wrong:** Phase 3 (`app.py`) ne peut pas charger l'index avec `FAISS.load_local()` → `ValueError: The de-serialization relies on pickle...`.
**Why it happens:** LangChain a ajouté ce flag de sécurité pour prévenir les attaques pickle. Absent par défaut.
**How to avoid:** Documenter dans le commentaire de `build_index.py` que Phase 3 devra utiliser `allow_dangerous_deserialization=True`. L'index est généré localement (source de confiance).
**Warning signs:** `ValueError` mentionnant "pickle" ou "dangerous deserialization" au chargement.

### Pitfall 3: Qualité du texte PDF dégradée

**What goes wrong:** Les chunks contiennent des caractères mélangés, du texte de colonnes interleaved, ou des fragments illisibles → résultats RAG non pertinents.
**Why it happens:** Les PDFs en colonnes ou avec mise en page complexe peuvent produire une extraction désordonnée avec `pypdf`.
**How to avoid:** Les logs de validation (INDEX-04) permettent de détecter ce problème AVANT de commiter l'index. Si la qualité est mauvaise, envisager `PyMuPDFLoader` ou `pdfplumber` (v2). Pour `dossier_competences.pdf` : extraction testée localement, qualité bonne.
**Warning signs:** Chunks avec des mots coupés arbitrairement, alternance de fragments de colonnes différentes dans le même chunk.

### Pitfall 4: Rate limit Mistral API pendant le build

**What goes wrong:** Erreur HTTP 429 pendant `FAISS.from_documents()` → IndexError ou partial index.
**Why it happens:** Le free tier Mistral a des limites de taux. `from_documents()` envoie tous les chunks en une passe.
**How to avoid:** Pour 20 chunks, le risque est faible. Si erreur, relancer le script (idempotent si on écrase `faiss_index/`). Pas besoin de retry logic pour Phase 2.
**Warning signs:** `MistralAPIStatusException: Status 429`.

### Pitfall 5: Divergence CHUNK_SIZE entre build et analyse

**What goes wrong:** Les chunks sont trop grands (>1000 chars) → embeddings moins précis, contexte trop dilué. Ou trop petits (<100 chars) → perte de contexte sémantique.
**Why it happens:** Mauvaise calibration initiale.
**How to avoid:** Les logs de validation montrent la taille et le contenu des chunks. CHUNK_SIZE=500 est calibré pour ce document (20 chunks sur 8700 chars = bonne granularité). Ajustable via `config.py` si l'aperçu révèle un problème.
**Warning signs:** Chunks qui coupent une phrase en deux, ou chunks trop courts (< 100 chars).

---

## Code Examples

### Pipeline complet minimal

```python
# Source: LangChain FAISS docs + MistralAIEmbeddings docs
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.vectorstores import FAISS
from langchain_mistralai import MistralAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP, FAISS_INDEX_PATH

# Charger + découper
raw_docs = PyPDFDirectoryLoader("assets/", recursive=True).load()
chunks = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
).split_documents(raw_docs)

# Embedder + indexer + sauvegarder
FAISS.from_documents(
    chunks,
    MistralAIEmbeddings(model=EMBEDDING_MODEL)
).save_local(FAISS_INDEX_PATH)
```

### Fichiers créés par save_local()

```
faiss_index/
├── index.faiss   # Index vectoriel binaire (FAISS)
└── index.pkl     # Métadonnées (page_content + metadata dict)
```

### Chargement en Phase 3 (app.py) — pour référence

```python
# Source: LangChain FAISS docs — load_local signature
# FAISS.load_local(folder_path, embeddings, index_name="index", *, allow_dangerous_deserialization=False)
vectorstore = FAISS.load_local(
    FAISS_INDEX_PATH,
    MistralAIEmbeddings(model=EMBEDDING_MODEL),
    allow_dangerous_deserialization=True  # Requis — source de confiance (local)
)
```

### Logs de validation (INDEX-04)

```python
# Afficher les N premiers chunks pour validation qualitative
n_preview = min(3, len(chunks))
for i in range(n_preview):
    print(f"--- Chunk {i+1} ({len(chunks[i].page_content)} chars) ---")
    print(chunks[i].page_content[:200])
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `PyPDF2` | `pypdf` | 2023 — PyPDF2 archivé | Migration triviale, même API |
| `DirectoryLoader(loader_cls=PyPDFLoader)` | `PyPDFDirectoryLoader(recursive=True)` | Disponible depuis langchain-community 0.1 | Plus concis pour les PDF |
| `FAISS.from_documents()` sans `save_local` | `save_local()` + commit Git | Décision projet | Nécessaire pour Streamlit Community Cloud |
| API key via `os.getenv()` explicite | `MistralAIEmbeddings()` lit `MISTRAL_API_KEY` automatiquement | langchain-mistralai 0.1+ | Moins de code boilerplate |

**Deprecated/outdated:**
- `PyPDF2` : archivé, remplacé par `pypdf`
- `langchain.document_loaders` (import direct) : déplacé dans `langchain_community.document_loaders`
- `langchain.vectorstores` (import direct) : déplacé dans `langchain_community.vectorstores`

---

## Open Questions

1. **Qualité d'extraction si d'autres formats sont ajoutés dans `assets/`**
   - What we know: `PyPDFDirectoryLoader` ne charge que les `.pdf` — les autres formats sont ignorés silencieusement
   - What's unclear: INDEX-01 dit "PDF et autres formats supportés" — Phase 2 couvre les PDF. Les autres formats sont en v2 (INDEX-V2-01)
   - Recommendation: Se limiter aux PDF pour Phase 2 — `PyPDFDirectoryLoader` est suffisant. Documenter dans les logs si un fichier non-PDF est présent.

2. **Comportement si `assets/` est vide**
   - What we know: `PyPDFDirectoryLoader` retourne une liste vide → `FAISS.from_documents([])` lève une erreur
   - What's unclear: Faut-il gérer explicitement ce cas edge ?
   - Recommendation: Ajouter une vérification `if not raw_docs: raise ValueError(...)` avec message clair.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Aucun framework de test (pas de tests automatisés pour ce script offline) |
| Config file | Aucun |
| Quick run command | `python build_index.py` (nécessite `MISTRAL_API_KEY` définie) |
| Full suite command | `python build_index.py && ls faiss_index/` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| INDEX-01 | `build_index.py` charge tous les fichiers `assets/` | smoke | `python -c "from langchain_community.document_loaders import PyPDFDirectoryLoader; d=PyPDFDirectoryLoader('assets/', recursive=True); print(len(d.load()), 'pages')"` | ✅ assets/ existe |
| INDEX-02 | `faiss_index/` créé avec `index.faiss` + `index.pkl` | smoke | `python build_index.py && ls faiss_index/` | ❌ Wave 0 (créer build_index.py) |
| INDEX-03 | `faiss_index/` visible par `git status` (non exclu) | smoke | `git check-ignore faiss_index/ 2>&1 \| grep -v "faiss_index" && echo "OK: not ignored"` | ✅ .gitignore créé Phase 1 |
| INDEX-04 | Logs affichent nb chunks + aperçu | smoke | `python build_index.py 2>&1 \| grep "chunks"` | ❌ Wave 0 (créer build_index.py) |

### Sampling Rate

- **Per task commit:** `python -c "from config import EMBEDDING_MODEL, FAISS_INDEX_PATH; print('config OK')"` (sans appel API)
- **Per wave merge:** `python build_index.py` (nécessite MISTRAL_API_KEY)
- **Phase gate:** Vérification manuelle des logs de validation + `git status` montre `faiss_index/` comme untracked

### Wave 0 Gaps

- [ ] `build_index.py` — couvre INDEX-01, INDEX-02, INDEX-04
- [ ] `MISTRAL_API_KEY` dans l'environnement — prérequis pour lancer `build_index.py`

*(Le `.gitignore`, `config.py`, et `requirements.txt` existent déjà depuis Phase 1)*

---

## Sources

### Primary (HIGH confidence)

- LangChain FAISS docs — `from_documents`, `save_local`, `load_local`: https://reference.langchain.com/v0.3/python/community/vectorstores/langchain_community.vectorstores.faiss.FAISS.html
- LangChain PyPDFLoader docs: https://reference.langchain.com/v0.3/python/community/document_loaders/langchain_community.document_loaders.pdf.PyPDFLoader.html
- LangChain MistralAIEmbeddings docs: https://reference.langchain.com/python/langchain-mistralai/embeddings/MistralAIEmbeddings
- Test direct du PDF `dossier_competences.pdf` avec `PyPDFDirectoryLoader` et `RecursiveCharacterTextSplitter` dans l'environnement local — résultats concrets et vérifiés

### Secondary (MEDIUM confidence)

- Inspection directe des signatures API via `inspect.signature()` — `save_local(folder_path, index_name="index")`, `load_local(folder_path, embeddings, ..., allow_dangerous_deserialization=False)`
- WebSearch LangChain FAISS patterns 2025 — cohérent avec les docs officiels

### Tertiary (LOW confidence)

- Recommandation `pdfplumber` comme alternative si extraction dégradée — non testé sur ce PDF spécifique

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — versions vérifiées localement, API testée, résultats concrets sur le PDF cible
- Architecture: HIGH — pipeline LangChain FAISS standard, testé, documenté officiellement
- Pitfalls: HIGH (pitfalls 1-3) / MEDIUM (pitfalls 4-5) — basés sur documentation officielle et tests locaux

**Research date:** 2026-03-13
**Valid until:** 2026-06-13 (90 jours — stack stable, API Mistral et LangChain FAISS sans changements majeurs attendus)
