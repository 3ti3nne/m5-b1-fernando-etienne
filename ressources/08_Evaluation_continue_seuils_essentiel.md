# Évaluation continue & seuils bloquants — Mini-cours

> Brief associé : M5-B2
> Durée de lecture : ~30 min
> Pré-requis : CI GitHub Actions (mini-cours 03), métriques de classif (M1)

## Pourquoi cette techno ?

Votre CI teste le **code**. Mais un dev peut casser le **modèle** sans casser
le code : un preprocessing modifié par erreur, et le F1 passe de 0.61 à 0.45 —
ça part en prod sans alerte. L'**évaluation continue** comble ce trou : à
chaque release, on recalcule les métriques modèle sur un **jeu de référence
figé**, et on **bloque la release** si une métrique passe sous un seuil.

C'est le geste C9 (amélioration continue) côté garde-fou. Pas de détection de
drift ici (c'est M6) : on reste sur des **seuils statiques** sur des métriques
globales, branchés dans la CI via un **code retour non-zéro**.

## Concepts clés

- **Jeu de référence (`reference_set.csv`)** : un sous-échantillon **figé** du
  holdout, versionné. Figé = comparable d'une release à l'autre. On le regénère
  seulement si la population change (et on le documente).
- **Deux baselines, à ne pas confondre.** La **baseline communiquée** est ce
  qu'on a annoncé au client (métriques du holdout M1 complet). Le **golden
  run** est la mesure faite sur **votre** jeu de référence, au moment où vous
  le gelez. Le garde-fou compare au **golden run** — jamais à la baseline
  communiquée. Les deux jeux n'ont ni la même taille ni la même composition :
  l'écart entre eux mesure une **différence de population**, pas une
  dégradation du modèle.
- **Stratégies de seuil** : **absolu** (« F1 ≥ 0.55 quoi qu'il arrive »),
  **relatif** (« pas plus de 5 pts sous le golden run »), **hybride** (les deux).
  L'hybride est le plus robuste.
- **Bruit de mesure** : un jeu de référence est un échantillon, donc ses
  métriques ont une incertitude. Un seuil relatif **plus petit que ce bruit**
  se déclenche tout seul. On le mesure par **bootstrap** et on prend au moins
  **2 σ** (cf. plus bas).
- **Code retour** : le script sort `0` si OK, **`1` si violation**. GitHub
  Actions interprète `exit 1` comme un échec → release bloquée. Un `print` ne
  bloque rien.
- **Idempotence** : `random_state` fixé partout → 2 exécutions donnent le même
  résultat. Attention : l'idempotence dit que la mesure ne bouge pas d'un run à
  l'autre. Elle ne dit **rien** sur le bruit d'échantillonnage du jeu — ce sont
  deux problèmes différents.

## Dimensionner la tolérance : le bootstrap en 10 lignes

```python
import numpy as np, pandas as pd
from sklearn.metrics import roc_auc_score

rng = np.random.default_rng(42)
y, proba = y_ref.to_numpy(), model.predict_proba(X_ref)[:, 1]
scores = [roc_auc_score(y[i], proba[i])
          for i in (rng.integers(0, len(y), len(y)) for _ in range(500))]
sigma = np.std(scores)
print(f"sigma = {sigma:.4f}  ->  tolerance mini = {2 * sigma:.3f}")
```

On retire un échantillon de même taille, avec remise, 500 fois : la dispersion
obtenue **est** l'incertitude de la mesure. Sur 500 lignes, comptez un σ de
l'ordre de 0.02-0.03 sur le ROC-AUC — donc une tolérance relative de 0.03 est
**sous le bruit**, et bloquera des releases parfaitement saines.

> 💡 Conséquence de conception : sur la classe rare, le bruit vient du **nombre
> de positifs**, pas du nombre de lignes. Sur-représenter la classe coûteuse
> dans un jeu d'**évaluation** (par ex. 250/250 au lieu de 408/92) divise
> presque par deux le σ du recall. Un jeu de référence n'est pas un échantillon
> de production : c'est un instrument de mesure, on le conçoit pour être stable.

## Exemple minimal qui tourne

```python
import sys
from sklearn.metrics import f1_score

THRESHOLDS = {"f1_macro": {"absolute_min": 0.55, "max_drop_vs_baseline": 0.03}}

def check(metrics, baseline):
    violations = []
    for name, rule in THRESHOLDS.items():
        v = metrics[name]
        if v < rule["absolute_min"]:
            violations.append(f"{name}={v} < {rule['absolute_min']}")
        if baseline.get(name) and baseline[name] - v > rule["max_drop_vs_baseline"]:
            violations.append(f"{name} a chuté > {rule['max_drop_vs_baseline']}")
    return violations

violations = check({"f1_macro": 0.50}, {"f1_macro": 0.61})
print(violations)
sys.exit(1 if violations else 0)   # ← bloque la CI
```

## Exercice guidé

Prouvez que le garde-fou marche :
0. Gelez le golden run : `evaluate_model.py --freeze-baseline` → commitez
   `data/reference_baseline.json`.
1. Lancez votre `evaluate_model.py --release-tag ok` → doit sortir **exit 0**,
   avec des écarts **exactement nuls** vs le golden run. Si ce n'est pas le cas
   sur un modèle inchangé, votre baseline n'est pas la bonne.
2. Ajoutez un mode `--degrade` qui **désaligne X et y** (ou casse une feature)
   → relancez → doit lister des violations et sortir **exit 1**.
3. Branchez l'étape `evaluate-model` dans `ci.yml` (`needs: test`) et poussez
   une dégradation : le workflow doit passer **rouge**.

## Pièges fréquents

| Piège | Conséquence |
|---|---|
| Seuil « magique » non justifié (« 0.65 ça me va ») | Indéfendable devant le client / le jury |
| `print` au lieu de `sys.exit(1)` | La release dégradée part quand même |
| Reference_set non figé (regénéré à chaque run) | Métriques non comparables, seuils inutiles |
| `random_state` oublié | Résultats non idempotents, faux positifs/négatifs |
| Jamais tester le chemin rouge | On découvre en prod que le garde-fou ne bloque pas |
| **Comparer au holdout M1 au lieu du golden run** | Le garde-fou mesure un écart de population et bloque des releases saines |
| **Tolérance relative sous le bruit du jeu** | Rouge aléatoire ; l'équipe finit par désactiver le garde-fou |
| Jeu de référence changé sans regeler le golden run | Même effet : on compare deux populations |

| Symptôme | Cause probable |
|---|---|
| La CI reste verte malgré une dégradation | Script ne renvoie pas `exit 1`, ou étape pas branchée |
| Résultats différents à chaque run | `random_state` non fixé / reference_set instable |
| Seuil contesté en revue | Pas de justification chiffrée vs golden run |
| **Rouge alors que rien n'a été touché** | Baseline mesurée sur une autre population, ou tolérance < bruit |

## Pour aller plus loin

- scikit-learn metrics : https://scikit-learn.org/stable/modules/model_evaluation.html
- GitHub Actions — job status & exit codes : https://docs.github.com/actions/writing-workflows
- Continuous evaluation (concept) : https://ml-ops.org/content/mlops-principles

## Vérification (checklist apprenant)

- [ ] Mon `reference_set.csv` est figé et versionné.
- [ ] Mon golden run est gelé dans `data/reference_baseline.json` et versionné.
- [ ] Sur un modèle inchangé, l'écart au golden run est **nul** (pas « petit »).
- [ ] J'ai mesuré le σ de mon jeu et ma tolérance relative est ≥ 2 σ.
- [ ] Chaque seuil est **justifié** par rapport au golden run.
- [ ] Le script sort **exit 1** sur dégradation (testé au moins une fois).
- [ ] L'étape `evaluate-model` bloque réellement la release en CI.
- [ ] Mes résultats sont idempotents (`random_state` fixé).
