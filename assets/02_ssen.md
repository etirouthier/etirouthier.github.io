# Expérience : Machine Learning Engineer — SSEN (via Sia Partners)

**Période** : ~2022 (4 mois)
**Cabinet** : Sia Partners
**Client** : Scottish & Southern Electricity Networks (SSEN)
**Rôle** : Machine Learning Engineer

---

## Projet

Mise en production d'un modèle de prédiction des dégâts provoqués par les tempêtes sur le réseau électrique écossais, et exposition de ses prédictions via une API REST utilisée en réunion de gestion de crise.

---

## Contexte

SSEN est le gestionnaire du réseau électrique écossais (Scottish & Southern Electricity Networks). Lors d'événements météorologiques extrêmes (tempêtes), anticiper l'impact sur le réseau est critique pour organiser les équipes d'intervention et prioriser les actions.

Dans le cadre d'une collaboration avec l'**université de Glasgow**, un modèle de machine learning prédisant l'impact des tempêtes sur le réseau avait été développé côté recherche. La mission consistait à industrialiser ce modèle : le mettre en production, stocker ses prédictions, et les exposer via une plateforme numérique utilisée lors des réunions de gestion de crise.

---

## Périmètre de la mission

Le modèle de prédiction avait été conçu par l'université de Glasgow — Etienne n'est pas intervenu sur sa conception. La valeur ajoutée de la mission est entièrement côté **ingénierie de mise en production** : rendre un modèle de recherche exploitable, fiable et accessible en conditions opérationnelles.

Le front-end de la plateforme de crise était géré par une équipe séparée, à partir des endpoints exposés.

---

## Missions et réalisations

### 1. API REST de serving — FastAPI

Conception et développement d'une **API REST** avec FastAPI pour exposer les prédictions pré-calculées stockées en base de données. L'API exposait deux types de ressources :
- Des **tables de données** (contexte réseau, historique événements)
- Des **prédictions ML** issues du modèle de l'université de Glasgow

Tous les endpoints sont typés et validés avec **Pydantic**, garantissant la robustesse des échanges avec le front-end tiers.

### 2. Gestion de la base de données et migrations

Mise en place de la couche de persistance avec **SQLAlchemy** (ORM) et gestion des migrations de schéma avec **Alembic**. Cette approche permet de faire évoluer le schéma de la base sans perte de données ni interruption de service — essentiel dans un contexte opérationnel de gestion de crise.

### 3. Mise en production sur Google Cloud Composer

Déploiement du modèle et orchestration des pipelines de calcul des prédictions sur **Google Cloud Composer** (Airflow managé sur GCP). Les prédictions sont calculées en amont et stockées en base, ce qui garantit des temps de réponse de l'API indépendants du temps d'inférence du modèle.

---

## Architecture de la solution

```
Modèle ML (université de Glasgow)
        ↓
Pipeline Airflow (Cloud Composer) — calcul des prédictions
        ↓
Base de données (SQLAlchemy / Alembic)
        ↓
API REST FastAPI / Pydantic — endpoints typés
        ↓
Front-end plateforme de crise (équipe tierce)
        ↓
Réunions de gestion de crise SSEN
```

---

## Ce que cette expérience révèle

Cette mission illustre la compétence de **translation recherche → production** : prendre un modèle développé en contexte académique et le rendre opérationnel dans un environnement critique. C'est une compétence distincte de la conception du modèle elle-même, qui requiert une maîtrise de l'ingénierie logicielle (API, ORM, migrations, orchestration) et une compréhension des contraintes opérationnelles (disponibilité, temps de réponse, évolutivité du schéma).

Le choix d'une architecture de prédictions pré-calculées plutôt que d'un scoring en temps réel est une décision d'ingénierie délibérée : elle découple la disponibilité de l'API des contraintes d'inférence du modèle, ce qui est particulièrement pertinent dans un contexte de gestion de crise où la fiabilité prime.

---

## Environnement technique

FastAPI, Pydantic, SQLAlchemy, Alembic, Airflow, Google Cloud Composer (GCP), Docker, Python, GitHub
