# Phase 7: Métadonnées & Contexte LLM — Research

**Researched:** 2026-03-16
**Domain:** LangChain document metadata enrichment + LLM context formatting
**Confidence:** HIGH

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| META-01 | Chaque chunk possède un champ `experience` dans ses métadonnées, dérivé du nom de fichier source | LangChain `Document.metadata` est un dict mutable — on itère sur `chunks` après `split_documents()` et on ajoute `doc.metadata["experience"]` depuis le mapping |
| META-02 | Le mapping filename → nom d'expérience est défini explicitement dans `build_index.py` (pas d'inférence fragile) | Un dict Python `EXPERIENCE_MAP` avec les 8 clés exactes (7 assets + PDF résumé) couvre tous les cas ; `os.path.basename(source)` sert de clé |
| GEN-01 | Le contexte injecté dans le LLM préfixe chaque chunk avec `[Expérience]\n<texte>` | Dans `app.py` ligne 118, remplacer `"\n\n".join(doc.page_content for doc in docs)` par une compréhension utilisant `doc.metadata.get("experience", "?")` |
| GEN-02 | Le prompt système indique au LLM de mentionner l'expérience source dans ses réponses quand c'est pertinent | Ajout d'une phrase à `SYSTEM_PROMPT` dans `app.py` — aucune dépendance externe |
</phase_requirements>

---

## Summary

Phase 7 est une modification chirurgicale de deux fichiers : `build_index.py` et `app.py`. Le vecteur de changement central est que LangChain expose `Document.metadata` comme un dict Python ordinaire, modifiable librement après le chargement et le découpage. Il n'y a donc aucune API spéciale à appeler : on enrichit les chunks en itérant dessus après `split_documents()` et en injectant `doc.metadata["experience"]` à partir d'un mapping dict explicite.

L'inspection directe de l'index existant révèle que le champ `source` est déjà peuplé par les loaders LangChain (ex: `"assets/01_decathlon.md"`, `"assets/06_these_sorbonne (1).md"`). Le mapping doit donc utiliser `os.path.basename(doc.metadata["source"])` comme clé — ce qui donne des clés prévisibles et stables. L'index actuel contient 97 chunks répartis sur 8 sources (7 fichiers `.md` + 1 PDF). Le nom de fichier sur disque pour la thèse est `06_these_sorbonne.md` (sans la parenthèse `(1)` que l'on voit dans l'index pkl actuel — à vérifier).

Côté `app.py`, la modification est d'une ligne (context assembly) + quelques mots dans `SYSTEM_PROMPT`. Aucune nouvelle dépendance Python n'est requise. L'index FAISS doit être **rebuilté et commité** après les changements de `build_index.py`, car les métadonnées sont sérialisées dans `index.pkl`.

**Recommandation principale:** Enrichir les métadonnées immédiatement après `split_documents()`, avant `FAISS.from_documents()`, avec un mapping dict couvrant les 8 sources connues (7 assets + PDF). Utiliser `os.path.basename` pour extraire la clé. Mettre à jour `app.py` pour formater le contexte et le prompt système.

---

## Standard Stack

### Core — déjà installé, aucune nouvelle dépendance

| Composant | Version/Source | Rôle | Statut |
|-----------|---------------|------|--------|
| `langchain_community.document_loaders` | existant | Charge docs, peuple `metadata["source"]` | Déjà utilisé |
| `langchain_text_splitters.RecursiveCharacterTextSplitter` | existant | Découpe en chunks, propagate metadata | Déjà utilisé |
| `langchain_community.vectorstores.FAISS` | existant | Sérialise chunks + metadata dans `index.pkl` | Déjà utilisé |
| `os.path.basename` | stdlib | Extrait le nom de fichier depuis le path complet | Aucune installation |

**Installation:** Aucune nouvelle dépendance — toute la stack est déjà présente.

---

## Architecture Patterns

### Pattern 1 : Enrichissement post-split (le seul pattern applicable)

**Ce que c'est:** Après `split_documents()`, itérer sur `chunks` et muter `doc.metadata` avant de passer à `FAISS.from_documents()`.

**Pourquoi post-split et pas pré-split:** `RecursiveCharacterTextSplitter.split_documents()` propage automatiquement les métadonnées du document parent vers chaque chunk enfant. On peut donc enrichir soit avant, soit après. Le pattern post-split est plus sûr : il garantit que tous les chunks ont le champ, y compris si le loader crée plusieurs docs pour un même fichier (comportement du `PyPDFDirectoryLoader` avec les pages PDF).

**Code pattern:**

