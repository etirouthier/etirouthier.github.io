# Phase 1: Setup & Configuration - Research

**Researched:** 2026-03-13
**Domain:** Python project structure, Git security, pip dependency management, Streamlit secrets
**Confidence:** HIGH

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| SETUP-01 | `.gitignore` exclut `.streamlit/secrets.toml` et tout fichier de clé API | Pattern standard Git + Streamlit Community Cloud — section "Gitignore Patterns" ci-dessous |
| SETUP-02 | `config.py` centralise les constantes partagées (modèle embedding, chunk size, chunk overlap, k) importables depuis tout script | Pattern module Python standard — section "Architecture Patterns" ci-dessous |
| SETUP-03 | `requirements.txt` liste toutes les dépendances avec versions fixées, installable sans erreur sur Streamlit Community Cloud | Versions vérifiées via research project (SUMMARY.md) — section "Standard Stack" ci-dessous |
</phase_requirements>

---

## Summary

Phase 1 est entièrement une phase de configuration — aucune logique applicative, aucun appel réseau. Les trois livrables sont : un `.gitignore` correct, un `config.py` avec les bonnes constantes, et un `requirements.txt` avec les versions fixées compatibles Streamlit Community Cloud.

La recherche projet (SUMMARY.md) a déjà résolu les décisions clés : stack défini, versions confirmées, pitfalls documentés. Cette phase est de la mécanique pure. Le seul risque réel est d'omettre une entrée dans `.gitignore` ou de laisser une version non-fixée dans `requirements.txt`. Ces erreurs ne sont pas détectables au runtime — elles créent des problèmes silencieux (secret exposé dans l'historique Git, dépendance qui casse au prochain deploy).

**Primary recommendation:** Créer les trois fichiers dans l'ordre — `.gitignore` d'abord (avant tout secret), `config.py` ensuite (établit les constantes), `requirements.txt` en dernier (consolide toutes les dépendances des phases suivantes).

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| streamlit | >=1.35.0 | Framework UI et hébergement Community Cloud | Plateforme cible du déploiement — version minimale pour `st.chat_input` stable |
| mistralai | >=1.0.0 | SDK Mistral officiel (LLM + embeddings) | Réécriture majeure mi-2024 — les versions <1.0 ont une API incompatible |
| langchain-mistralai | >=0.1.0 | Intégration LangChain pour Mistral | Nécessaire pour `MistralAIEmbeddings` et `ChatMistralAI` via LCEL |
| langchain | >=0.2.0 | Orchestration RAG via LCEL | LCEL remplace `RetrievalQA` legacy — seule version supportée activement |
| langchain-core | >=0.2.0 | Composants de base LangChain | Dépendance directe de langchain-mistralai |
| langchain-community | >=0.2.0 | Wrappers FAISS pour LangChain | Contient `FAISS.from_documents()` et `FAISS.load_local()` |
| faiss-cpu | >=1.8.0 | Vectorstore local — recherche par similarité | Pas de GPU requis, adapté à un seul document |
| pypdf | >=4.0.0 | Parsing PDF | Remplace PyPDF2 déprécié — activement maintenu |
| python-dotenv | >=1.0.0 | Chargement `.env` local (optionnel, dev only) | Pas strictement nécessaire si on utilise `st.secrets` — inclure pour flexibilité dev |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| langchain-text-splitters | >=0.2.0 | Découpage des documents en chunks | Séparé de `langchain` depuis 0.2 — nécessaire pour Phase 2 |
| numpy | >=1.26.0 | Dépendance transitive FAISS | Pinned pour éviter incompatibilité |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| faiss-cpu | chromadb, qdrant | FAISS = pas de service externe, commitable dans Git — seul choix viable pour Streamlit Community Cloud |
| pypdf | pdfminer.six, pdfplumber | pypdf est plus simple et suffisant pour texte linéaire — pdfplumber utile si tableaux complexes (Phase 2 decidera) |
| langchain-mistralai | mistralai direct | LangChain abstractions simplifient le pipeline RAG — justifié pour ce projet |

**Installation:**

```bash
pip install streamlit>=1.35.0 mistralai>=1.0.0 langchain-mistralai>=0.1.0 langchain>=0.2.0 langchain-core>=0.2.0 langchain-community>=0.2.0 langchain-text-splitters>=0.2.0 faiss-cpu>=1.8.0 pypdf>=4.0.0
pip freeze > requirements.txt
```

