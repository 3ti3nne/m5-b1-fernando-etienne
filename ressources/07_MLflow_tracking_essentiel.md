# MLflow tracking — Mini-cours

> Brief associé : M5-B2
> Durée de lecture : ~30 min
> Pré-requis : un modèle entraîné + des métriques (M1, M5-B2)

## Pourquoi cette techno ?

En M1 vous traciez vos expériences dans un `experiments.md` à la main : ça
marche pour 2 runs, pas pour un modèle qui vit en prod et qu'on évalue à chaque
release. **MLflow** est l'outil pro standard pour ça : à chaque exécution
(« run »), il enregistre automatiquement les **paramètres**, les **métriques**
et éventuellement le **modèle**, et offre une **UI** pour comparer les runs
dans le temps.

C'est exactement la question de Sophie Léger : *« comment je vois si la
release de demain est meilleure ou pire que celle d'aujourd'hui ? »*. MLflow
donne l'**historique comparable**. ⚠️ **Attendu de la certification** : le
sujet d'examen demande explicitement MLflow pour le suivi des versions,
hyperparamètres et performances. Alternative `experiments.md` : ok pour
débuter, insuffisant en prod.

## Concepts clés

- **Run** : une exécution tracée. `with mlflow.start_run(run_name=...):` ouvre
  un run ; tout ce qu'on logue dedans lui est rattaché.
- **`log_params`** : les entrées (version du modèle, tag de release, jeu de
  référence). Fixes pour un run.
- **`log_metrics`** : les mesures (F1, ROC-AUC…). Peuvent être des séries.
- **Experiment** : un regroupement de runs (`set_experiment("pyrenex-eval-continue")`).
- **Tracking local** : par défaut, MLflow écrit dans `./mlruns`. `mlflow ui`
  lance l'interface de comparaison. **Pas besoin de serveur distant** pour M5.
- **Tags** : métadonnées libres (`set_tag("release_blocked", "True")`).
- **Registry** (hors-scope M5) : un cran au-dessus, gère les versions promues
  en « Staging/Production ». Optionnel ici.

## Exemple minimal qui tourne

```python
# versions : mlflow 2.17
import mlflow

mlflow.set_experiment("pyrenex-eval-continue")
with mlflow.start_run(run_name="v2.0.0"):
    mlflow.log_params({"model_version": "v2.0.0", "reference_set": "ref.csv"})
    mlflow.log_metrics({"f1_macro": 0.65, "roc_auc": 0.71})
    mlflow.set_tag("release_blocked", "False")
```

```bash
mlflow ui          # http://localhost:5000 — comparez les runs
```

## Exercice guidé

Dans `evaluate_model.py`, après avoir calculé vos 4 métriques :
1. ouvrez un run nommé d'après `--release-tag`,
2. loguez `model_version`, `release_tag`, `reference_set`, `n_reference` en
   params, et les 4 métriques,
3. lancez le script **2 fois** avec 2 tags différents, puis `mlflow ui` :
   vous devez voir **2 runs comparables** dans l'expérience.

## Pièges fréquents

| Piège | Conséquence |
|---|---|
| Loguer hors du `with start_run()` | Métriques rattachées à aucun run, ou run par défaut |
| Commiter `mlruns/` dans Git | Pollue le repo ; mettez-le en `.gitignore` (artefact CI) |
| Confondre tracking et Registry | On veut juste l'historique en M5, pas la promotion de modèles |
| Logguer un objet non-scalaire en metric | `log_metrics` attend des floats |
| Réutiliser le même `run_name` sans s'y retrouver | Difficile de comparer (utilisez le tag de release) |

| Symptôme | Cause probable |
|---|---|
| `mlflow ui` ne montre rien | Mauvais répertoire (`mlruns/` ailleurs) ou expérience non créée |
| Les runs ne sont pas comparables | Métriques nommées différemment d'un run à l'autre |
| `mlruns/` énorme dans Git | Pas dans `.gitignore` |

## Pour aller plus loin

- Doc tracking : https://mlflow.org/docs/latest/tracking.html
- Quickstart : https://mlflow.org/docs/latest/getting-started/intro-quickstart/
- (Pour plus tard) Model Registry : https://mlflow.org/docs/latest/model-registry.html

## Vérification (checklist apprenant)

- [ ] `mlflow ui` montre **≥ 2 runs comparables** de mon évaluation.
- [ ] Chaque run a params (version) + 4 métriques + tag `release_blocked`.
- [ ] `mlruns/` est dans `.gitignore`.
- [ ] Je distingue **tracking** (M5) et **Registry** (optionnel).
- [ ] Je sais expliquer pourquoi MLflow > `experiments.md` en prod.
