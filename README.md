# M5-B1 + M5-B2 — Pyrenex Prod (architecture, CI/CD, monitoring, éval continue)

> **Repo template GitHub.** Un·e des 2 du binôme clique **« Use this
> template »** → `M5-B1-pyrenex-prod-<binome>`, puis ajoute l'autre comme
> collaborateur. Vous partez du **scoring v2** (modèle M1 fourni) et vous le
> mettez en **production complète** : 3 services orchestrés, CI/CD, monitoring
> Grafana, runbook, puis (B2) évaluation continue + tracking MLflow.

---

## 🧭 Votre brief en un coup d'œil

**Ce README est votre document de pilotage unique** — tout ce qu'il faut faire,
dans l'ordre, avec le bon appui. Les autres supports ont chacun un rôle précis :

| Support | Rôle |
|---|---|
| **Simplonline** | Le contrat : contexte client, livrables, critères de performance |
| **Ce README** | Le pilotage : quoi faire, quand, avec quel mini-cours |
| [`ressources/`](./ressources/) | Les 8 mini-cours d'appui (index dans [`ressources/README.md`](./ressources/README.md)) |
| **Discord `fil-M5`** | Annonces + questions |

### M5-B1 — les 2 jours sync (binôme)

| Quand | Tâche | Durée | Appui |
|---|---|---|---|
| Mardi 9h15 | 1. Appropriation de la reprise M1 (modèle + API fournis) | 30 min | — |
| Mardi 10h00 | 2. Architecture 3 services (`model` / `backend` / `frontend`) | 1h30 | [`01_Docker_compose`](./ressources/01_Docker_compose_multiservices_essentiel.md) |
| Mardi 12h15 | 3. Vérification `docker compose up` | 15 min | [`01_Docker_compose`](./ressources/01_Docker_compose_multiservices_essentiel.md) |
| Mardi 12h30 | 4. 🍽️ Déjeuner | 1h | — |
| Mardi 13h30 | 5. Pipeline CI/CD GitHub Actions + *quality gate* | 2h30 | [`03_GitHub_Actions`](./ressources/03_GitHub_Actions_CI_CD_essentiel.md) — appui [`06_Pair_coding`](./ressources/06_Pair_coding_sync_long_essentiel.md) |
| Mardi 16h45 | 6. Mur réflexif intermédiaire | 15 min | — |
| Mercredi 9h15 | 7. Endpoint `/metrics` + métriques métier | 30 min | [`02_FastAPI_metrics_Prometheus`](./ressources/02_FastAPI_metrics_Prometheus_essentiel.md) |
| Mercredi 9h45 | 8. Prometheus + Grafana dans le compose | 30 min | [`02_FastAPI_metrics_Prometheus`](./ressources/02_FastAPI_metrics_Prometheus_essentiel.md) |
| Mercredi 10h25 | 9. Dashboard Grafana custom (vie / vitesse / comportement) | 40 min | [`04_Grafana_dashboard`](./ressources/04_Grafana_dashboard_custom_essentiel.md) |
| Mercredi 11h00 | 10. Runbook d'astreinte (4 procédures) | 30 min | [`05_Runbook_astreinte`](./ressources/05_Runbook_astreinte_essentiel.md) |
| Mercredi 11h30 | 11. **Tour de table binômes** (démo compose + dashboard) | 1h | — |
| Mercredi 12h30 | 12. Mur réflexif final M5-B1 | 30 min | — |

### M5-B2 — l'async individuel (jeudi + vendredi matin, 6 h)

Vous repartez **chacun·e** du repo binôme, dans une branche perso
`<prenom>/m5-b2-eval-continue`. Pas de nouveau repo.

| Étape | Durée | Appui |
|---|---|---|
| 1. Constituer le jeu de référence (`data/reference_set.csv`, ~500 lignes) | 1h | [`08_Evaluation_continue_seuils`](./ressources/08_Evaluation_continue_seuils_essentiel.md) |
| 2. Écrire `scripts/evaluate_model.py` (code retour 0 / non-zéro) | 2h | [`08_Evaluation_continue_seuils`](./ressources/08_Evaluation_continue_seuils_essentiel.md) |
| 3. Tracer chaque run dans **MLflow** (local, `mlruns/`) | 1h | [`07_MLflow_tracking`](./ressources/07_MLflow_tracking_essentiel.md) |
| 4. Documenter les seuils (`evaluation_thresholds.md`) | 1h | [`08_Evaluation_continue_seuils`](./ressources/08_Evaluation_continue_seuils_essentiel.md) |
| 5. Étape `evaluate-model` bloquante dans la CI + tests | 1h | [`03_GitHub_Actions`](./ressources/03_GitHub_Actions_CI_CD_essentiel.md) |

