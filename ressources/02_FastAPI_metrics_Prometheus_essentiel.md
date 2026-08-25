# Métriques FastAPI avec Prometheus — Mini-cours

> Brief associé : M5-B1
> Durée de lecture : ~30 min
> Pré-requis : API FastAPI (M1-B2), notion d'endpoint

## Pourquoi cette techno ?

En prod, « ça marche sur ma machine » ne suffit pas : il faut **mesurer** le
service en continu. Sophie Léger veut 3 réponses : *est-il en vie ? rapide ?
prédit-il toujours bien ?* Prometheus est le standard pour ça : votre API
expose un endpoint `/metrics` au format texte, Prometheus le **scrape**
(interroge) régulièrement et stocke les séries temporelles ; Grafana les
affiche.

Plutôt que d'instrumenter chaque route à la main, la lib
`prometheus-fastapi-instrumentator` ajoute automatiquement les métriques HTTP
(latence, nombre de requêtes, codes retour). Pour les métriques **métier**
(ex. distribution des classes prédites), on utilise `prometheus-client`
directement. Alternative : pousser vers un SaaS (Datadog) — payant et overkill
pour M5.

## Concepts clés

- **`/metrics`** : un endpoint texte que Prometheus lit. Vous ne le formatez
  pas à la main, les libs le font.
- **Types de métriques** : **Counter** (ne fait qu'augmenter — ex. nombre de
  prédictions), **Histogram** (distribution — ex. latence, proba), **Gauge**
  (monte/descend — ex. modèles en mémoire).
- **Labels** : des dimensions sur une métrique. `predictions_total{predicted_class="1"}`
  permet de filtrer/grouper. ⚠️ jamais de label à cardinalité infinie
  (request_id !) — ça fait exploser Prometheus.
- **Instrumentator** : `Instrumentator().instrument(app).expose(app)` câble les
  métriques HTTP + l'endpoint `/metrics` en 1 ligne.
- **Scrape** : Prometheus interroge `/metrics` toutes les N secondes (config
  `prometheus.yml`). Les métriques sont des **cumuls** ; on calcule des taux
  avec `rate()` côté requête.

## Exemple minimal qui tourne

```python
# app/main.py — versions : fastapi 0.115, prometheus-fastapi-instrumentator 7.0
from fastapi import FastAPI
from prometheus_client import Counter
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

# Métriques HTTP automatiques + endpoint /metrics
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# Métrique métier custom
PREDICTIONS = Counter("predictions_total", "Prédictions", ["predicted_class"])

@app.post("/predict")
def predict():
    cls = 1
    PREDICTIONS.labels(predicted_class=str(cls)).inc()
    return {"prediction": cls}
```

```bash
curl localhost:8000/metrics | grep predictions_total
# predictions_total{predicted_class="1"} 1.0
```

## Exercice guidé

Sur le **service backend** (qui appelle le model), ajoutez :
1. l'instrumentator (mêmes 1 ligne) pour exposer `/metrics`,
2. un `Counter("backend_upstream_errors_total", ..., ["kind"])` incrémenté
   quand l'appel au model échoue (timeout vs erreur HTTP → 2 valeurs de label).

<details><summary>Indice</summary>
`UPSTREAM_ERRORS.labels(kind="unreachable").inc()` dans le `except httpx.RequestError`.
</details>

## Pièges fréquents

| Piège | Conséquence |
|---|---|
| Label à cardinalité infinie (request_id, timestamp) | Explosion mémoire Prometheus, dashboard inutilisable |
| Recréer un Counter à chaque requête | `Duplicated timeseries` au 2ᵉ appel |
| Lire la valeur brute du Counter comme un débit | Faux : c'est un cumul, il faut `rate()` côté Prometheus |
| Oublier `.expose(app)` | `/metrics` renvoie 404 |
| `/metrics` dans le schéma OpenAPI | Pollue la doc (`include_in_schema=False`) |

| Symptôme | Cause probable |
|---|---|
| `/metrics` → 404 | `.expose(app)` oublié ou endpoint custom mal nommé |
| `Duplicated timeseries in CollectorRegistry` | Counter défini dans une fonction au lieu du module |
| Une métrique reste à 0 | La ligne `.inc()`/`.observe()` n'est jamais atteinte |
| Prometheus ne voit pas la cible | Mauvais nom de service/port dans `prometheus.yml` |

## Pour aller plus loin

- Instrumentator : https://github.com/trallnag/prometheus-fastapi-instrumentator
- prometheus-client : https://prometheus.github.io/client_python/
- Types de métriques : https://prometheus.io/docs/concepts/metric_types/

## Vérification (checklist apprenant)

- [ ] `curl localhost:8000/metrics` renvoie du texte Prometheus.
- [ ] Je distingue Counter / Histogram / Gauge.
- [ ] Je sais pourquoi un label `request_id` est interdit.
- [ ] Mon backend expose `/metrics` (réplique du pattern model).
- [ ] J'ai ajouté une métrique métier avec au moins 1 label.
