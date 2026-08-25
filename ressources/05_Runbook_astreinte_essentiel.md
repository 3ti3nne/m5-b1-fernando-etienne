# Runbook d'astreinte — Mini-cours

> Brief associé : M5-B1
> Durée de lecture : ~20 min
> Pré-requis : la stack tourne, monitoring Grafana en place

## Pourquoi cette techno ?

Un service en prod **tombera** un jour, à 3h du matin, et ce n'est pas vous
qui serez de garde mais un·e SRE qui ne connaît pas votre code. Le **runbook**
est le document qui lui permet d'agir vite et **sans aggraver** : pour chaque
incident type, quoi regarder, quoi faire, qui appeler, et surtout **ce qu'il
ne faut PAS faire**.

Ce n'est pas de la doc technique exhaustive : c'est une **procédure
opérationnelle** courte, orientée action. Un bon runbook se lit en 30 secondes
sous stress. Alternative « pas de runbook » = chaque incident est une enquête
qui dépend de la personne disponible. Sophie Léger en demande 4.

## Concepts clés

- **Déclenchement** : le signal observable qui dit « il se passe quelque
  chose » — un panel Grafana qui passe au rouge, un `docker ps` anormal. Doit
  être **chiffré** (« p95 > 300 ms sur 5 min »), pas vague.
- **Actions** : la séquence à exécuter, dans l'ordre, du moins au plus
  intrusif (regarder les logs avant de redémarrer, redémarrer avant de rebuild).
- **Escalade (« qui appeler »)** : à partir de quand on réveille qui. Évite que
  la personne d'astreinte reste seule trop longtemps.
- **« Ce qu'on NE fait PAS »** : les gestes qui aggravent (ex. `down -v` qui
  détruit les volumes, hotfix non testé en prod). **C'est la section la plus
  utile** — elle évite la catastrophe.
- **Réversibilité** : préférer le **rollback** (revenir à la version stable
  précédente) à la rustine en urgence.

## Exemple minimal qui tourne

```markdown
## Service KO (un conteneur down)

**Déclenchement** : `docker compose ps` montre un service `exited`,
ou panel « Vie » : RPS à 0.

**Actions** :
1. `docker compose logs --tail=100 <service>` — lire l'erreur.
2. `docker compose restart <service>`.
3. Si KO après 2 essais : escalade.

**Qui appeler** : astreinte FastIA.

**On NE fait PAS** : `docker compose down -v` (détruit les volumes).
```

## Exercice guidé

Rédigez la procédure **« Latence p95 dégradée »** :
1. Déclenchement **chiffré** (référez-vous à votre baseline de latence model).
2. 2-3 actions (vérifier la charge, `docker stats`, regarder un déploiement
   récent).
3. Qui appeler + 1 chose à NE PAS faire (ex. redéployer une version non testée).

## Pièges fréquents

| Piège | Conséquence |
|---|---|
| Déclenchement vague (« si c'est lent ») | La personne d'astreinte ne sait pas quand agir |
| Pas de section « ce qu'on NE fait PAS » | Geste destructeur fait en panique |
| Runbook trop long / encyclopédique | Illisible sous stress, donc inutilisé |
| Seuils non reliés à la baseline | « 300 ms » sorti du chapeau, non défendable |
| Pas de procédure de rollback | On bricole en prod au lieu de revenir au stable |

| Symptôme | Cause probable |
|---|---|
| L'astreinte n'ose pas agir | Déclenchement pas assez explicite/chiffré |
| Un incident s'aggrave après intervention | Action destructrice non interdite explicitement |
| Chaque incident prend 1h | Pas de procédure → enquête à chaque fois |

## Pour aller plus loin

- Google SRE — Runbooks/Playbooks : https://sre.google/sre-book/being-on-call/
- Postmortems sans blâme : https://sre.google/sre-book/postmortem-culture/

## Vérification (checklist apprenant)

- [ ] J'ai 4 procédures (Service KO / Latence / Métrique modèle / Rollback).
- [ ] Chaque déclenchement est **chiffré** ou observable précisément.
- [ ] Chaque procédure a une section « ce qu'on NE fait PAS ».
- [ ] Un·e SRE non-data pourrait l'exécuter sans moi.
- [ ] Mes seuils sont reliés à la baseline / aux panels Grafana.
