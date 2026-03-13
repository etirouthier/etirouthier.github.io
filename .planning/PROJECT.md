# Chatbot CV — Dossier de Compétences

## What This Is

Application Streamlit hébergée sur Streamlit Community Cloud, exposant un chatbot RAG qui permet aux clients potentiels d'explorer interactivement un CV/portfolio (dossier_competence.pdf). L'utilisateur pose des questions en français et obtient des réponses contextualisées basées sur le contenu du document. Le chatbot est alimenté par l'API Mistral (free tier) et une base vectorielle FAISS locale.

## Core Value

Un client potentiel peut poser n'importe quelle question sur le profil professionnel et obtenir une réponse précise et contextuelle directement depuis le document — sans avoir à lire le PDF en entier.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Le chatbot répond aux questions en s'appuyant sur le contenu de dossier_competence.pdf
- [ ] L'interface propose des questions prédéfinies au démarrage ("Quelles sont vos principales compétences ?", "En quoi pouvez-vous m'aider sur mon projet ?")
- [ ] Toutes les réponses sont en français
- [ ] L'app est publique (pas d'authentification)
- [ ] La base vectorielle FAISS est buildée via un script Python manuel (à relancer après mise à jour du PDF)
- [ ] L'app est déployée et fonctionnelle sur Streamlit Community Cloud
- [ ] L'API Mistral (free tier) est utilisée pour la génération de réponses

### Out of Scope

- Authentification / mot de passe — app publique par choix
- Multi-langue — français uniquement
- Affichage des sources/extraits dans les réponses — interface épurée avec suggestions
- Mise à jour automatique de l'index FAISS — rebuild manuel intentionnel

## Context

- Le document source est `assets/dossier_competence.pdf` (CV + portfolio)
- La base FAISS est locale et versionnée avec le projet (ou ignorée selon la taille)
- Le script de build de l'index (`build_index.py` ou similaire) est lancé manuellement après chaque mise à jour du PDF
- Hébergement cible : Streamlit Community Cloud (gratuit), avec la clé API Mistral stockée dans les secrets Streamlit
- Le projet existant contient déjà du HTML pour un dossier de compétences — le chatbot vient en complément ou en remplacement

## Constraints

- **API**: Mistral free tier — limites de rate et de tokens à respecter
- **Hébergement**: Streamlit Community Cloud — pas de persistance de fichiers, FAISS doit être inclus dans le repo ou regénéré au démarrage
- **Stack**: Python / Streamlit / LangChain ou équivalent / FAISS / Mistral API
- **Budget**: Gratuit (free tier uniquement)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| FAISS local (pas de vectorstore cloud) | Simplicité, pas de coût, rebuild manuel suffisant | — Pending |
| Mistral free tier | Pas de coût d'API | — Pending |
| Streamlit Community Cloud | Déploiement gratuit, intégration native Streamlit | — Pending |
| Rebuild index manuel | Contrôle explicite sur quand l'index est mis à jour | — Pending |

---
*Last updated: 2026-03-13 after initialization*
