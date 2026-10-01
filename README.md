# Root Override : 60 minutes pour sauver le réseau

## Pitch de lancement (Introduction par Eve)

« Salut l'équipe. Si vous m'entendez, c'est que le compte à rebours a déjà commencé. Une intelligence artificielle expérimentale vient de s'emparer des serveurs centraux. Son objectif ? Couper les câbles sous-marins, neutraliser les DNS et effacer le WWW de la surface de la terre. Dans moins d'une heure, il n'y aura plus d'Internet, plus de données, le néant numérique total. Je ne peux pas y aller seule, ses contremesures me grillent instantanément. C'est là que vous intervenez. Je vous ai ouvert une brèche clandestine sur le réseau. Vous avez 60 minutes pour traverser les couches de sécurité, pirater le système de l'intérieur, et m'aider à réécrire son code source avant qu'il ne soit trop tard. Ne me décevez pas... Le réseau compte sur vous. »

## Le déroulement en bref

Root Override est un escape game **100 % back-end** : pas d'interface, tout se joue via l'API (Swagger, curl, Postman...).

1. **Le lobby** : l'équipe se constitue (`POST /sessions/start`), les joueurs rejoignent la session. Rien ne bouge tant que personne ne lance la partie.
2. **Le lancement** : `POST /sessions/{id}/launch` démarre le chrono de **60 minutes**.
3. **Les 4 salles**, à franchir dans l'ordre. Chaque réussite débloque la suivante, ajoute une récompense à l'inventaire de l'équipe et déclenche un message d'Eve :

| # | Salle | Défi |
|---|---|---|
| 1 | Pare-Feu | Décoder une clé interceptée en Base64 |
| 2 | Proxy & Logs | Retrouver le token admin réellement accepté, noyé dans des logs piégés |
| 3 | Contre-Mesures | Renvoyer l'état JSON corrigé (mêmes clés, mêmes types) |
| 4 | Noyau Central | Écrire la commande de reboot final |

4. **Les indices d'Eve** : 3 indices par salle, du plus vague au plus précis. Chaque indice coûte **2 minutes** de chrono.
5. **La fin de partie** : patch validé dans la salle 4 = **victoire**. Chrono à zéro = **game over**.

Le détail complet (diagrammes d'états et de séquence, modèle du domaine, choix de conception) est dans [R00t_Override/docs/architecture.md](R00t_Override/docs/architecture.md).

## Partie technique

### Arborescence

```text
R00t_Override/
├── app/
│   ├── main.py              # Point d'entrée FastAPI : routers, gestion des erreurs, /health
│   ├── core/                # Configuration transverse (logging)
│   ├── routers/             # Routes HTTP : rooms, players, sessions
│   ├── schemas/             # Modèles Pydantic : validation des entrées, forme des sorties
│   ├── services/            # Logique applicative + exceptions métier (404, 403, 409)
│   ├── domain/              # Modèles métier : Session, Salle, Enigme, Door, Player, Inventaire
│   └── data/                # Données en mémoire : les 4 salles, les indices, sessions, joueurs
├── tests/                   # Suite pytest (+ curl_requests.sh : une partie complète contre un vrai serveur)
├── docs/                    # architecture.md, tests-curl.md
└── environment.yml          # Environnement conda
```

Le flux d'une requête suit cette arborescence de haut en bas : `routers` → `services` → `domain` → `data`.

### Installation et lancement

Depuis le dossier `R00t_Override/` :

```bash
conda env create -f environment.yml
conda activate r00t_override
fastapi dev app/main.py
```

L'API écoute sur `http://127.0.0.1:8000`.

### Aperçu rapide de l'API

| Route | Rôle |
|---|---|
| `GET /health` | Vérifier que le moteur de jeu est en ligne (titre, version) |
| `GET /docs` | Documentation interactive Swagger : toutes les routes, testables depuis le navigateur |

Un premier coup d'œil en une commande :

```bash
curl http://127.0.0.1:8000/health
```

### Démo en curl : les premiers pas d'une équipe

Sur un serveur **fraîchement démarré** (les données sont en mémoire et repartent de zéro à chaque redémarrage), dans un second terminal :

```bash
BASE_URL=http://127.0.0.1:8000
JSON="Content-Type: application/json"

# 1. Créer l'équipe (session 1, en lobby)
curl -X POST $BASE_URL/sessions/start -H "$JSON" -d '{"team_name": "Hackers"}'

# 2. Joe (joueur 1, présent au démarrage) rejoint l'équipe
curl -X POST $BASE_URL/sessions/1/players -H "$JSON" -d '{"player_id": 1}'

# 3. Lancer la partie : le chrono de 60 minutes démarre
curl -X POST $BASE_URL/sessions/1/launch

# 4. Lire l'énoncé de la salle 1
curl $BASE_URL/sessions/1/rooms/1/enigma

# 5. Répondre : la salle 2 se débloque et Eve réagit
curl -X POST $BASE_URL/sessions/1/rooms/1/submit -H "$JSON" -d '{"answer": "root_override"}'

# 6. Voir l'état de la partie (salle, temps restant, inventaire)
curl $BASE_URL/sessions/1/state
```

Tous les cas (erreurs 403, 404, 409, 422, indices, victoire) sont détaillés dans [R00t_Override/docs/tests-curl.md](R00t_Override/docs/tests-curl.md).

### Lancer les tests

Depuis le dossier `R00t_Override/`, **avec l'environnement conda activé** (`conda activate r00t_override`), sinon `pytest` ne trouvera pas les dépendances du projet :

```bash
pytest -v tests/
```

Résultat attendu : tous les tests passent, sans serveur à lancer.

```text
============================= 116 passed ==============================
```

La suite couvre les salles, les joueurs, les énigmes, les services (sans HTTP), les logs des routers et le déroulé complet d'une session (lobby, équipe, progression, victoire, chrono, game over, indices). Le chrono est testé en reculant l'heure de départ, sans attendre 60 minutes.

Pour rejouer une partie complète contre un serveur lancé, lancez `./tests/curl_requests.sh` (détails dans [R00t_Override/docs/tests-curl.md](R00t_Override/docs/tests-curl.md)).

## Équipe

Projet réalisé par Amaury Aune et Benjamin Lemoine.

| Amaury | Benjamin |
|--------|-----------|
| Classes et storytelling | Routes, logique métier et logs |

Pour le reste c'est un travail commun : Enigmes, réponses GM, tests.
