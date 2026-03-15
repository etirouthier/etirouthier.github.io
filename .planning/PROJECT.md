# Chatbot CV — Dossier de Compétences

## What This Is

Application Streamlit hébergée sur Streamlit Community Cloud, exposant un chatbot RAG qui permet aux clients potentiels d'explorer interactivement un CV/portfolio (dossier_competence.pdf). L'utilisateur pose des questions en français et obtient des réponses contextualisées basées sur le contenu du document. Le chatbot est alimenté par l'API Mistral (free tier) et une base vectorielle FAISS locale.

## Core Value

Un client potentiel peut poser n'importe quelle question sur le profil professionnel et obtenir une réponse précise et contextuelle directement depuis le document — sans avoir à lire le PDF en entier.

## Requirements

### Validated

- ✓ Le chatbot répond aux questions en s'appuyant sur le contenu de dossier_competence.pdf — v1.0
- ✓ L'interface propose des questions prédéfinies au démarrage — v1.0
- ✓ Toutes les réponses sont en français — v1.0
- ✓ L'app est publique (pas d'authentification) — v1.0
- ✓ La base vectorielle FAISS est buildée via un script Python manuel — v1.0
- ✓ L'app est déployée et fonctionnelle sur Streamlit Community Cloud — v1.0
- ✓ L'API Mistral (free tier) est utilisée pour la génération de réponses — v1.0

### Active

(Définir avec `/gsd:new-milestone` pour v1.1)

### Out of Scope

- Authentification / mot de passe — app publique par choix
- Multi-langue — français uniquement
- Affichage des sources/extraits dans les réponses — interface épurée avec suggestions
- Mise à jour automatique de l'index FAISS — rebuild manuel intentionnel

## Context

**v1.0 shipped 2026-03-15** — 284 lignes Python, 4 phases, 5 plans, 38 commits.

Tech stack : Streamlit 1.55 · LangChain · FAISS-cpu · Mistral API (mistral-embed + mistral-small)

App live : https://etirouthierappio.streamlit.app/

- `build_index.py` — script offline à relancer manuellement après mise à jour du PDF
- `faiss_index/` — index commité dans git (filesystem éphémère sur Streamlit Cloud)
- `requirements-app.txt` — dépendances minimales pour le déploiement (7 packages)
- `requirements.txt` — environnement de dev complet (189 packages)

## Constraints

- **API**: Mistral free tier — limites de rate et de tokens à respecter
- **Hébergement**: Streamlit Community Cloud — pas de persistance de fichiers, FAISS doit être inclus dans le repo
- **Stack**: Python / Streamlit / LangChain / FAISS / Mistral API
- **Budget**: Gratuit (free tier uniquement)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| FAISS local (pas de vectorstore cloud) | Simplicité, pas de coût, rebuild manuel suffisant | ✓ Validé — fonctionne bien pour document stable |
| Mistral free tier | Pas de coût d'API | ✓ Validé — rate limits gérés via message d'erreur dans le chat |
| Streamlit Community Cloud | Déploiement gratuit, intégration native Streamlit | ✓ Validé — app publique déployée en < 1h |
| Rebuild index manuel | Contrôle explicite sur quand l'index est mis à jour | ✓ Validé — faiss_index/ commité dans git |
| EMBEDDING_MODEL centralisé dans config.py | Divergence silencieuse = résultats FAISS invalides | ✓ Critique — même valeur utilisée dans build et app |
| requirements-app.txt séparé | Streamlit Cloud n'a pas besoin des 189 packages dev | ✓ Bon pattern — 7 packages suffisants en prod |

---
*Last updated: 2026-03-15 after v1.0 milestone*