### ✅ Checklist livrables

**M5-B1 — avant mercredi 12h30**

- [ ] `docker compose up --build` démarre les **3 services** de façon **reproductible**, healthchecks verts
- [ ] `/metrics` exposé côté `model` **et** `backend`
- [ ] Dashboard Grafana provisionné **automatiquement** (3 panels : vie / vitesse / comportement)
- [ ] Workflow CI **vert**, image poussée sur GHCR, tag `v1.0.0-prod`
- [ ] Le **contract test** du modèle bloque la release s'il est rouge
      *(il vérifie le **contrat technique** de l'API — pas la performance du
      modèle : ça, c'est l'évaluation continue de B2)*
- [ ] `runbook.md` — 4 procédures (Service KO / Latence / Métrique modèle / Rollback)
- [ ] `README.md` — schéma Mermaid de l'archi + démarrage en 3 commandes
- [ ] Commits binôme : `Co-authored-by:` ou auteurs nominatifs

**M5-B2 — avant vendredi 17h**

- [ ] `scripts/evaluate_model.py` idempotent, sortie JSON parsable
- [ ] `data/reference_set.csv` versionné
- [ ] ≥ 2 runs MLflow comparables + **une preuve** (artefact CI `mlruns` ou
      capture de `mlflow ui`) — ⚠️ `mlruns/` est gitignoré, **ne le commitez pas**
- [ ] `evaluation_thresholds.md` — 4 métriques × baseline / seuil / justification
- [ ] Étape CI `evaluate-model` **rouge sur dégradation volontaire** (testé une fois)
- [ ] `tests/test_evaluation.py` — 3 tests minimum, `pytest -v` vert
- [ ] Branche mergée en `main`, tag `v1.1.0-eval-continue`

**Les deux briefs**

- [ ] **Journal de bord** — 1 entrée par séance (trame `cas_usage_certif/journal-de-bord.ipynb`
      du repo [`ia-dev-id-ressources`](https://github.com/Formation-SIMPLON-IA/ia-dev-id-ressources))

→ Compétences visées : **C6 — transposer** (palier final) + **C9 — imiter**.

---

## 🚀 Démarrage (le service `model` tourne déjà)

```bash
# 1. Environnement de tests local (optionnel mais conseillé)
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt

# 2. Vérifier que la base fournie passe les tests
pytest -v services/model/tests

# 3. Lancer ce qui est déjà câblé (model + prometheus + grafana)
docker compose up --build
```

> 🧰 **Avec `uv`** : `uv venv && source .venv/bin/activate` puis
> **`uv pip install -r requirements-dev.txt`**.
> ⚠️ Un venv créé par `uv venv` **n'embarque pas `pip`** : si vous voyez
> `No module named pip`, c'est ça — utilisez `uv pip install`, pas `pip install`.

> ⚠️ **Ports hôte** : frontend **8088** (pas 8080), Grafana **3001** (pas 3000)
> — pour éviter les conflits courants. Model 8000, backend 8001, Prometheus 9090.

Au départ, seuls `model`, `prometheus` et `grafana` démarrent : à vous
d'ajouter `backend` + `frontend` et de compléter le reste (cf. TODO).

---

## 📁 Structure

```
services/
  model/        # FOURNI — API scoring M1-B2 + /metrics (ne pas réécrire)
  backend/      # À COMPLÉTER — orchestrateur
  frontend/     # À COMPLÉTER — formulaire nginx
prometheus/     # FOURNI — scrape config
grafana/provisioning/
  datasources/  # FOURNI — datasource Prometheus
  dashboards/   # provider fourni ; le dashboard JSON = à vous (tâche 9)
.github/workflows/ci.yml   # squelette (job test fourni)
runbook.md                 # template 4 sections
scripts/evaluate_model_TEMPLATE.py   # B2 — MLflow pré-câblé
data/reference_set_TEMPLATE.csv      # B2 — exemple à remplacer
evaluation_thresholds_TEMPLATE.md    # B2 — seuils à justifier
ressources/                # 📚 mini-cours d'appui (lecture juste-à-temps)
```

> Le service `model` (déjà fourni) est votre **exemple de référence** : il
> expose déjà `/metrics` — répliquez ce pattern sur le `backend`.

---

## 📚 Ressources

Voir [`./ressources/`](./ressources/) — 8 mini-cours + `liens_officiels.md`.
Lecture **juste-à-temps** : ouvrez le mini-cours de la tâche en cours.

---

## 🆘 Bloqué·e·s ?

1. Relisez le mini-cours de la tâche en cours (`ressources/`).
2. Le service `model` est votre exemple qui marche : copiez ses patterns.
3. 30 min sur un bloquant → Discord `fil-M5`.
