# Expérience : Doctorant Data Scientist — Sorbonne Université

**Période** : 2018 – 2021 (3 ans 4 mois)
**Financement** : Bourse de l'ENS Paris-Saclay
**Cadre** : Projet scientifique international GP-write

---

## Projet

Prédiction par deep learning de la densité en nucléosomes sur le génome de la levure, et conception de séquences d'ADN synthétiques à densité contrôlée.

---

## Contexte scientifique

Le projet GP-write est une collaboration scientifique internationale dont l'objectif à long terme est la conception de génomes synthétiques fonctionnels. Le fonctionnement d'un génome dépend en grande partie de ses interactions avec les protéines. Parmi ces interactions, le positionnement des nucléosomes joue un rôle central : les nucléosomes sont des complexes protéiques qui permettent de compacter l'ADN et participent à la régulation génique en contrôlant l'accessibilité des séquences.

La levure (*S. cerevisiae*) est l'organisme modèle de référence pour l'étude des nucléosomes. Modéliser la densité en nucléosomes à partir de la séquence d'ADN est une étape nécessaire à la conception de génomes synthétiques fonctionnels.

---

## Approche technique

### 1. Modèle de prédiction — CNN sur séquences ADN

Un réseau de neurones convolutif (CNN) a été conçu et entraîné pour prédire la densité en nucléosomes à partir de la séquence d'ADN brute. Les CNN sont particulièrement adaptés aux séquences biologiques car ils capturent les motifs locaux (k-mers) qui influencent le positionnement des nucléosomes.

### 2. Conception de séquences synthétiques

Le modèle de prédiction a ensuite été utilisé comme fonction de score pour concevoir des séquences d'ADN synthétiques à densité en nucléosomes contrôlée. Deux approches d'optimisation ont été explorées :
- **Monte Carlo** : évolution stochastique des séquences vers le minimum d'énergie (écart entre densité souhaitée et densité prédite).
- **GAN (Generative Adversarial Network)** : génération de séquences synthétiques par apprentissage adversarial.

### 3. Validation expérimentale

Les séquences synthétiques conçues computationnellement ont été synthétisées et testées expérimentalement. La densité en nucléosomes mesurée expérimentalement correspond à la densité prédite par le réseau — ce qui valide à la fois le modèle prédictif et la méthode de conception.

Cette validation expérimentale permet de poser des questions théoriques sur le code nucléosomal : dans quelle mesure la séquence d'ADN détermine-t-elle le positionnement des nucléosomes ?

---

## Librairie open source — keras_dna

Publication d'une librairie Python open source **keras_dna** disponible sur **PyPI** (~25 stars GitHub), permettant de mettre en forme les données génomiques pour l'entraînement de réseaux de neurones. La librairie gère les formats standards de la bioinformatique :
- Séquences ADN (fichiers FASTA)
- Données de positionnement des nucléosomes (MNase-seq)
- Données d'expression génique (RNA-seq)
- Données de liaison protéine-ADN (ChIP-seq)

---

## Publications scientifiques

Participation à la rédaction de **7 articles scientifiques** au cours de la thèse, totalisant environ **25 citations**.

---

## Missions

- Conception et entraînement d'un CNN pour prédire la densité en nucléosomes à partir de séquences ADN.
- Développement d'algorithmes de conception de séquences synthétiques (Monte Carlo, GAN) à densité contrôlée.
- Validation expérimentale des séquences conçues computationnellement.
- Création et publication de la librairie open source **keras_dna** pour la mise en forme de données génomiques.
- Rédaction et co-rédaction de 7 articles scientifiques.

---

## Environnement technique

Keras, TensorFlow, Python, Bash, Git, formats bioinformatiques (FASTA, MNase-seq, RNA-seq, ChIP-seq)

---

## Ce que cette expérience révèle

Cette thèse démontre une capacité à mener un projet de recherche de bout en bout sur 3 ans : formulation d'une problématique scientifique, développement d'une solution deep learning, validation expérimentale, publication. Elle atteste également d'une capacité à produire des outils réutilisables (keras_dna) et à contribuer à une communauté scientifique internationale.

### Continuité méthodologique avec le travail actuel

Les méthodes développées en thèse entretiennent des liens profonds avec les problématiques data science actuelles, au-delà du changement de domaine :

**Deep learning sur données structurées séquentielles** : entraîner un CNN sur une séquence d'ADN et entraîner un réseau sur une série temporelle sont structurellement le même problème — extraire des dépendances locales dans une séquence ordonnée. Les architectures transformers désormais utilisées en prévision de séries temporelles (Chronos, TimeGPT) sont les héritières directes de cette famille de modèles.

**Méthodes de Monte Carlo** : en thèse, Monte Carlo était utilisé pour faire évoluer des séquences vers un minimum d'énergie — c'est-à-dire explorer un espace de configurations et trouver les états rares. C'est exactement le cadre de l'estimation de risque en supply chain : les méthodes Monte Carlo permettent d'échantillonner des scénarios de demande extrêmes, d'estimer les queues de distribution, et de quantifier l'incertitude sur les stocks de sécurité. Le changement est celui du domaine d'application, pas de la structure mathématique.
