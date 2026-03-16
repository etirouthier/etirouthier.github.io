# Expérience : Data Scientist — Decathlon (via Wivoo / Wavestone)

**Période** : ~2023 – 2025 (1 an 8 mois)
**Cabinet** : Wivoo, filiale de Wavestone spécialisée dans les méthodes produit
**Rôle** : Data Scientist embedé dans une équipe produit interne Decathlon

---

## Projet

Améliorer le modèle de prévision de la demande au service de la supply chain, en intégrant la réponse causale aux facteurs externes (météo, événements) et en améliorant l'estimation des incertitudes.

---

## Contexte

Decathlon est un distributeur sportif mondial avec un modèle unique fondé sur des marques propriétaires et une grande intégration de la chaîne de valeur. Ce modèle génère des enjeux forts de gestion de la chaîne d'approvisionnement : Decathlon conçoit, produit et distribue ses propres produits, ce qui rend la précision des prévisions de demande critique pour éviter les ruptures et les surstocks.

Un produit digital interne fournit chaque semaine aux planneurs des prédictions de demande à la maille continentale. Etienne a rejoint l'équipe produit pour améliorer la précision du modèle, sa sensibilité aux facteurs externes et sa capacité à estimer les incertitudes.

---

## L'équipe produit

L'équipe était constituée de : 2 Product Managers, 8 Data Scientists, 4 ML Engineers, 1 Data Engineer, 2 Data Analysts, 1 Tech Lead. Etienne travaillait en tant que Data Scientist embedé, en méthode produit (Agile/Scrum), au sein de cette équipe pluridisciplinaire.

---

## Missions et réalisations

### 1. Modèle causal météo et événements

Développement d'un modèle répondant de façon **causale** à la météo et aux événements extérieurs. L'enjeu n'était pas seulement d'améliorer la précision statistique, mais d'éviter que le modèle reproduise mécaniquement les patterns météo passés — ce qui nuisait à l'acceptation du modèle par les planneurs.

**Résultat** : amélioration de **2 points de WAPE** sur les SKUs météo-sensibles.

Production d'une **table de sensibilité météo par famille de produits**, permettant à l'équipe d'identifier quels segments bénéficient le plus de la modélisation météo.

### 2. Système de mélange d'experts en production

Déploiement d'un **estimateur optimal en ligne** pour intégrer le nouveau modèle météo avec le modèle de prévision existant. Les poids de mélange sont mis à jour à chaque pas de temps en fonction des performances relatives des deux modèles — ce qui permet une transition progressive et robuste sans rupture pour les utilisateurs.

### 3. Impact collectif de l'équipe

Les travaux de l'ensemble de l'équipe sur la durée ont permis d'obtenir :
- **-10 points de WAPE** sur le modèle de prévision global
- **-10 jours de durée de vie moyenne du stock** — un indicateur business direct traduisant une meilleure rotation et moins d'immobilisation de capital

### 4. Veille modèles de fondation

Veille active sur les **modèles de fondation pour les séries temporelles** (notamment Chronos 2) pour évaluer leur capacité à intégrer des co-variables externes. Évaluation de leur pertinence pour le cas d'usage Decathlon.

### 5. Vision long terme du produit (discovery)

Appui à la réflexion sur les évolutions futures du produit :
- **Gestion automatique des stocks** : estimation des incertitudes de prévision pour alimenter un système de calcul automatique des niveaux de stock de sécurité.
- **Scénarisation avant saison** : travail de discovery sur l'estimation de l'impact du prix et du nombre de magasins sur les ventes, pour permettre aux équipes de simuler des scénarios avant le lancement d'une saison.

---

## Ce que cette expérience révèle

Cette mission illustre la capacité à travailler en environnement produit structuré (Agile, grande équipe pluridisciplinaire) sur un système de prévision critique à grande échelle. Elle combine expertise en séries temporelles, compréhension des enjeux supply chain, et sens du produit — avec un impact business mesurable et concret (-10 jours de stock).

Le choix d'un estimateur en ligne pour le mélange d'experts témoigne d'une approche pragmatique : plutôt qu'un modèle monolithique, une architecture modulaire qui s'adapte en continu aux conditions réelles.

---

## Environnement technique

Databricks, Nixtla, Statsmodels, Python, Pytest, GitHub, PySpark
