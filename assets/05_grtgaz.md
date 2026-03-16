# Expérience : Data Scientist — GRTgaz (via Sia Partners)

**Période** : ~2021 (8 mois) — première mission post-doctorat
**Cabinet** : Sia Partners
**Client** : GRTgaz
**Rôle** : Data Scientist

---

## Projet

Évaluation de l'intérêt d'un système de prévision de consommation de gaz multi-échelle, combinant prédictions à la maille des points unitaires et cohérence avec les agrégats régionaux.

---

## Contexte

GRTgaz est l'acteur majeur du transport de gaz en France, gestionnaire du réseau de pipelines et responsable de l'équilibrage du réseau (mettre autant de gaz en entrée qu'en sortie). Dans ce cadre, GRTgaz fournit des prévisions de consommation aux acteurs de la distribution.

Le réseau est composé d'environ **3 000 points de raccordement** avec les réseaux de ville ou d'usine (points unitaires). Le système historique produit des prévisions régionales agrégées, puis les désagrège à la maille des points unitaires. La question posée : serait-il plus pertinent de prédire directement à la maille unitaire, puis de réconcilier les prévisions avec les agrégats régionaux ?

La mission est une **étude d'opportunité** — pas de mise en production, mais une évaluation rigoureuse pour orienter une décision d'investissement.

---

## Missions et réalisations

### 1. Benchmark de méthodes de séries temporelles à la maille unitaire

Évaluation de la qualité des prédictions pour un ensemble de méthodes de séries temporelles appliquées aux 3 000 points unitaires individuellement : XGBoost, modèles sklearn, modèles statistiques classiques. Benchmark comparatif sur des métriques de précision adaptées au contexte gaz.

### 2. Évaluation du gain multi-échelle — réconciliation hiérarchique

Estimation du gain apporté par un **système de prévision hiérarchique** : prédictions unitaires réconciliées pour garantir la cohérence avec les agrégats régionaux. L'enjeu de la réconciliation hiérarchique est de s'assurer que la somme des prévisions unitaires est cohérente avec la prévision régionale — un problème classique en prévision multi-échelle (méthodes bottom-up, top-down, ou réconciliation optimale type MinT).

### 3. Estimation des coûts de build et de run

Évaluation des coûts d'infrastructure et de développement associés aux différentes solutions : coût de construction (build), coût d'exploitation récurrente (run), complexité de maintenance.

### 4. Analyse business et conclusion

**Résultat clé** : les coûts d'un système multi-échelle se sont révélés élevés dans le contexte régulatoire spécifique de GRTgaz. L'équilibrage du réseau est incentivé par la **CRE (Commission de Régulation de l'Énergie)**, mais le calcul de l'incentive se fait à la **maille régionale agrégée** — et non à la maille des points unitaires. GRTgaz opère en monopole régulé : il n'y a pas de réalité marché qui valoriserait directement une meilleure précision à la maille fine.

La conclusion de l'étude : le gain technique de la prédiction multi-échelle ne se justifiait pas économiquement dans ce cadre régulatoire. C'est un exemple de cas où la qualité du modèle ne suffit pas — la valeur d'une amélioration dépend du contexte dans lequel elle s'insère.

---

## Ce que cette expérience révèle

Cette mission, première post-doctorat, illustre la capacité à articuler une analyse technique rigoureuse avec une lecture business et régulatoire. Savoir conclure qu'un investissement technique n'est pas justifié — en le démontrant par les chiffres — est une compétence aussi importante que de savoir construire le modèle.

Elle témoigne également d'une montée en compétence rapide sur les séries temporelles appliquées à des problèmes industriels à grande échelle (3 000 séries simultanées), directement après une thèse en bioinformatique — confirmant la capacité de transfert méthodologique d'un domaine à l'autre.

---

## Environnement technique

XGBoost, Scikit-learn, Docker, Python, Git
