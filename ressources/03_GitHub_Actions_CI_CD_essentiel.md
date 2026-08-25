# GitHub Actions — CI/CD — Mini-cours

> Brief associé : M5-B1 (+ M5-B2 pour l'étape bloquante)
> Durée de lecture : ~30 min
> Pré-requis : Git/GitHub, pytest, Docker build

## Pourquoi cette techno ?

Livrer en prod « à la main » (je build, je teste si j'y pense, je push) est
une source d'incidents. La **CI/CD** automatise : à chaque push, GitHub
exécute vos tests, construit les images, et ne publie une **release** que si
tout est vert. Sophie Léger l'exige : *« une release ne sort que si tous les
tests passent et si le contract test du modèle est vert »*.

GitHub Actions est intégré au repo (pas de serveur à gérer). Un fichier YAML
dans `.github/workflows/` décrit des **jobs** (tests, build, push) avec leurs
dépendances. Alternatives : GitLab CI, Jenkins (serveur dédié). Pour M5,
Actions est le choix naturel — gratuit sur repo public, registry GHCR inclus.

## Concepts clés

- **Workflow** : un fichier `.yml` déclenché par des `on:` (push, tag, PR).
- **Job** : un ensemble d'étapes sur une machine fraîche (`runs-on:
  ubuntu-latest`). Les jobs sont **parallèles** par défaut.
- **`needs:`** : crée une dépendance — `build` `needs: [test]` ne démarre que
  si `test` réussit. C'est le **garde-fou** : pas de build si les tests cassent.
- **`steps`** : `uses:` (action réutilisable, ex. `actions/checkout`) ou `run:`
  (commande shell).
- **Secrets** : `${{ secrets.GITHUB_TOKEN }}` (fourni) pour pousser sur GHCR ;
  jamais de secret en clair dans le YAML.
- **GHCR** : `ghcr.io/<org>/<image>` — le registry d'images de GitHub.

## Exemple minimal qui tourne

```yaml
# .github/workflows/ci.yml
name: CI
on:
  push: { branches: [main], tags: ["v*"] }
  pull_request: { branches: [main] }

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install -r services/model/requirements.txt pytest httpx
      - run: pytest -v services/model/tests   # inclut le contract test

  build:
    needs: test           # ← bloque si les tests échouent
    if: github.event_name == 'push'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker compose build
```

## Exercice guidé

Ajoutez le **push GHCR** au job `build` :
1. Login : `docker/login-action@v3` avec `registry: ghcr.io`,
   `username: ${{ github.actor }}`, `password: ${{ secrets.GITHUB_TOKEN }}`.
2. `permissions: { packages: write }` sur le job.
3. Tag + push de l'image model vers `ghcr.io/<votre-repo-en-minuscules>-model`.

⚠️ Deux pièges vous attendent ici, et ils ne se voient qu'au moment du push :

- **GHCR n'accepte que des noms d'image en minuscules.** Votre repo s'appelle
  `Formation-SIMPLON-IA/M5-B1-pyrenex-prod-<binôme>` : tel quel, `docker tag`
  refuse avec *« repository name must be lowercase »*. Il faut abaisser la casse.
- **`docker compose images -q model` renvoie une chaîne vide** après un simple
  `docker compose build` : cette commande ne liste que les images des conteneurs
  **créés**, pas celles qui viennent d'être construites. Le `docker tag` casse
  alors sur un argument vide.

<details><summary>Indice</summary>

```bash
IMG="ghcr.io/$(echo "${{ github.repository }}" | tr '[:upper:]' '[:lower:]')-model"
TAG="${GITHUB_REF_NAME//\//-}"          # une branche `feature/ci` n'est pas un tag valide
docker build -t "$IMG:$TAG" ./services/model
docker push "$IMG:$TAG"
```
</details>

## Pièges fréquents

| Piège | Conséquence |
|---|---|
| `build` sans `needs: test` | Une image cassée part en prod (les tests servent à rien) |
| Secret en clair dans le YAML | Fuite de credentials dans l'historique Git |
| Oublier `permissions: packages: write` | `denied: permission_denied` au push GHCR |
| Chemin de tests faux (`pytest tests` au mauvais endroit) | Le job passe en testant... rien |
| Workflow pas dans `.github/workflows/` | GitHub ne le détecte pas |
| Nom d'image GHCR avec des majuscules | `docker tag` refuse : *repository name must be lowercase* |
| `docker compose images -q` après un simple `build` | Renvoie du vide → `docker tag` casse sur un argument manquant |

| Symptôme | Cause probable |
|---|---|
| Le workflow ne se lance pas | Fichier hors `.github/workflows/`, ou `on:` ne matche pas l'event |
| `denied` au push d'image | `permissions: packages: write` manquant ou login raté |
| `build` tourne malgré des tests rouges | `needs:` oublié |
| `pytest` « passe » mais ne teste rien | Mauvais répertoire de tests, 0 test collecté |
| `invalid reference format` au `docker tag` | Majuscules dans le nom d'image, ou variable vide |

## Pour aller plus loin

- Doc : https://docs.github.com/actions
- Publier sur GHCR : https://docs.github.com/packages/working-with-a-github-packages-registry/working-with-the-container-registry
- `needs` & dépendances : https://docs.github.com/actions/using-jobs/using-jobs-in-a-workflow

## Vérification (checklist apprenant)

- [ ] Mon workflow est **vert** sur la dernière push.
- [ ] `build` a `needs: test` (et `evaluate-model` en B2).
- [ ] Aucun secret n'est écrit en clair.
- [ ] Une image taguée est poussée sur GHCR.
- [ ] Je sais expliquer pourquoi le contract test bloque la release.
