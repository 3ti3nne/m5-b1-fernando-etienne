# Docker Compose multi-services — Mini-cours

> Brief associé : M5-B1
> Durée de lecture : ~30 min
> Pré-requis : Docker de base (build, run, ports) vu en M0/M1

## Pourquoi cette techno ?

En M1, vous serviez **un** conteneur (l'API). En production, une solution IA
est rarement un seul process : il y a souvent un **frontend**, un **backend**
qui orchestre, le **service modèle**, et de l'outillage (monitoring). Les
lancer/arrêter/relier à la main devient ingérable.

`docker compose` décrit **toute la stack dans un seul fichier YAML** et la
démarre en une commande (`docker compose up`). Chaque service a son image, ses
ports, ses variables d'env, et les services se parlent par leur **nom** sur un
réseau interne. Alternatives : Kubernetes (trop lourd pour du local / une démo
— c'est M7+), ou des scripts shell (fragiles). Pour M5, compose est le bon
niveau : reproductible, lisible, sans surcouche.

## Concepts clés

- **Service** : un bloc sous `services:`. `build: ./services/model` construit
  l'image depuis un Dockerfile ; `image: prom/prometheus` la tire d'un registry.
- **Résolution par nom** : `backend` peut appeler `http://model:8000` — compose
  crée un DNS interne. **N'utilisez jamais `localhost` entre services** (chaque
  conteneur a son propre `localhost`).
- **Ports `"8088:80"`** : `hôte:conteneur`. Le port hôte doit être libre (d'où
  8088 au lieu de 8080, souvent pris).
- **`depends_on` + `condition: service_healthy`** : démarrer `backend`
  seulement quand `model` répond à son healthcheck (pas juste « démarré »).
- **`healthcheck`** : une commande que Docker répète ; le service passe
  `healthy` quand elle réussit. C'est ce qui rend `depends_on` fiable.
- **`volumes` `./conf:/etc/...:ro`** : monter un fichier de config en lecture
  seule (Prometheus, provisioning Grafana).

## Exemple minimal qui tourne

```yaml
# docker-compose.yml — versions : Docker 24+, Compose v2
services:
  model:
    build: ./services/model
    ports: ["8000:8000"]
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/health').status==200 else 1)"]
      interval: 10s
      timeout: 3s
      start_period: 20s
      retries: 3

  backend:
    build: ./services/backend
    ports: ["8001:8001"]
    environment:
      MODEL_URL: "http://model:8000"   # ← nom de service, pas localhost
    depends_on:
      model:
        condition: service_healthy
```

```bash
docker compose up --build       # build + démarre
docker compose ps               # statut + santé
docker compose logs -f backend  # logs en direct
docker compose down             # arrêt + nettoyage réseau
```

## Exercice guidé

Ajoutez le service `frontend` (nginx) à l'exemple ci-dessus :
1. `build: ./services/frontend`, port hôte **8088** → conteneur **80**.
2. `depends_on: backend` avec `condition: service_healthy`.
3. **Son propre healthcheck** — le critère du brief est « les **3** services
   `healthy` ». Un service sans healthcheck reste éternellement sans état.
4. Relancez `docker compose up --build` et vérifiez `docker compose ps` :
   `frontend` doit démarrer **après** que `backend` soit `healthy`, puis passer
   `healthy` à son tour.

<details><summary>Solution attendue</summary>

```yaml
  frontend:
    build: ./services/frontend
    ports: ["8088:80"]
    healthcheck:
      # 127.0.0.1 et NON `localhost` : `listen 80;` ne bind que l'IPv4, or
      # `localhost` résout ::1 en premier dans l'image nginx → refused.
      test: ["CMD", "wget", "-q", "--spider", "http://127.0.0.1/"]
      interval: 10s
      timeout: 3s
      start_period: 5s
      retries: 3
    depends_on:
      backend:
        condition: service_healthy
```
</details>

## Pièges fréquents

| Piège | Conséquence |
|---|---|
| Utiliser `localhost` entre services | Connexion refusée — chaque conteneur a son propre localhost |
| Port hôte déjà pris (8080, 3000) | `Bind for 0.0.0.0:8080 failed: port is already allocated` |
| `depends_on` sans `condition: service_healthy` | Le backend démarre avant que le model soit prêt → erreurs au boot |
| Oublier `--build` après modif du code | L'ancienne image tourne, vos changements sont invisibles |
| Healthcheck sans `start_period` | Le service est marqué `unhealthy` pendant son démarrage normal |
| Monter un volume sans `:ro` pour une config | Risque de modification accidentelle du fichier source |

| Symptôme | Cause probable |
|---|---|
| `Connection refused` vers un autre service | `localhost` au lieu du nom de service |
| `port is already allocated` | Un autre process (ou une autre stack) occupe le port hôte |
| Le service reste `health: starting` puis `unhealthy` | Commande de healthcheck fausse, ou app pas encore prête (start_period trop court) |
| `frontend` `unhealthy` alors que la page s'ouvre dans le navigateur | La sonde interroge `localhost` (→ ::1) alors que nginx n'écoute qu'en IPv4 : utiliser `127.0.0.1` |
| Un service n'affiche aucun état de santé | Il n'a pas de `healthcheck` — « pas de healthcheck » ≠ « healthy » |
| Changements de code ignorés | Image pas reconstruite (`--build` oublié) |

## Pour aller plus loin

- Doc officielle : https://docs.docker.com/compose/
- Healthchecks : https://docs.docker.com/reference/dockerfile/#healthcheck
- `depends_on` conditions : https://docs.docker.com/compose/how-tos/startup-order/

## Vérification (checklist apprenant)

- [ ] `docker compose up --build` démarre tous mes services.
- [ ] `docker compose ps` montre les services `healthy`.
- [ ] Mes services se parlent par leur **nom** (pas `localhost`).
- [ ] Je sais expliquer `depends_on: condition: service_healthy` à un collègue.
- [ ] J'ai fait l'exercice (ajout du frontend après le backend).
