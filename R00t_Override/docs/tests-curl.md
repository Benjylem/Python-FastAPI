# Tester l'API à la main avec curl

Ce guide liste une requête `curl` par cas à vérifier, avec le résultat attendu.
Il couvre tout ce qui est implémenté pour l'instant : `rooms`, `players` et `sessions`
(équipe, lobby, lancement, les 4 salles, inventaire partagé, victoire).

> Toutes les données sont en mémoire : chaque redémarrage du serveur remet l'API
> à zéro. Les exemples des sections 4 à 8 supposent un serveur **fraîchement
> démarré** (première session = id `1`, joueurs de départ `1` Joe et `2` Jasmine).

## 1. Lancer le serveur

Depuis le dossier `R00t_Override/` :

```bash
conda activate r00t_override
uvicorn app.main:app --reload
```

L'API écoute sur `http://127.0.0.1:8000`. La doc interactive Swagger est aussi
disponible sur <http://127.0.0.1:8000/docs>.

> Avec `--reload`, chaque sauvegarde d'un fichier redémarre le serveur et efface
> les sessions. Pour tester sans toucher au code, lance-le sans `--reload`.

Dans un second terminal, définis l'URL de base et l'en-tête JSON :

```bash
BASE_URL=http://127.0.0.1:8000
JSON="Content-Type: application/json"
```

Pour voir le code HTTP en plus du corps de la réponse, ajoute
`-w "\nHTTP %{http_code}\n"` à n'importe quelle commande (ou utilise `-i` pour
voir tous les en-têtes).

> **zsh** : par défaut, zsh refuse les lignes `# commentaire` collées dans le
> terminal (`command not found: #`). Lance une fois `setopt interactivecomments`
> pour pouvoir copier les blocs ci-dessous tels quels.

## 2. Tout lancer d'un coup

Le script [`tests/curl_requests.sh`](../tests/curl_requests.sh) joue tout le
parcours (sections 4 à 8), vérifie le code HTTP attendu de chaque requête
(✔ vert / ✘ rouge) et affiche un bilan :

```bash
./tests/curl_requests.sh
```

Sur une autre adresse :

```bash
BASE_URL=http://127.0.0.1:8001 ./tests/curl_requests.sh
```

Le script crée ses propres joueurs et équipes et supprime ses joueurs à la fin :
il peut être relancé sans redémarrer le serveur. Code de sortie `0` si tout est OK.

## 3. Tests automatiques

Les mêmes cas (et plus) sont couverts par pytest, **sans serveur à lancer** :

```bash
python -m pytest -q     # résumé
python -m pytest -v     # nom de chaque test
```

## 4. Health check

```bash
curl $BASE_URL/
```

Attendu : `200`, `{"status": "ok", "message": "..."}`

## 5. Rooms : la carte publique

`/rooms` ne donne que le nom et la bio de chaque salle. L'énoncé de l'énigme
n'est lisible que via la session de l'équipe, une fois la salle débloquée
(voir section 8).

```bash
# Lister les salles -> 200, [1, 2, 3, 4]
curl $BASE_URL/rooms/

# Détail d'une salle -> 200, id, name, bio (pas d'énoncé, pas de réponse)
curl $BASE_URL/rooms/1

# Salle inconnue -> 404, {"detail": "Salle introuvable"}
curl $BASE_URL/rooms/99
```

## 6. Players

Joueurs présents au démarrage : `1` (Joe) et `2` (Jasmine), sans équipe.
Format du corps : `{"name": "<3 caractères minimum>"}`. Un joueur n'a pas de
rewards : ils sont dans l'inventaire partagé de son équipe.

Les exemples créent Alice (id `3`) pour la modifier et la supprimer, afin de
garder Joe et Jasmine pour la suite.

```bash
# Lister -> 200, Joe et Jasmine avec "session_id": null
curl $BASE_URL/players/

# Lire un joueur -> 200, Joe
curl $BASE_URL/players/1

# Joueur inconnu -> 404
curl $BASE_URL/players/999

# Créer -> 200, {"id": 3, "name": "Alice", "session_id": null}
curl -X POST $BASE_URL/players/ -H "$JSON" -d '{"name": "Alice"}'

# Nom trop court -> 422
curl -X POST $BASE_URL/players/ -H "$JSON" -d '{"name": "Al"}'

# Modifier -> 200, Alice devient Alicia
curl -X PUT $BASE_URL/players/3 -H "$JSON" -d '{"name": "Alicia"}'

# Modifier un joueur inconnu -> 404
curl -X PUT $BASE_URL/players/999 -H "$JSON" -d '{"name": "Ghost"}'

# Supprimer -> 204 (pas de corps), puis GET /players/3 renvoie 404
curl -i -X DELETE $BASE_URL/players/3

# Supprimer un joueur inconnu -> 404
curl -X DELETE $BASE_URL/players/999
```