> Note: générer le `requirements.txt` depuis un environnement propre avec `pip freeze` après installation garantit des versions fixées. Ne pas écrire les versions manuellement — utiliser ce que l'environnement produit.

---

## Architecture Patterns

### Recommended Project Structure

```
/workspaces/etienne.routhier/
├── .gitignore               # SETUP-01 — secrets et fichiers locaux exclus
├── config.py                # SETUP-02 — constantes partagées
├── requirements.txt         # SETUP-03 — dépendances avec versions fixées
├── build_index.py           # Phase 2 — script offline d'indexation
├── app.py                   # Phase 3 — application Streamlit
├── assets/
│   └── resume               # Document source existant
├── faiss_index/             # Phase 2 — index commité dans Git
│   ├── index.faiss
│   └── index.pkl
└── .streamlit/
    └── secrets.toml         # LOCAL UNIQUEMENT — exclu par .gitignore
```

### Pattern 1: .gitignore pour projet Streamlit avec secrets

**What:** Fichier `.gitignore` qui protège les secrets Mistral et exclut les artefacts Python locaux, tout en permettant le commit de `faiss_index/`.

**When to use:** Toujours — à créer avant tout fichier de secret.

```gitignore
# Source: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management
# Secrets Streamlit — jamais commités
.streamlit/secrets.toml

# Variables d'environnement locales
.env
*.env

# Python
__pycache__/
*.py[cod]
*.egg-info/
.eggs/
dist/
build/
*.egg

# Environnements virtuels
venv/
.venv/
env/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo

# macOS
.DS_Store

# NOTE: faiss_index/ est INTENTIONNELLEMENT absent de .gitignore
# Il doit être commité pour être disponible sur Streamlit Community Cloud
```

### Pattern 2: config.py — module de constantes partagées

**What:** Module Python importable depuis tous les scripts du projet. Définit une seule fois chaque constante critique.

**When to use:** Toujours — importer depuis `build_index.py` et `app.py`, jamais dupliquer les valeurs.

```python
# config.py
# Source: pattern standard Python — constante partagée entre scripts

# Modèle d'embedding — DOIT être identique entre build_index.py et app.py
# Toute divergence rend l'index inutilisable sans erreur explicite
EMBEDDING_MODEL = "mistral-embed"

# Modèle de génération
LLM_MODEL = "mistral-small-latest"

# Paramètres de chunking (calibrés pour un document court et dense)
CHUNK_SIZE = 500       # caractères — ajustable en Phase 2 selon qualité chunks
CHUNK_OVERLAP = 50     # caractères — chevauchement pour continuité du contexte

# Nombre de chunks récupérés par requête
K_RETRIEVED = 4        # chunks — compromis précision/contexte pour Mistral free tier

# Chemin de l'index FAISS
FAISS_INDEX_PATH = "faiss_index"
```

### Pattern 3: requirements.txt avec versions fixées

**What:** Fichier de dépendances avec versions exactes (opérateur `==`) pour reproductibilité sur Streamlit Community Cloud.

**When to use:** Toujours — les versions non-fixées peuvent casser silencieusement lors d'un deploy.

```
# requirements.txt
# Généré depuis un environnement propre — versions fixées pour reproductibilité
streamlit==1.43.0
mistralai==1.5.0
langchain==0.3.20
langchain-core==0.3.45
langchain-community==0.3.19
langchain-mistralai==0.2.7
langchain-text-splitters==0.3.6
faiss-cpu==1.10.0
pypdf==5.4.0
numpy==2.2.3
```

> Attention: ces versions sont illustratives. Les versions exactes doivent être générées par `pip freeze` dans l'environnement de développement réel.

### Anti-Patterns to Avoid

- **Versions non-fixées dans requirements.txt** (`streamlit>=1.35.0` au lieu de `streamlit==1.43.0`) : Streamlit Community Cloud réinstalle les dépendances à chaque deploy — une version majeure peut casser l'app sans avertissement.
- **`faiss_index/` dans `.gitignore`** : L'index doit être commité — le filesystem Streamlit Community Cloud est éphémère, l'index ne peut pas être reconstruit au runtime.
- **Constantes dupliquées entre `build_index.py` et `app.py`** : Si `EMBEDDING_MODEL` diffère entre build et query, FAISS retourne des résultats silencieusement invalides (dimensions incompatibles ou résultats incohérents).
- **`secrets.toml` commité même une fois** : L'historique Git conserve ce fichier pour toujours — une exposition même brève nécessite une rotation de clé API.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Gestion des secrets | Variable d'environnement custom, fichier JSON parsé manuellement | `st.secrets` (Streamlit natif) | Intégration directe avec le dashboard Streamlit Community Cloud — zéro configuration supplémentaire |
| Validation du requirements.txt | Script de vérification custom | `pip install -r requirements.txt` dans un venv propre | La commande standard est le test de validation |

