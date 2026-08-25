# Seuils d'évaluation continue — Pyrenex scoring v2 (À COMPLÉTER)

> Doit être lisible par Sophie Léger (Lead Data) et le DPO. **Chaque seuil
> est justifié** par une raison chiffrée. Renommez en `evaluation_thresholds.md`.

Stratégie retenue (absolu / relatif / **hybride**) : _à choisir et justifier_.
Jeu de référence : `data/reference_set.csv` (sous-échantillon figé du holdout M1).

## Deux baselines, à ne pas confondre

| | Mesurée sur | Sert à |
|---|---|---|
| **Baseline communiquée** (`metrics_holdout`) | le holdout M1 complet | ce qu'on a annoncé au client |
| **Golden run** (`data/reference_baseline.json`) | **votre** jeu de référence, au gel | **arbitrer les releases** |

⚠️ Le garde-fou compare au **golden run**, jamais à la baseline communiquée :
les deux jeux n'ont ni la même taille ni la même composition, donc l'écart
entre eux mesure une **différence de population**, pas une dégradation du
modèle.

| Métrique | Golden run | Plancher absolu | Baisse max vs golden run | Justification |
|---|---|---|---|---|
| F1 macro | _…_ | _…_ | _…_ | _… (pourquoi ce seuil ?)_ |
| ROC-AUC | _…_ | _…_ | _…_ | _…_ |
| Recall défaut | _…_ | _…_ | _…_ | _…_ |

> **Comment dimensionner la colonne « baisse max »** : mesurez le bruit de
> votre jeu de référence (bootstrap, cf. mini-cours 08), et prenez **au moins
> 2 σ**. Une tolérance sous le bruit se déclenche toute seule. Reportez ici le
> σ mesuré — c'est ce qui rend le seuil défendable devant Sophie Léger.

| Métrique | σ bootstrap mesuré | 2 σ | Tolérance retenue |
|---|---|---|---|
| F1 macro | _…_ | _…_ | _…_ |
| ROC-AUC | _…_ | _…_ | _…_ |
| Recall défaut | _…_ | _…_ | _…_ |

## Procédure de mise à jour des seuils

- **Qui** : _…_
- **Quand** : _…_
- **Comment** : _… (garder `THRESHOLDS` dans le script ET ce fichier cohérents ;
  si le jeu de référence change, **regeler le golden run** — `--freeze-baseline`)_