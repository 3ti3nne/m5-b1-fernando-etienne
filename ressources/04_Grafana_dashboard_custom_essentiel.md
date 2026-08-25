# Grafana — dashboard custom & provisioning — Mini-cours

> Brief associé : M5-B1
> Durée de lecture : ~30 min
> Pré-requis : Prometheus expose des métriques (mini-cours 02)

## Pourquoi cette techno ?

Prometheus stocke des métriques mais ne les **montre** pas joliment. Grafana
est l'outil de visualisation : il interroge Prometheus (PromQL) et affiche des
**panels** (courbes, jauges). On vous demande un dashboard qui réponde aux 3
questions de Sophie Léger : **vie** (RPS, erreurs), **vitesse** (latence
p50/p95/p99), **comportement** (distribution des prédictions — ce que le
modèle prédit *actuellement*, pas s'il prédit *bien* : sans les vraies
réponses on ne mesure pas la performance, c'est le rôle de M5-B2).

Point pro central : ne **pas** importer un dashboard tout fait (le fameux
`1860`) — vous **construisez le vôtre**, adapté à VOS métriques métier. Et vous
le **provisionnez** : le dashboard est versionné en JSON dans le repo et chargé
automatiquement au démarrage (pas de clic manuel à reproduire).

## Concepts clés

- **Datasource** : la source de données (ici Prometheus). Provisionnée via
  `provisioning/datasources/*.yml` avec un `uid` fixe pour la référencer.
- **Panel** : un graphique. Type `timeseries` pour des courbes.
- **PromQL** : le langage de requête. `rate(metric[1m])` = débit ;
  `histogram_quantile(0.95, sum(rate(..._bucket[1m])) by (le))` = p95.
- **Provisioning** : `provisioning/dashboards/*.yml` (le *provider* qui dit
  « charge les JSON de ce dossier ») + le **JSON du dashboard** lui-même.
- **`uid`** : identifiant stable du dashboard / de la datasource — pour que les
  panels référencent la datasource de façon reproductible.
- **`up`** : la métrique que **Prometheus fabrique lui-même** pour chaque cible
  scrapée — `1` si le scrape a réussi, `0` sinon. C'est la seule qui répond
  vraiment à *« est-il en vie ? »*, parce qu'elle ne vient **pas** du service.
  Quand un conteneur meurt, il n'expose plus rien : ses compteurs ne montent
  pas, ils **se figent**. Un dashboard qui ne surveille que le taux d'erreur ne
  voit donc **pas** la panne. Ajoutez toujours un panneau `up{job=~"..."}`.

## La panne muette — à faire une fois pour le croire

Coupez le service model (`docker compose stop model`) et envoyez 3 requêtes :
elles renvoient bien des 503, et pourtant le panneau « erreurs 5xx » affiche
**0**. Deux raisons cumulées :

1. une série de compteur qui **apparaît pour la première fois** ne produit pas
   de `rate()` — il faut au moins deux points de mesure ;
2. le service mort ne publie plus rien du tout.

Seul `up{job="model"}` bascule à 0. C'est la démonstration que **« pas
d'erreurs affichées » ≠ « tout va bien »**.

## Exemple minimal qui tourne

```yaml
# provisioning/datasources/datasource.yml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    uid: prometheus          # ← référencé par les panels
    url: http://prometheus:9090
    isDefault: true
```

```json
// provisioning/dashboards/pyrenex_prod.json (extrait — 1 panel latence p95)
{
  "uid": "pyrenex-prod", "title": "Pyrenex Prod", "schemaVersion": 39,
  "panels": [{
    "type": "timeseries", "title": "Vitesse — p95",
    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
    "datasource": {"type": "prometheus", "uid": "prometheus"},
    "targets": [{
      "datasource": {"type": "prometheus", "uid": "prometheus"},
      "expr": "histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{job=\"model\"}[1m])) by (le))",
      "legendFormat": "p95"
    }]
  }]
}
```

```yaml
# provisioning/dashboards/dashboards.yml (le provider)
apiVersion: 1
providers:
  - name: Pyrenex
    type: file
    options: { path: /etc/grafana/provisioning/dashboards }
```

## Exercice guidé

Ajoutez le panel **Qualité** (distribution des classes prédites) :
1. Requête : `sum(rate(pyrenex_predictions_total[5m])) by (predicted_class)`.
2. `legendFormat: "classe {{predicted_class}}"`.
3. Relancez `docker compose up`, ouvrez `localhost:3001` (admin/admin), le
   dashboard doit apparaître **sans import manuel**.

## Pièges fréquents

| Piège | Conséquence |
|---|---|
| Importer le dashboard 1860 au lieu du vôtre | Hors-sujet : il ne montre pas vos métriques métier |
| Construire le dashboard à la main dans l'UI sans l'exporter | Perdu au prochain `compose down` — non reproductible |
| `uid` de datasource non fixé | Les panels pointent dans le vide après provisioning |
| Lire un Counter sans `rate()` | Courbe qui monte indéfiniment, illisible |
| Mauvais nom de métrique dans `expr` | Panel « No data » |
| Dashboard « Vie » sans panneau `up` | La panne d'un service ne se voit **pas** : ses compteurs se figent au lieu de monter |
| `sum(rate(...))` sans `or vector(0)` | « No data » quand il n'y a aucune erreur — indistinguable d'un panneau cassé |

| Symptôme | Cause probable |
|---|---|
| Dashboard absent après `up` | JSON mal placé / provider mal configuré |
| Panel « No data » | Métrique pas encore générée (envoyez du trafic) ou nom faux |
| « Datasource not found » | `uid` du panel ≠ `uid` de la datasource provisionnée |
| Latence plate à 0 | `_bucket` ou `by (le)` manquant dans `histogram_quantile` |
| Un service est tombé mais rien ne bouge sur le dashboard | Pas de panneau `up` : on mesure le trafic, pas la vie |

## Pour aller plus loin

- Provisioning : https://grafana.com/docs/grafana/latest/administration/provisioning/
- PromQL : https://prometheus.io/docs/prometheus/latest/querying/basics/
- `histogram_quantile` : https://prometheus.io/docs/practices/histograms/

## Vérification (checklist apprenant)

- [ ] Mon dashboard apparaît **automatiquement** (provisionné, pas importé).
- [ ] J'ai 3 panels : vie, vitesse, comportement.
- [ ] La latence utilise `histogram_quantile(..._bucket, by le)`.
- [ ] Le JSON du dashboard est **versionné** dans le repo.
- [ ] Je sais pourquoi on évite le dashboard 1860 ici.
