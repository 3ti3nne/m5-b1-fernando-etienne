"""Métriques métier Prometheus — service model (fourni — votre exemple de référence).

En plus des métriques HTTP standard exposées par
``prometheus-fastapi-instrumentator`` (latence, RPS, codes retour), on
expose 2 métriques **métier** qui répondent à la 3ᵉ question de Sophie
Léger : *« le modèle prédit-il toujours bien ? »*

- ``pyrenex_predictions_total`` : compteur des prédictions, labellé par
  classe prédite (0 = remboursé, 1 = défaut). La dérive de la répartition
  0/1 dans le temps est un signal d'alerte (data drift / concept drift).
- ``pyrenex_prediction_proba`` : histogramme des probabilités de défaut
  renvoyées. Un modèle sain produit une distribution étalée ; un pic à
  0.5 ou aux bornes signale un problème.
"""
from __future__ import annotations

from prometheus_client import Counter, Histogram

PREDICTIONS_TOTAL = Counter(
    "pyrenex_predictions_total",
    "Nombre de prédictions servies, par classe prédite.",
    labelnames=("predicted_class",),
)

PREDICTION_PROBA = Histogram(
    "pyrenex_prediction_proba",
    "Distribution des probabilités de défaut prédites.",
    buckets=(0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
)


def observe_prediction(predicted_class: int, proba_default: float) -> None:
    """Enregistre une prédiction dans les métriques métier.

    Args:
        predicted_class: Classe prédite (0 = remboursé, 1 = défaut).
        proba_default: Probabilité de défaut renvoyée par le modèle.
    """
    PREDICTIONS_TOTAL.labels(predicted_class=str(predicted_class)).inc()
    PREDICTION_PROBA.observe(proba_default)
