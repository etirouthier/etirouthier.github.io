# Expérience : Data Scientist — Veolia (via Sia Partners)

**Période** : ~2021 – 2022 (10 mois)
**Cabinet** : Sia Partners
**Client** : Veolia Groupe
**Rôle** : Data Scientist

---

## Projet

Création d'un produit de recommandation d'optimisation de la consommation électrique des bâtiments : modèle de référence, détection d'anomalies, exposition via API, mise en production.

---

## Contexte

Veolia est un leader mondial de la gestion des ressources environnementales qui assure également la gestion énergétique de certains bâtiments. Dans ce cadre, Veolia Groupe a souhaité développer des outils digitaux permettant d'identifier les anomalies de consommation électrique et d'estimer les gains potentiels d'optimisation.

Le produit repose sur une logique en deux temps : d'abord estimer ce que devrait consommer un bâtiment dans des conditions normales (modèle de référence), puis détecter les écarts anormaux par rapport à cette référence (détection d'anomalie). Les anomalies détectées alimentent des recommandations d'optimisation avec estimation des gains associés.

---

## Missions et réalisations

### 1. Modèle de consommation de référence — XGBoost

Création d'un modèle estimant la consommation électrique normale d'un bâtiment, utilisé comme baseline pour la détection d'anomalies. Le modèle est un **XGBoost** entraîné sur les variables :
- **Météo** (température extérieure, ensoleillement)
- **Taille du bâtiment** (surface, volume)

Ce modèle de référence permet de comparer la consommation observée à la consommation attendue dans les mêmes conditions, indépendamment des variations saisonnières ou climatiques.

### 2. Détection d'anomalies de consommation — Seuillage statistique non paramétrique

Création de **trois modèles de détection d'anomalie** de consommation énergétique, basés sur une approche de seuillage statistique après estimation des distributions conditionnelles.

L'approche est **non paramétrique** : plutôt que de supposer une forme de distribution a priori (gaussienne par exemple), les **distributions conditionnelles** de la consommation sont estimées par la **méthode de Laplace**. Cette estimation permet de définir des seuils d'anomalie robustes qui s'adaptent aux conditions réelles de chaque bâtiment, sans hypothèse forte sur la forme de la distribution.

Trois modèles ont été développés, couvrant vraisemblablement différentes granularités temporelles ou types d'anomalies (ponctuelles, persistantes, dérive progressive).

### 3. API REST temps réel — FastAPI sur Cloud Run

Conception et développement d'une **API REST** avec FastAPI, déployée sur **Google Cloud Run**, appelée en temps réel. L'API expose :
- Les prédictions du modèle de référence
- Les scores d'anomalie
- Les estimations de gains potentiels

La validation des entrées/sorties est gérée avec **Pydantic**. Cloud Run assure un déploiement serverless — l'infrastructure scale automatiquement selon la charge sans gestion de serveurs.

### 4. Framework d'expérimentation pré-industriel

Création d'une **librairie interne d'expérimentation** permettant aux data scientists de travailler dès le début avec du code à qualité industrielle, sans attendre la phase de mise en production. Le framework inclut :
- Typage et validation des données avec **Pydantic**
- Tests unitaires systématiques
- Hooks **pre-commit** (formatage, linting) avec Black et Flake8
- Structure de projet reproductible

L'objectif est de réduire la dette technique accumulée pendant les phases d'expérimentation et de faciliter le passage en production. C'est un investissement en ingénierie qui bénéficie à l'ensemble des projets data de l'équipe.

---

## Architecture de la solution

```
Données bâtiment (météo, taille, consommation historique)
        ↓
Modèle XGBoost — consommation de référence
        ↓
Estimation distributions conditionnelles (méthode de Laplace)
        ↓
3 modèles de détection d'anomalie (seuillage statistique)
        ↓
API REST FastAPI / Pydantic — Cloud Run (temps réel)
        ↓
Front-end recommandations + estimation des gains
```

---

## Ce que cette expérience révèle

Cette mission illustre la capacité à construire un produit data complet de bout en bout : modélisation statistique, détection d'anomalie, API de serving, déploiement cloud. Le choix d'une approche non paramétrique pour la détection d'anomalie (distributions conditionnelles par méthode de Laplace) témoigne d'une rigueur statistique — refuser les hypothèses simplificatrices quand les données permettent de faire mieux.

La création du framework d'expérimentation pré-industriel révèle une préoccupation pour la qualité du code dès les phases amont — une compétence rare chez les data scientists qui travaillent souvent dans des environnements de prototypage découplés de la production.

---

## Environnement technique

XGBoost, FastAPI, Pydantic, Python, Docker, Cloud Run (GCP), MLflow, GitHub
