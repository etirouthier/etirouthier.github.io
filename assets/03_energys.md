# Expérience : Data Scientist — Energys (via Sia Partners)

**Période** : ~2022 (6 mois)
**Cabinet** : Sia Partners
**Client** : Energys
**Rôle** : Data Scientist

---

## Projet

Conception d'un jumeau numérique d'un bâtiment de bureaux pour modéliser sa réponse thermique et optimiser sa consommation d'énergie à confort égal.

---

## Contexte

Energys est une PME spécialisée dans la gestion thermique des bâtiments — elle fournit les logiciels et les personnels nécessaires pour piloter les systèmes de climatisation et de chauffage. Dans l'objectif de proposer une gestion automatique et optimisée des bâtiments, la réponse thermique d'un bâtiment à une commande (chauffage ou climatisation) doit être modélisée.

La mission portait sur un **bâtiment de bureaux test**, particulièrement bien instrumenté : capteurs de température dans toutes les salles, mesure d'ensoleillement, comptage du nombre de personnes présentes. Ce niveau d'instrumentation a permis une modélisation fine, mais représente aussi une limite à la généralisation — le passage à l'échelle sur des bâtiments moins instrumentés reste un défi.

Le projet visait à concevoir un jumeau numérique comme **première étape de R&D** d'un logiciel complet de gestion automatique.

---

## Missions et réalisations

### 1. Collecte et compréhension des données

Collecte, nettoyage et analyse exploratoire des données issues des capteurs :
- Températures par salle et par étage
- Commandes du système de chauffage
- Ensoleillement
- Occupation (nombre de personnes)

### 2. Revue bibliographique des méthodes de modélisation thermique

Revue des approches existantes pour la modélisation thermique des bâtiments, aboutissant au choix de l'**analogie électrique** (modèle RC) comme approche la mieux adaptée au compromis précision / nombre de paramètres / interprétabilité.

### 3. Jumeau numérique — State Space Model à 3 zones

Modélisation thermique du bâtiment par **analogie électrique** : la chaleur est traitée comme un flux électrique, les murs comme des résistances, les masses thermiques comme des capacités. Ce formalisme conduit naturellement à un **state space model**.

Le bâtiment est modélisé en **3 zones correspondant aux 3 étages**. Les paramètres du modèle (résistances, capacités thermiques) sont estimés par **optimisation bayésienne** sur les données historiques des capteurs.

### 4. Optimisation sous contrainte — CVXPY / HiGHS

Une fois le jumeau numérique calibré, les commandes de chauffage sont optimisées sous contraintes via **CVXPY** (framework de programmation convexe) avec le solveur **HiGHS** :

**Contraintes :**
- Température moyenne ≥ 20°C pendant les heures d'ouverture (confort)
- Puissance maximale du système de chauffage (contrainte physique)

**Objectif :** minimiser la consommation d'énergie sur l'horizon de planification.

**Résultat :** environ **20% de réduction de consommation énergétique** dans les conditions du bâtiment test, à confort égal.

### 5. Limites et passage à l'échelle

La performance du modèle repose sur la qualité et la densité de l'instrumentation du bâtiment test (température par salle, ensoleillement, occupation). Le passage à l'échelle sur des bâtiments moins bien instrumentés est un défi identifié : les paramètres du state space model ne peuvent pas être estimés avec la même précision si les données de capteurs sont rares ou bruitées.

---

## Ce que cette expérience révèle

Cette mission illustre la capacité à mobiliser des méthodes issues de la physique (analogie électrique, state space model) pour résoudre un problème data science — une approche hybride entre modélisation mécaniste et apprentissage des paramètres. L'optimisation bayésienne pour la calibration et CVXPY pour l'optimisation opérationnelle forment un pipeline complet de bout en bout.

La réduction de 20% de consommation est un résultat concret, mais la lucidité sur les conditions de sa reproductibilité (instrumentation dense) témoigne d'une maturité dans l'évaluation des solutions — distinguer ce qui fonctionne en conditions idéales de ce qui est déployable à grande échelle.

---

## Environnement technique

Python, CVXPY, HiGHS, R, Docker, GitHub