**Key insight:** Phase 1 est de la configuration pure — les "don't hand-roll" sont inexistants car on n'écrit pas de logique applicative.

---

## Common Pitfalls

### Pitfall 1: `faiss_index/` ajouté par erreur au `.gitignore`

**What goes wrong:** L'app démarre sur Streamlit Community Cloud mais crashe immédiatement avec `FileNotFoundError: faiss_index/ not found`.

**Why it happens:** Un `.gitignore` générique (template GitHub Python) exclut parfois les dossiers d'index ou les fichiers `.pkl`. Le développeur copie ce template sans vérifier.

**How to avoid:** Vérifier explicitement après création du `.gitignore` que `faiss_index/` n'est pas exclu — `git status` après création du dossier doit lister ses fichiers comme "untracked".

**Warning signs:** `git status` ne montre pas `faiss_index/` après sa création.

### Pitfall 2: `secrets.toml` exposé dans l'historique Git

**What goes wrong:** La clé API Mistral est exposée dans l'historique Git — même après suppression du fichier, elle reste accessible dans les commits précédents.

**Why it happens:** Le développeur crée `secrets.toml` avant d'ajouter l'entrée dans `.gitignore`, puis fait un `git add .`.

**How to avoid:** Créer `.gitignore` en premier absolu — avant de créer `.streamlit/secrets.toml`. Vérifier avec `git status` que le fichier n'apparaît pas comme "untracked" avant tout commit.

**Warning signs:** `git status` liste `.streamlit/secrets.toml` dans "Untracked files".

### Pitfall 3: Divergence silencieuse du modèle d'embedding

**What goes wrong:** L'index est construit avec `mistral-embed`, mais `app.py` utilise un nom de modèle différent (typo, version différente). FAISS ne lève pas d'erreur mais retourne des résultats sans sens.

**Why it happens:** La valeur est définie en deux endroits différents. Une modification dans un script n'est pas propagée à l'autre.

**How to avoid:** `EMBEDDING_MODEL` défini une seule fois dans `config.py`, importé par les deux scripts. Tout changement se propage automatiquement.

**Warning signs:** Résultats de similarité FAISS qui semblent aléatoires ou non-pertinents malgré un index valide.

### Pitfall 4: `requirements.txt` incomplet (dépendances transitives manquantes)

**What goes wrong:** L'app fonctionne en local mais crashe sur Streamlit Community Cloud avec `ModuleNotFoundError`.

**Why it happens:** Le développeur liste les dépendances directes mais pas les dépendances transitives. En local, elles sont déjà installées depuis un contexte précédent.

**How to avoid:** Générer `requirements.txt` via `pip freeze` depuis un environnement vierge (venv fraîchement créé), pas manuellement.

**Warning signs:** `pip install -r requirements.txt` dans un venv propre lève des erreurs.

---

## Code Examples

### Import de config.py depuis un script

```python
# build_index.py ou app.py
from config import EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP, K_RETRIEVED, FAISS_INDEX_PATH

# Utilisation directe — aucune duplication de valeur
embeddings = MistralAIEmbeddings(model=EMBEDDING_MODEL)
```

### Lecture de la clé API via st.secrets

```python
# app.py — jamais de clé API hardcodée
# Source: https://docs.streamlit.io/develop/concepts/connections/secrets-management
import streamlit as st

mistral_api_key = st.secrets["MISTRAL_API_KEY"]
```

### Structure de .streamlit/secrets.toml (local uniquement)

```toml
# .streamlit/secrets.toml — EXCLU DU GIT
# Équivalent du dashboard Streamlit Community Cloud pour le dev local
MISTRAL_API_KEY = "votre-clé-ici"
```

### Validation du .gitignore