```python
# Dans build_index.py — après split_documents(), avant FAISS.from_documents()

import os

EXPERIENCE_MAP = {
    "00_profil.md": "Profil",
    "01_decathlon.md": "Decathlon",
    "02_ssen.md": "SSEN",
    "03_energys.md": "Energys",
    "04_veolia.md": "Veolia",
    "05_grtgaz.md": "GRTgaz",
    "06_these_sorbonne.md": "Thèse Sorbonne",
    "dossier_competences.pdf": "Résumé",
}

for doc in chunks:
    source = doc.metadata.get("source", "")
    basename = os.path.basename(source)
    doc.metadata["experience"] = EXPERIENCE_MAP.get(basename, basename)
```

**Point d'attention — nom du fichier thèse:** L'index actuel contient `"assets/06_these_sorbonne (1).md"` comme source (avec `(1)` dans le nom), mais le fichier sur disque est `assets/06_these_sorbonne.md`. La discordance vient probablement d'un ancien état du repo. Lors du rebuild, `basename` sera `06_these_sorbonne.md` — la clé dans `EXPERIENCE_MAP` doit correspondre exactement au nom réel sur disque.

### Pattern 2 : Formatage du contexte LLM labellisé

**Ce que c'est:** Dans `app.py`, remplacer l'assemblage du contexte par une version qui préfixe chaque chunk avec son étiquette d'expérience.

**Code pattern:**

```python
# Dans app.py — ligne ~118 (remplacement de la ligne context = ...)
context = "\n\n".join(
    f"[{doc.metadata.get('experience', '?')}]\n{doc.page_content}"
    for doc in docs
)
```

### Pattern 3 : Mise à jour du SYSTEM_PROMPT

**Ce que c'est:** Ajouter une instruction au prompt système pour que le LLM exploite les étiquettes d'expérience.

**Code pattern:**

```python
# Dans app.py — ajout à SYSTEM_PROMPT
"Chaque extrait du contexte est préfixé par [NomExpérience] indiquant "
"l'expérience professionnelle dont il provient. "
"Mentionne l'expérience source dans tes réponses quand c'est pertinent."
```

### Anti-Patterns à éviter

- **Inférence regex sur le nom de fichier:** Extraire `"Decathlon"` depuis `"01_decathlon.md"` par regex ou capitalisation automatique — fragile face aux espaces, tirets, accents, parenthèses. Utiliser le mapping explicite (META-02).
- **Modifier les métadonnées des raw_docs avant split:** Techniquement fonctionne, mais la propagation vers les chunks dépend du comportement interne du splitter. Plus robuste de le faire sur `chunks`.
- **Patcher l'index.pkl existant sans rebuild:** La sérialisation FAISS inclut les métadonnées. Il n'y a pas d'API LangChain pour mettre à jour les métadonnées d'un index existant sans rebuild. Seul un rebuild complet garantit la cohérence.

---

## Don't Hand-Roll

| Problème | Ne pas construire | Utiliser à la place | Pourquoi |
|----------|------------------|--------------------|----|
| Propagation metadata vers les chunks | Copie manuelle de metadata depuis raw_docs | `split_documents()` le fait automatiquement | Comportement documenté LangChain |
| Persistance de l'index avec les nouvelles metadata | Sérialisation pickle manuelle | `vectorstore.save_local()` existant | Déjà dans build_index.py |
| Parsing du nom de fichier | Regex complexe | `os.path.basename()` + dict lookup | Stdlib, sans ambiguité |

---

## Common Pitfalls

### Pitfall 1 : Nom de fichier avec espace ou caractère spécial

**Ce qui se passe:** `os.path.basename("assets/06_these_sorbonne (1).md")` retourne `"06_these_sorbonne (1).md"` — clé non trouvée dans `EXPERIENCE_MAP` si la clé est `"06_these_sorbonne.md"`.

**Pourquoi:** L'index pkl actuel montre le path avec `(1)` car l'ancien fichier s'appelait ainsi. Après le renommage sur disque, le rebuild produira le basename sans `(1)`. La clé dans le mapping doit correspondre au nom **réel sur disque au moment du rebuild**.

**Comment éviter:** Vérifier `os.path.basename()` sur les fichiers réels avant d'écrire le mapping. La validation post-rebuild (logs) montre la valeur exacte de `metadata["source"]`.

**Signe d'alerte:** Le log de validation affiche `experience=06_these_sorbonne.md` (la clé brute au lieu du nom mappé) — indique que `EXPERIENCE_MAP.get(basename, basename)` a utilisé le fallback.

### Pitfall 2 : Oublier de rebuilter l'index après build_index.py

**Ce qui se passe:** `app.py` appelle `doc.metadata.get("experience", "?")` mais les chunks chargés depuis l'ancien `index.pkl` n'ont pas le champ — la valeur retournée est `"?"` pour tous les chunks.

**Pourquoi:** Les métadonnées sont sérialisées dans `index.pkl`. Modifier `build_index.py` sans relancer le script ne change pas l'index sur disque.

