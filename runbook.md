# Runbook d'astreinte — Pyrenex Prod

> Pour l'équipe SRE Pyrenex. Lisible sans connaissance du code ni de la data science.
> Dashboard Grafana : http://localhost:3001 → **Pyrenex Prod — scoring v2** (admin/admin).
> Toutes les commandes se lancent à la racine du dépôt.

**Baseline mesurée le 2026-08-25** sur `/score` et `/predict` (30 requêtes) :
p50 = 52 ms · **p95 = 98 ms** · p99 = 380 ms.
Les seuils ci-dessous en découlent — ce ne sont pas des chiffres arbitraires.

---

## 1. Service KO (un conteneur down)

**Déclenchement** : panel **Vie** — `up` d'un service passe à **0** (affiché `DOWN`)
pendant plus de 1 min. Ou `docker compose ps` montre un service `exited` /
`unhealthy`.

> ⚠️ Ne vous fiez pas au panel d'erreurs : un service mort n'expose plus rien,
> ses compteurs se figent au lieu de monter. Seul `up` voit la panne.

**Actions** :
1. `docker compose ps` — identifier le service et son état.
2. `docker compose logs --tail=100 <service>` — lire l'erreur avant d'agir.
3. `docker compose restart <service>`.
4. Attendre 30 s, re-vérifier `docker compose ps` : le service doit repasser `healthy`.
5. Toujours KO après 2 redémarrages → escalade.

**Qui appeler** : astreinte FastIA (niveau 1). Si le service `model` reste KO
plus de 15 min → Sophie Léger, Lead Data Pyrenex.

**On NE fait PAS** :
- `docker compose down -v` — détruit les volumes, y compris l'historique Prometheus.
- Redémarrer les 5 services « pour être sûr » : on perd la trace de l'incident.

---

## 2. Latence p95 dégradée

**Déclenchement** : panel **Vitesse** — p95 > **300 ms** pendant plus de 5 min
sur `model` ou `backend`.

> 300 ms ≈ **3 × la baseline mesurée (98 ms)**. En dessous de ce facteur on
> déclencherait sur du bruit normal ; le p99 monte déjà à 380 ms au repos.

**Actions** :
1. Panel **Vie** : les deux services sont-ils `UP` ? Si non → procédure 1.
2. `docker stats --no-stream` — un conteneur sature-t-il son CPU ou sa RAM ?
3. Comparer p95 `model` et p95 `backend` :
   - les deux montent ensemble → le goulot est le **model**,
   - seul le backend monte → problème réseau ou timeout côté orchestrateur.
4. Vérifier si une release a été déployée dans l'heure (`git log --oneline -5`).
   Si oui et que la dégradation suit le déploiement → procédure 4 (rollback).
5. Pas de release récente et charge normale → escalade.

**Qui appeler** : astreinte FastIA. Si la dégradation dépasse 30 min ou touche
les heures ouvrées Pyrenex → Sophie Léger.

**On NE fait PAS** :
- Déployer un correctif non testé pour « voir si ça passe ».
- Augmenter les timeouts pour faire disparaître le symptôme : ça masque la cause
  et transforme une erreur rapide en attente longue côté client.

---

## 3. Métrique modèle qui s'écarte

**Déclenchement** : panel **Comportement** — la part de la classe 1 (défaut)
sort de la fourchette **26 % – 46 %** sur 1 h glissante.

> Référence : sur le holdout M1, le modèle prédit « défaut » pour **36 %** des
> dossiers (2160 / 6000). La fourchette est ±10 points autour de cette valeur.

**Actions** :
1. Vérifier d'abord que ce n'est pas un artefact de volume : moins de ~20
   prédictions sur l'heure rend le pourcentage instable. Si le trafic est faible,
   observer sans agir.
2. Panel **Vie** + **Vitesse** : si un service a redémarré, les compteurs sont
   repartis de zéro — attendre 1 h de trafic propre avant de conclure.
3. `git log --oneline -5` : une release a-t-elle changé le modèle ou le
   préprocessing ? Comparer `model_version` sur http://localhost:8000/info.
4. Si le modèle est inchangé et l'écart persiste > 2 h : c'est probablement la
   **population de demandes** qui a changé, pas le modèle. Escalade data.

**Qui appeler** : Sophie Léger (Lead Data Pyrenex) — c'est une décision métier,
pas une panne technique.

**On NE fait PAS** :
- Réentraîner ou remplacer le modèle en urgence pendant l'astreinte.
- Conclure à une dégradation de performance : ce panel montre ce que le modèle
  **prédit**, pas s'il prédit **juste**. Sans les vraies réponses, on ne mesure
  pas la performance — c'est le rôle de l'évaluation continue (M5-B2).

---

## 4. Rollback de release

**Déclenchement** : après un déploiement, l'un des cas suivants dans l'heure :
- taux de réponses 5xx > 5 % sur 5 min,
- p95 > 300 ms de façon durable (procédure 2 sans autre cause identifiée),
- un service ne redevient pas `healthy` après 2 redémarrages (procédure 1).

**Actions** :
1. Identifier la dernière version stable : `git tag --sort=-creatordate | head -5`.
2. `git checkout <tag-stable>` (ex. `v1.0.0-prod`).
3. `docker compose up --build -d` — reconstruit la stack sur la version stable.
4. `docker compose ps` : les 3 services doivent être `healthy`.
5. Vérifier sur le dashboard que p95 et taux d'erreur reviennent à la baseline.
6. Prévenir l'équipe : la version cassée reste sur `main`, **personne ne
   redéploie tant que la cause n'est pas comprise**.

**Qui appeler** : astreinte FastIA pour exécuter. Prévenir Sophie Léger **après**
le retour à la normale, pas pendant.

**On NE fait PAS** :
- Corriger en avant (« un petit fix et ça repart ») : on revient au stable
  d'abord, on comprend ensuite.
- `git push --force` sur `main` pour effacer la release fautive : on perd la
  trace nécessaire au post-mortem.
- Rollback sans noter l'heure et le tag concernés — le post-mortem en dépend.

---

## Contacts

| Rôle | Qui | Quand |
|---|---|---|
| Astreinte niveau 1 | FastIA | tout incident technique |
| Lead Data Pyrenex | Sophie Léger | comportement du modèle, décision métier |
| Responsable projet | Karim (FastIA) | incident > 1 h ou impact client |

> À compléter avec les numéros et canaux réels avant la mise en production.