```bash
# Après création de .streamlit/secrets.toml, vérifier qu'il n'apparaît pas
git status
# Attendu: secrets.toml N'APPARAIT PAS dans "Untracked files"

# Après création du dossier faiss_index/ (Phase 2), vérifier qu'il apparaît bien
git status
# Attendu: faiss_index/ APPARAIT dans "Untracked files" ou "Changes not staged"
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `PyPDF2` | `pypdf` | 2023 — PyPDF2 archivé | Migration triviale, même API de base |
| `mistralai` <1.0 | `mistralai` >=1.0.0 | mi-2024 | API client entièrement réécrite — incompatible |
| `RetrievalQA` LangChain | LCEL (`langchain` >=0.2) | 2024 | Pattern legacy déprécié, migration vers LCEL |
| `pip install X` sans version | `pip freeze > requirements.txt` | Bonne pratique stable | Reproductibilité garantie sur tout environnement |

**Deprecated/outdated:**

- `PyPDF2` : archivé, ne pas utiliser — `pypdf` est le successeur officiel
- `mistralai` <1.0.0 : API incompatible avec la version actuelle
- `langchain` <0.2.0 : `RetrievalQA` et chaînes legacy dépréciés

---

## Open Questions

1. **Versions exactes disponibles dans l'environnement de déploiement**
   - What we know: Streamlit Community Cloud utilise pip — toute version publique est disponible
   - What's unclear: La version Python exacte de l'environnement de déploiement (3.11 recommandé)
   - Recommendation: Spécifier `python_requires` dans un fichier de config si problème, ou tester avec `python_version` dans requirements (non-standard pip)

2. **`langchain-text-splitters` comme dépendance séparée**
   - What we know: Séparé de `langchain` depuis 0.2.0
   - What's unclear: Certaines versions de `langchain-community` l'importent automatiquement ou non
   - Recommendation: L'inclure explicitement dans `requirements.txt` pour éviter toute ambiguïté

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Aucun framework de test existant — Phase 1 est configuration pure |
| Config file | Aucun — pas de tests automatisés pour cette phase |
| Quick run command | `pip install -r requirements.txt && python -c "import config; print('OK')"` |
| Full suite command | Validation manuelle via checklist (voir ci-dessous) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SETUP-01 | `.gitignore` exclut `.streamlit/secrets.toml` | smoke | `git check-ignore -v .streamlit/secrets.toml` | ❌ Wave 0 (créer .gitignore) |
| SETUP-02 | `config.py` importable avec toutes les constantes | smoke | `python -c "from config import EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP, K_RETRIEVED, FAISS_INDEX_PATH; print('OK')"` | ❌ Wave 0 (créer config.py) |
| SETUP-03 | `requirements.txt` installable sans erreur | smoke | `pip install -r requirements.txt` (dans venv propre) | ❌ Wave 0 (créer requirements.txt) |

### Sampling Rate

- **Per task commit:** `python -c "from config import EMBEDDING_MODEL; print(EMBEDDING_MODEL)"`
- **Per wave merge:** `pip install -r requirements.txt && python -c "from config import EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP, K_RETRIEVED; print('All constants OK')"`
- **Phase gate:** Les trois success criteria vérifiés manuellement avant passage à Phase 2

### Wave 0 Gaps

- [ ] `.gitignore` — couvre SETUP-01
- [ ] `config.py` — couvre SETUP-02
- [ ] `requirements.txt` — couvre SETUP-03
- [ ] `.streamlit/secrets.toml` (local, jamais commité) — pour valider l'exclusion SETUP-01

*(Tous les livrables de cette phase sont des créations from scratch — aucune infrastructure de test préexistante)*

---

## Sources

### Primary (HIGH confidence)

- Documentation officielle Streamlit — Secrets management: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management
- Documentation officielle Streamlit — Community Cloud filesystem: https://docs.streamlit.io/deploy/streamlit-community-cloud
- Research SUMMARY.md du projet (2026-03-13) — stack et versions validés

### Secondary (MEDIUM confidence)

- Pattern Python standard `config.py` — pratique universelle, aucune source unique
- GitHub .gitignore template Python officiel — base pour les exclusions Python standard

### Tertiary (LOW confidence)

- Versions illustratives dans les exemples de `requirements.txt` — doivent être générées par `pip freeze` dans l'environnement réel

---

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH — versions issues de la recherche projet déjà validée contre la documentation officielle
- Architecture: HIGH — patterns de configuration Python/Git/Streamlit standards et documentés
- Pitfalls: HIGH — identifiés dans la recherche projet et confirmés par la documentation Streamlit Community Cloud

**Research date:** 2026-03-13
**Valid until:** 2026-06-13 (90 jours — stack stable, pas de changements API majeurs attendus)