**Comment éviter:** Le plan doit inclure explicitement l'étape `python build_index.py` + commit de `faiss_index/` comme étape obligatoire.

### Pitfall 3 : MISTRAL_API_KEY absente lors du rebuild

**Ce qui se passe:** `MistralAIEmbeddings` lève une exception à l'étape 3 du build — rebuild échoue.

**Comment éviter:** Le rebuild nécessite que `MISTRAL_API_KEY` soit présente dans l'environnement (`.env` ou variable d'environnement). Ce n'est pas une contrainte nouvelle — c'est le comportement documenté de `build_index.py`.

### Pitfall 4 : PDF résumé sans champ `experience` cohérent

**Ce qui se passe:** Les 20 chunks du PDF `dossier_competences.pdf` reçoivent une étiquette d'expérience. Si le PDF est un résumé global, l'étiquette `"Résumé"` est la plus neutre. Si on l'oublie dans le mapping, ces chunks auront `experience="dossier_competences.pdf"` (fallback).

**Comment éviter:** Le mapping doit couvrir explicitement `"dossier_competences.pdf"`.

---

## Code Examples

### État actuel de l'assemblage du contexte (app.py ligne 118)

```python
# Actuel — SANS étiquette d'expérience
context = "\n\n".join(doc.page_content for doc in docs)
```

### État cible de l'assemblage du contexte

```python
# Cible — AVEC étiquette d'expérience (GEN-01)
context = "\n\n".join(
    f"[{doc.metadata.get('experience', '?')}]\n{doc.page_content}"
    for doc in docs
)
```

### SYSTEM_PROMPT actuel (app.py lignes 17-23)

```python
SYSTEM_PROMPT = (
    "Tu es un assistant professionnel qui répond aux questions sur le profil "
    "et les compétences d'Etienne Routhier, basé uniquement sur les documents fournis.\n"
    "Tu réponds toujours en français, avec un ton professionnel et bienveillant.\n"
    "Si la question dépasse le contenu des documents fournis, réponds explicitement "
    "que tu ne disposes pas de cette information — ne génère pas de contenu inventé."
)
```

### SYSTEM_PROMPT cible (GEN-02 — ajout d'une phrase)

```python
SYSTEM_PROMPT = (
    "Tu es un assistant professionnel qui répond aux questions sur le profil "
    "et les compétences d'Etienne Routhier, basé uniquement sur les documents fournis.\n"
    "Tu réponds toujours en français, avec un ton professionnel et bienveillant.\n"
    "Si la question dépasse le contenu des documents fournis, réponds explicitement "
    "que tu ne disposes pas de cette information — ne génère pas de contenu inventé.\n"
    "Chaque extrait du contexte est préfixé par [NomExpérience] indiquant l'expérience "
    "professionnelle dont il provient. Mentionne l'expérience source dans tes réponses "
    "quand c'est pertinent."
)
```

---

## Inventory des sources connues

Issu de l'inspection directe de `faiss_index/index.pkl` (état avant rebuild) :

| Source (path complet) | Basename actuel | Chunks actuels | Experience cible |
|-----------------------|----------------|---------------|-----------------|
| `assets/00_profil.md` | `00_profil.md` | 4 | `"Profil"` |
| `assets/01_decathlon.md` | `01_decathlon.md` | 12 | `"Decathlon"` |
| `assets/02_ssen.md` | `02_ssen.md` | 10 | `"SSEN"` |
| `assets/03_energys.md` | `03_energys.md` | 11 | `"Energys"` |
| `assets/04_veolia.md` | `04_veolia.md` | 13 | `"Veolia"` |
| `assets/05_grtgaz.md` | `05_grtgaz.md` | 11 | `"GRTgaz"` |
| `assets/06_these_sorbonne (1).md` | `06_these_sorbonne.md` (après renommage) | 16 | `"Thèse Sorbonne"` |
| `assets/resume/dossier_competences.pdf` | `dossier_competences.pdf` | 20 | `"Résumé"` |

**Total actuel:** 97 chunks. Le rebuild produira un compte identique ou proche.

---

## Validation Architecture

### Test Framework

| Propriété | Valeur |
|-----------|--------|
| Framework | Aucun framework de test détecté dans le repo |
| Config file | Aucun (`pytest.ini`, `jest.config.*` absents) |
| Quick run command | `python build_index.py 2>&1 \| grep "experience"` (smoke test manuel) |
| Full suite command | Rebuild + inspection manuelle des logs |

### Phase Requirements → Test Map

