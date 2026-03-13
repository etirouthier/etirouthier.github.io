# Pitfalls: RAG Chatbot CV — Streamlit + FAISS + Mistral free tier

**Researched:** 2026-03-13
**Confidence:** MEDIUM-HIGH (patterns stables sur ce stack)

---

## Pitfall 1 — Index FAISS absent sur Streamlit Community Cloud ⚠️ CRITIQUE

**Problème :** Streamlit Community Cloud n'a pas de filesystem persistant entre les déploiements. Si l'index FAISS n'est pas commité dans le repo, l'app plante au démarrage à chaque deploy.

**Signes d'alerte :**
- L'app tourne en local mais plante dès le premier déploiement
- Erreur `FileNotFoundError: faiss_index/` dans les logs Streamlit

**Prévention :**
- Commiter le dossier `faiss_index/` dans le repo Git
- Vérifier que `faiss_index/` n'est PAS dans `.gitignore`
- Ajouter un check au démarrage : `if not os.path.exists("faiss_index/"): st.error("Index manquant")`

**Phase concernée :** Phase setup/déploiement — décider dès le début, avant d'écrire l'app.

---

## Pitfall 2 — Clé API Mistral exposée dans le repo ⚠️ CRITIQUE

**Problème :** Un commit accidentel de la clé API dans un repo public la compromet définitivement (même après suppression du commit).

**Signes d'alerte :**
- `.streamlit/secrets.toml` n'est pas dans `.gitignore`
- La clé est hardcodée dans `app.py` ou `config.py`

**Prévention :**
- Ajouter `.streamlit/secrets.toml` dans `.gitignore` dès l'init du repo
- Utiliser `st.secrets["MISTRAL_API_KEY"]` — jamais de variable d'environnement hardcodée
- Configurer les secrets dans le dashboard Streamlit Community Cloud

**Phase concernée :** Avant tout commit.

---

## Pitfall 3 — Rate limits Mistral free tier non gérés ⚠️ CRITIQUE

**Problème :** Le free tier Mistral a des limites de requêtes/minute et tokens/jour. Sans gestion des erreurs 429, l'app plante avec une stack trace incompréhensible pour l'utilisateur.

**Signes d'alerte :**
- `RateLimitError` ou HTTP 429 dans les logs sans message utilisateur
- L'app marche en test mais plante en demo avec plusieurs questions rapides

**Prévention :**
- Wrapper tous les appels Mistral dans `try/except` avec message FR : `"Limite d'appels atteinte, réessayez dans quelques secondes."`
- Afficher avec `st.warning()` ou dans `st.chat_message("assistant")`

**Phase concernée :** Développement du core RAG.

---

## Pitfall 4 — Taille de chunks mal calibrée pour un CV/dossier de compétences

**Problème :** Le chunk size par défaut LangChain (1000 chars, pas d'overlap) est optimisé pour des documents longs. Un dossier de compétences a des sections courtes et denses — trop gros = bruit, trop petit = perte de contexte.

**Signes d'alerte :**
- Les réponses sont génériques ou récupèrent des informations non pertinentes
- La similarité cosine des chunks récupérés est faible (< 0.5)

**Prévention :**
- Utiliser `chunk_size=400-600`, `chunk_overlap=50-100`
- Valider les chunks avant de builder l'index : imprimer les 5 premiers chunks pour vérifier qu'ils ont du sens
- Tester avec `vectorstore.similarity_search("compétences principales", k=3)` et vérifier les résultats

**Phase concernée :** Build de l'index.

---

## Pitfall 5 — Modèle d'embedding différent entre build et query ⚠️ CRITIQUE

**Problème :** Si le modèle utilisé pour vectoriser le PDF lors du build est différent de celui utilisé à la query, les distances cosine sont sans signification — l'app répond n'importe quoi.

**Signes d'alerte :**
- Les réponses semblent aléatoires ou hors-sujet
- Changement de modèle entre les scripts sans rebuild de l'index

**Prévention :**
- Définir `EMBEDDING_MODEL = "mistral-embed"` dans `config.py` et importer depuis les deux scripts
- Ne jamais changer le modèle d'embedding sans rebuilder l'index entier

**Phase concernée :** Avant d'écrire la première ligne du pipeline.

---

## Pitfall 6 — FAISS rechargé à chaque re-run Streamlit

**Problème :** Streamlit re-exécute le script à chaque interaction utilisateur. Sans cache, `FAISS.load_local()` recharge l'index 100Mo à chaque message.

**Signes d'alerte :**
- L'app est lente (1-3s de latence supplémentaire par message)
- Utilisation CPU anormalement haute

**Prévention :**
```python
@st.cache_resource
def load_vectorstore():
    return FAISS.load_local("faiss_index/", embeddings, allow_dangerous_deserialization=True)
```

**Phase concernée :** Développement de l'app.

---

## Pitfall 7 — `allow_dangerous_deserialization` oublié

**Problème :** LangChain >=0.2 exige `allow_dangerous_deserialization=True` lors du chargement d'un index FAISS depuis pickle. Sans ça, exception au démarrage.

**Prévention :**
```python
FAISS.load_local("faiss_index/", embeddings, allow_dangerous_deserialization=True)
```

**Phase concernée :** Développement de l'app.

---

## Pitfall 8 — Modèle d'embedding non multilingue

**Problème :** Un projet en français utilisant un modèle d'embedding English-only aura de très mauvaises performances de récupération.

**Prévention :**
- Utiliser `mistral-embed` (natif multilingue) — recommandé pour cohérence avec le LLM
- Alternative : `paraphrase-multilingual-MiniLM-L12-v2` (sentence-transformers) si on veut éviter les appels API pour les embeddings

**Phase concernée :** Sélection du stack avant le build.

---

## Pitfall 9 — Extraction PDF de mauvaise qualité

**Problème :** Si le PDF est scanné (image) ou utilise des tableaux complexes, `pypdf` peut extraire du texte incohérent. Les chunks résultants sont du bruit.

**Signes d'alerte :**
- Texte extrait avec caractères spéciaux, coupures au milieu de mots
- Questions sur des infos présentes dans le PDF ne trouvent pas de réponse

**Prévention :**
- Valider l'extraction avant de builder l'index : `print(loader.load()[0].page_content[:500])`
- Si le PDF est scanné : utiliser `pdfminer.six` ou `pymupdf` (fitz) qui gèrent mieux les PDFs complexes

**Phase concernée :** Build de l'index — valider avant de commencer.

---

## Pitfall 10 — Cold start Streamlit Community Cloud non anticipé

**Problème :** L'app dort après inactivité (free tier). Le premier visiteur attend 10-30s. Sans explication, cela ressemble à une app cassée.

**Prévention :**
- Ajouter un spinner de chargement au démarrage : `with st.spinner("Chargement du chatbot...")`
- Optionnel : message explicatif "L'app se réveille, merci de patienter quelques secondes"

**Phase concernée :** Polish avant déploiement.

---

## Résumé des risques par phase

| Phase | Risque principal | Priorité |
|-------|-----------------|---------|
| Setup | Clé API dans `.gitignore`, décision index bundled vs rebuilt | CRITIQUE |
| Build index | Validation extraction PDF, chunk size, modèle embedding cohérent | HAUTE |
| App core | `@st.cache_resource`, gestion 429, `allow_dangerous_deserialization` | HAUTE |
| Déploiement | Index commité dans repo, secrets Streamlit configurés, cold start UX | CRITIQUE |