Supprimer un joueur le retire aussi de son équipe.

## 7. Sessions : l'équipe

Une session = une équipe et sa partie. Cycle de vie :
`lobby` (l'équipe se constitue) → `in_progress` (après `launch`, le chrono
démarre) → `victory` (salle 4 validée).

### Créer l'équipe (lobby)

```bash
# Créer -> 200, "status": "lobby", "started_at": null, "players": [],
# inventaire à false
curl -X POST $BASE_URL/sessions/start -H "$JSON" -d '{"team_name": "Hackers"}'

# Nom d'équipe vide -> 422
curl -X POST $BASE_URL/sessions/start -H "$JSON" -d '{"team_name": "   "}'

# Lire l'état -> 200
curl $BASE_URL/sessions/1/state

# Session inconnue -> 404
curl $BASE_URL/sessions/999/state
```

### Composer l'équipe

```bash
# Lancer sans joueur -> 409
curl -X POST $BASE_URL/sessions/1/launch

# Joe rejoint -> 200, Joe dans "players"
curl -X POST $BASE_URL/sessions/1/players -H "$JSON" -d '{"player_id": 1}'

# Joe rejoint une deuxième fois -> 409
curl -X POST $BASE_URL/sessions/1/players -H "$JSON" -d '{"player_id": 1}'

# Joueur inconnu -> 404
curl -X POST $BASE_URL/sessions/1/players -H "$JSON" -d '{"player_id": 999}'
```

### Lancer la partie

```bash
# Énoncé ou réponse avant le lancement -> 409
curl $BASE_URL/sessions/1/rooms/1/enigma

# Lancer -> 200, "status": "in_progress", "started_at" renseigné
curl -X POST $BASE_URL/sessions/1/launch

# Lancer une deuxième fois -> 409
curl -X POST $BASE_URL/sessions/1/launch
```

### Changer d'équipe

Un joueur n'est que dans une équipe à la fois : pour changer, il quitte la
première puis rejoint la seconde. Quitter est possible dans tous les états.

```bash
# Créer une deuxième équipe (id 2) et y mettre Jasmine
curl -X POST $BASE_URL/sessions/start -H "$JSON" -d '{"team_name": "Rivaux"}'
curl -X POST $BASE_URL/sessions/2/players -H "$JSON" -d '{"player_id": 2}'

# Jasmine rejoint Hackers sans quitter Rivaux -> 409
curl -X POST $BASE_URL/sessions/1/players -H "$JSON" -d '{"player_id": 2}'

# Jasmine quitte Rivaux -> 200, puis rejoint Hackers -> 200
curl -X DELETE $BASE_URL/sessions/2/players/2
curl -X POST $BASE_URL/sessions/1/players -H "$JSON" -d '{"player_id": 2}'

# Quitter une équipe dont on ne fait pas partie -> 404
curl -X DELETE $BASE_URL/sessions/2/players/2
```

Rejoindre une partie **en cours** est autorisé (retardataire) : le joueur voit
immédiatement la progression et l'inventaire de l'équipe. Rejoindre une partie
terminée renvoie `409`.

## 8. Jouer une partie

On ne peut lire et répondre qu'à la salle active (`current_room`) :

| Cas | Code |
|---|---|
| Partie pas encore lancée | `409` |
| Salle pas encore débloquée | `403` « Salle verrouillée » |
| Salle déjà résolue | `409` « Salle déjà résolue » |
| Partie terminée | `409` |

Chaque bonne réponse ajoute le reward de la salle à l'inventaire de l'équipe et
ouvre la salle suivante. La réponse contient `success`, `message`, `reward`,
`current_room` et `game_status`.

### Salle 1 : Pare-Feu (clé encodée en Base64)

L'énoncé contient `cm9vdF9vdmVycmlkZQ==` : il faut la décoder et renvoyer la
clé en clair. La casse est ignorée.