| Req ID | Comportement | Type de test | Commande automatisée | Fichier existant |
|--------|-------------|-------------|---------------------|-----------------|
| META-01 | Chaque chunk a `experience` dans `metadata` | Smoke (inspection log) | `python -c "import pickle; data=pickle.load(open('faiss_index/index.pkl','rb')); docs=list(data[0]._dict.values()); assert all('experience' in d.metadata for d in docs), 'FAIL'; print('META-01 OK')"` | ❌ Wave 0 |
| META-02 | Le mapping couvre les 8 sources | Inspection code | Lecture de `build_index.py` — vérification visuelle du dict `EXPERIENCE_MAP` | ❌ Wave 0 |
| GEN-01 | Context string formaté `[Exp]\nchunk` | Smoke (print) | Vérification visuelle des logs build_index.py — ou test unitaire du format | ❌ Wave 0 |
| GEN-02 | SYSTEM_PROMPT mentionne les étiquettes | Inspection code | Lecture de `app.py` — vérification visuelle | ❌ Wave 0 |

### Sampling Rate

- **Par commit:** `python -c "import pickle; data=pickle.load(open('faiss_index/index.pkl','rb')); docs=list(data[0]._dict.values()); missing=[d.metadata.get('source') for d in docs if 'experience' not in d.metadata]; print('Missing experience:', missing or 'NONE')"` (< 5 secondes)
- **Phase gate:** Rebuild complet + vérification log + smoke test pickle

### Wave 0 Gaps

- [ ] Aucun fichier de test à créer — les critères de succès sont vérifiables via logs build_index.py et inspection du pkl
- [ ] Le smoke test META-01 ci-dessus peut être ajouté directement en fin de `build_index.py` comme assertion de validation

---

## Périmètre et contraintes

### Ce qui est IN SCOPE (v1.2)

- Ajout de `EXPERIENCE_MAP` dict dans `build_index.py`
- Enrichissement de `doc.metadata["experience"]` après `split_documents()`
- Modification de l'assemblage du contexte dans `app.py`
- Ajout d'une phrase au `SYSTEM_PROMPT` dans `app.py`
- Rebuild et commit de `faiss_index/`

### Ce qui est OUT OF SCOPE (extrait de REQUIREMENTS.md)

- Filtrage FAISS par expérience
- Métadonnées période/dates
- Affichage des sources dans l'UI

### Ordre d'exécution obligatoire

1. Modifier `build_index.py` (META-01, META-02)
2. Modifier `app.py` (GEN-01, GEN-02)
3. Rebuilter l'index : `python build_index.py`
4. Vérifier les logs de validation
5. Commiter `faiss_index/index.faiss` + `faiss_index/index.pkl`

L'ordre 1→2 peut être inversé, mais le rebuild (étape 3) doit venir après l'étape 1.

---

## Open Questions

1. **Nom exact du fichier thèse sur disque**
   - Ce qu'on sait: L'index pkl actuel a `"assets/06_these_sorbonne (1).md"` mais `ls assets/` retourne `06_these_sorbonne.md` (sans `(1)`)
   - Ce qui est ambigu: Si le fichier a été renommé entre la création de l'index et maintenant, le rebuild utilisera le nom actuel sur disque
   - Recommandation: Le planner doit inclure une étape de vérification `ls assets/` avant d'écrire la clé du mapping — la clé doit correspondre au fichier réel

2. **Étiquette pour le PDF résumé**
   - Ce qu'on sait: `dossier_competences.pdf` est un résumé global (4 pages, contenu générique)
   - Ce qui est ambigu: L'étiquette `"Résumé"` ou `"Dossier de compétences"` — les deux sont neutres
   - Recommandation: `"Résumé"` est court et clair, cohérent avec le contexte

---

## Sources

### Primary (HIGH confidence — inspection directe du code)

- `build_index.py` — flux complet de construction de l'index, structure des loaders
- `app.py` — ligne exacte d'assemblage du contexte (ligne 118), `SYSTEM_PROMPT` existant
- `faiss_index/index.pkl` — inspection directe : structure réelle des métadonnées, 8 sources, 97 chunks
- `assets/` — listing réel des fichiers sur disque

### Secondary (MEDIUM confidence)

- LangChain docs : `Document.metadata` est un `dict` mutable propagé par les splitters — comportement standard documenté, confirmé par l'inspection du pkl existant qui montre déjà `source`, `page`, etc. dans les métadonnées

### Tertiary (LOW confidence — non vérifiée pour cette version précise)

- Le comportement de propagation de `split_documents()` est stable depuis LangChain 0.1 — comportement attendu mais version exacte installée non vérifiée

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — tout le code existant est inspectable directement
- Architecture: HIGH — deux modifications de code déterministes, pas de choix d'API ambiguë
- Pitfalls: HIGH — identifiés par inspection directe du pkl et du code existant

**Research date:** 2026-03-16
**Valid until:** Stable — pas de dépendances externes nouvelles, changements purement internes au code projet
