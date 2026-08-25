# Pair-coding sur 7 h sync — Mini-cours

> Brief associé : M5-B1
> Durée de lecture : ~20 min
> Pré-requis : Git (branches, commits), `Co-authored-by:` vu en M3-B2

## Pourquoi cette techno ?

M5-B1 est le brief binôme le plus exigeant : **7 h sync** sur une stack
multi-services où les parties s'imbriquent (model ↔ backend ↔ frontend ↔
compose ↔ monitoring). Sans organisation, vous passez la journée à vous
marcher dessus (conflits Git) ou à attendre l'autre. Le pair-coding structuré
et une **répartition claire** transforment 2 personnes en équipe efficace.

Ce n'est pas qu'une question d'outils Git : c'est une **compétence
transversale** (CT2 pilotage, CT9 collectif) que le jury de certif observe.
Savoir co-construire du code partagé, c'est le quotidien d'un·e intégrateur·rice.

## Concepts clés

- **Driver / Navigator** : l'un code (driver), l'autre relit/anticipe
  (navigator). On **switche** régulièrement (toutes les 30-45 min) pour rester
  tous les deux dans le sujet.
- **Répartition par service vs par couche** : *par service* (un fait le
  backend, l'autre le frontend) = parallèle, peu de conflits, mais besoin de
  se resynchroniser sur l'interface ; *par couche* = pair-coding sur le même
  fichier. Pour M5, **par service au démarrage** puis switch l'après-midi.
- **`Co-authored-by:`** : ligne en fin de message de commit qui crédite les 2
  auteurs (2 avatars GitHub sur le commit). C'est la trace de la collaboration.
- **Branches nominatives** : `prenom/feature` plutôt que tout sur `main` —
  permet des PR, des revues, et limite les conflits.
- **Contrat d'interface** : se mettre d'accord **tôt** sur le schéma d'échange
  (ici `/score` ↔ `/predict`, même Pydantic) pour bosser en parallèle sans
  surprise.

## Exemple minimal qui tourne

```bash
# Commit à deux (driver + navigator)
git commit -m "feat(backend): route /score qui appelle le model

Co-authored-by: Prénom Nom <prenom@example.com>"
```

```bash
# Branche nominative + PR
git switch -c lea/backend-orchestrator
# ... travail ...
git push -u origin lea/backend-orchestrator   # puis Pull Request
```

## Exercice guidé

Organisez votre demi-journée AVANT de coder (5 min) :
1. Qui prend `backend`, qui prend `frontend` (répartition par service) ?
2. Quel est le **contrat d'interface** entre les deux (route, schéma, port) ?
3. À quelle heure vous **switchez** les rôles ?
Notez-le dans un `decisions.md` — ça vous servira en restitution.

## Pièges fréquents

| Piège | Conséquence |
|---|---|
| Tout committer sur `main` à deux | Conflits permanents, historique illisible |
| Pas de `Co-authored-by:` | CT9 « non observée » par le jury ; un seul crédité |
| Démarrer sans contrat d'interface | Backend et frontend incompatibles à la fusion |
| Ne jamais switcher driver/navigator | Une personne décroche, l'autre s'épuise |
| Pull tardif (fin de journée) | Gros conflit de merge en fin de brief |

| Symptôme | Cause probable |
|---|---|
| Conflits Git à répétition | Travail sur les mêmes fichiers sans branches |
| Un seul nom sur tous les commits | `Co-authored-by:` oublié |
| Backend ↔ frontend ne s'emboîtent pas | Contrat d'interface pas fixé au départ |
| Une personne « perdue » l'après-midi | Pas de switch de rôle, décrochage |

## Pour aller plus loin

- `Co-authored-by:` : https://docs.github.com/pull-requests/committing-changes-to-your-project/creating-and-editing-commits/creating-a-commit-with-multiple-authors
- Pair programming (patterns) : https://martinfowler.com/articles/on-pair-programming.html

## Vérification (checklist apprenant)

- [ ] On a réparti le travail **avant** de coder (par service).
- [ ] Nos commits portent `Co-authored-by:` (2 avatars).
- [ ] On a travaillé sur des **branches nominatives**.
- [ ] On a switché driver/navigator au moins une fois.
- [ ] Le contrat d'interface backend↔model était fixé au départ.