```bash
# Énoncé -> 200, "resolue": false
curl $BASE_URL/sessions/1/rooms/1/enigma

# Salle 2 pas encore débloquée -> 403 (énoncé comme réponse)
curl $BASE_URL/sessions/1/rooms/2/enigma
curl -X POST $BASE_URL/sessions/1/rooms/2/submit -H "$JSON" -d '{"answer": "ADMIN_TOKEN_X987F"}'

# Réponse vide -> 422
curl -X POST $BASE_URL/sessions/1/rooms/1/submit -H "$JSON" -d '{"answer": "   "}'

# Renvoyer la chaîne encore encodée -> 200, "success": false
curl -X POST $BASE_URL/sessions/1/rooms/1/submit -H "$JSON" -d '{"answer": "cm9vdF9vdmVycmlkZQ=="}'

# Bonne réponse -> 200, "success": true, "reward": "cle_validation_externe", "current_room": 2
curl -X POST $BASE_URL/sessions/1/rooms/1/submit -H "$JSON" -d '{"answer": "root_override"}'

# Rejouer la salle 1 -> 409 "Salle déjà résolue"
curl -X POST $BASE_URL/sessions/1/rooms/1/submit -H "$JSON" -d '{"answer": "root_override"}'
```

### Salle 2 : Proxy & Logs (token dans un extrait de log)

L'énoncé contient un extrait de log avec des leurres. Le bon token est celui
dont l'élévation a été acceptée (`status=GRANTED`). La casse compte.

```bash
# Énoncé (affichage lisible des logs, sans jq)
curl -s $BASE_URL/sessions/1/rooms/2/enigma | python3 -c "import json,sys; print(json.load(sys.stdin)['enigme'])"

# Token leurre en minuscules (status=DENIED) -> 200, "success": false
curl -X POST $BASE_URL/sessions/1/rooms/2/submit -H "$JSON" -d '{"answer": "admin_token_x987f"}'

# Bon token -> 200, "success": true, "reward": "privileges_intermediaires"
curl -X POST $BASE_URL/sessions/1/rooms/2/submit -H "$JSON" -d '{"answer": "ADMIN_TOKEN_X987F"}'
```

### Salle 3 : Contre-Mesures (payload JSON typé)

Format du corps : `{"conditions": {...}}`. Il faut renvoyer l'état corrigé avec
exactement les mêmes clés **et les mêmes types** (`true` n'est pas `1`, `80`
n'est pas `"80"`).

```bash
# Énoncé -> 200
curl $BASE_URL/sessions/1/rooms/3/enigma

# Format "answer" des autres salles -> 422
curl -X POST $BASE_URL/sessions/1/rooms/3/submit -H "$JSON" -d '{"answer": "x"}'

# Conditions vides -> 422
curl -X POST $BASE_URL/sessions/1/rooms/3/submit -H "$JSON" -d '{"conditions": {}}'

# 1 au lieu de true -> 200, "success": false
curl -X POST $BASE_URL/sessions/1/rooms/3/submit -H "$JSON" \
  -d '{"conditions": {"bypass_firewall": 1, "override_lock": "ACTIVE", "port_status": 80}}'

# Bonnes conditions -> 200, "success": true, "reward": "module_dechiffrement"
curl -X POST $BASE_URL/sessions/1/rooms/3/submit -H "$JSON" \
  -d '{"conditions": {"bypass_firewall": true, "override_lock": "ACTIVE", "port_status": 80}}'
```

### Salle 4 : Noyau Central (patch final)

La commande attendue est `system.reboot(true)`. La casse et les espaces sont
ignorés.

```bash
# Énoncé -> 200
curl $BASE_URL/sessions/1/rooms/4/enigma

# Mauvais patch -> 200, "success": false
curl -X POST $BASE_URL/sessions/1/rooms/4/submit -H "$JSON" -d '{"answer": "system.reboot(false)"}'

# Patch final -> 200, "success": true, "game_status": "victory"
curl -X POST $BASE_URL/sessions/1/rooms/4/submit -H "$JSON" -d '{"answer": "  System.Reboot( TRUE ) "}'

# Soumettre après la victoire -> 409
curl -X POST $BASE_URL/sessions/1/rooms/4/submit -H "$JSON" -d '{"answer": "system.reboot(true)"}'
```

### Fin de partie

```bash
# État final -> "status": "victory", inventaire entièrement à true
curl $BASE_URL/sessions/1/state

# Tous les énoncés sont marqués "resolue": true
curl $BASE_URL/sessions/1/rooms/1/enigma
```
