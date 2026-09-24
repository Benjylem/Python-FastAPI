# Tester l'API à la main avec curl

Ce guide liste une requête `curl` par cas à vérifier, avec le résultat attendu.
Il couvre tout ce qui est implémenté pour l'instant : `rooms`, `players` et
`sessions` (lobby, équipe, partie complète, timer).

> ⚠️ Toutes les données sont en mémoire : chaque redémarrage du serveur remet
> l'API à zéro. Les commandes sont écrites **dans l'ordre**, pour un serveur tout
> juste démarré (les ids `1`, `2`… des sessions en dépendent).

> 🔑 Ce document contient les réponses des 4 énigmes.

## 1. Lancer le serveur

Depuis le dossier `R00t_Override/` :

```bash
conda activate r00t_override
uvicorn app.main:app --reload
```

L'API écoute sur `http://127.0.0.1:8000`. La doc interactive Swagger est aussi
disponible sur <http://127.0.0.1:8000/docs> (bouton **Try it out** sur chaque route).

Dans un **second terminal**, définis l'URL de base (en majuscules, et à refaire
dans chaque nouveau terminal) :

```bash
BASE_URL=http://127.0.0.1:8000
```

Pour voir le code HTTP en plus du corps de la réponse, ajoute
`-w "\nHTTP %{http_code}\n"` à n'importe quelle commande (ou `-i` pour voir tous
les en-têtes).

## 2. Déroulé d'une partie

```
POST /sessions/start          -> équipe créée, statut "lobby"
POST /sessions/1/players      -> des joueurs rejoignent l'équipe
POST /sessions/1/launch       -> statut "in_progress", le chrono de 60 min démarre
GET  /sessions/1/rooms/N/enigma   -> énoncé de la salle active
POST /sessions/1/rooms/N/submit   -> bonne réponse = reward + salle suivante
...salle 4 réussie            -> statut "victory"
...ou chrono à 0              -> statut "game_over"
```

## 3. Health check

```bash
curl $BASE_URL/
```

Attendu : `200`, `{"status": "ok", "message": "..."}`

## 4. Rooms (carte publique)

Ces routes donnent seulement le nom et la bio des salles. L'énoncé d'une énigme
se lit via une session (voir section 6).

```bash
# Liste des salles -> 200, [1, 2, 3, 4]
curl $BASE_URL/rooms/

# Détail -> 200, {"id": 1, "name": "Pare-Feu", "bio": "..."}
curl $BASE_URL/rooms/1

# Salle inconnue -> 404, {"detail": "Salle introuvable"}
curl $BASE_URL/rooms/99
```

## 5. Players

Joueurs présents au démarrage : `1` (Joe) et `2` (Jasmine).
Corps attendu : `{"name": "<3 caractères minimum>"}`. Un joueur est renvoyé
sous la forme `{"id": 1, "name": "Joe", "session_id": null}` (`session_id` =
son équipe).

```bash
# Lister -> 200
curl $BASE_URL/players/

# Lire un joueur -> 200
curl $BASE_URL/players/1

# Joueur inconnu -> 404
curl $BASE_URL/players/999

# Créer -> 200, Alice avec l'id 3
curl -X POST $BASE_URL/players/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice"}'

# Nom trop court -> 422
curl -X POST $BASE_URL/players/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Al"}'

# Renommer -> 200, Joe devient Joseph
curl -X PUT $BASE_URL/players/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "Joseph"}'

# Renommer un joueur inconnu -> 404
curl -X PUT $BASE_URL/players/999 \
  -H "Content-Type: application/json" \
  -d '{"name": "Ghost"}'

# Supprimer -> 204 (pas de corps)
curl -i -X DELETE $BASE_URL/players/2

# Supprimer un joueur inconnu -> 404
curl -X DELETE $BASE_URL/players/999
```

## 6. Sessions

### Créer une équipe (lobby)

```bash
# Créer -> 200, id 1, "status": "lobby", "started_at": null,
# "temps_restant": null, "players": [], inventaire vide (tout à false)
curl -X POST $BASE_URL/sessions/start \
  -H "Content-Type: application/json" \
  -d '{"team_name": "Root Squad"}'

# Nom d'équipe vide -> 422
curl -X POST $BASE_URL/sessions/start \
  -H "Content-Type: application/json" \
  -d '{"team_name": "   "}'

# Lire l'état -> 200
curl $BASE_URL/sessions/1/state

# Session inconnue -> 404
curl $BASE_URL/sessions/999/state
```

Tant que la partie est en lobby, on ne peut pas jouer :

```bash
# Énoncé en lobby -> 409, "La partie n'a pas encore été lancée"
curl $BASE_URL/sessions/1/rooms/1/enigma

# Réponse en lobby -> 409
curl -X POST $BASE_URL/sessions/1/rooms/1/submit \
  -H "Content-Type: application/json" \
  -d '{"answer": "root_override"}'

# Lancer sans joueur -> 409, "Impossible de lancer une partie sans joueur"
curl -X POST $BASE_URL/sessions/1/launch
```

### Composer l'équipe

```bash
# Le joueur 1 rejoint l'équipe -> 200, il apparaît dans "players"
curl -X POST $BASE_URL/sessions/1/players \
  -H "Content-Type: application/json" \
  -d '{"player_id": 1}'

# Rejoindre deux fois -> 409
curl -X POST $BASE_URL/sessions/1/players \
  -H "Content-Type: application/json" \
  -d '{"player_id": 1}'

# Joueur inconnu -> 404
curl -X POST $BASE_URL/sessions/1/players \
  -H "Content-Type: application/json" \
  -d '{"player_id": 999}'
```

### Lancer la partie et le timer

```bash
# Lancer -> 200, "status": "in_progress", "started_at" rempli,
# "temps_restant": 3600 (secondes)
curl -X POST $BASE_URL/sessions/1/launch

# Lancer une 2e fois -> 409
curl -X POST $BASE_URL/sessions/1/launch

# Le temps restant diminue à chaque appel
curl $BASE_URL/sessions/1/state
```

Le chrono dure **60 minutes**. Quand `temps_restant` atteint `0`, la session
passe en `"status": "game_over"` et toute réponse renvoie
`409 "Temps écoulé : la partie est perdue"`. Ce cas n'est pas faisable à la main
(il faudrait attendre une heure) : il est couvert par les tests pytest.

### Jouer les 4 salles

On ne peut répondre qu'à la **salle active** (`current_room`) :

- une salle suivante renvoie `403 "Salle verrouillée"` ;
- une salle déjà résolue renvoie `409` ;
- une partie terminée (victoire ou game over) renvoie `409`.

Chaque réponse renvoie `success`, `message`, `reward`, `current_room`,
`game_status` et `temps_restant`.

```bash
# Énoncé de la salle 1 -> 200, "resolue": false
curl $BASE_URL/sessions/1/rooms/1/enigma

# Énoncé de la salle 2 -> 403, pas encore débloquée
curl $BASE_URL/sessions/1/rooms/2/enigma

# Répondre à la salle 2 trop tôt -> 403
curl -X POST $BASE_URL/sessions/1/rooms/2/submit \
  -H "Content-Type: application/json" \
  -d '{"answer": "ADMIN_TOKEN_X987F"}'

# Réponse vide -> 422
curl -X POST $BASE_URL/sessions/1/rooms/1/submit \
  -H "Content-Type: application/json" \
  -d '{"answer": "   "}'

# Mauvaise réponse -> 200, "success": false, "current_room": 1
curl -X POST $BASE_URL/sessions/1/rooms/1/submit \
  -H "Content-Type: application/json" \
  -d '{"answer": "faux"}'
```

**Salle 1 — Pare-Feu** (clé base64 à décoder, casse ignorée)

```bash
# -> 200, "success": true, "reward": "cle_validation_externe", "current_room": 2
curl -X POST $BASE_URL/sessions/1/rooms/1/submit \
  -H "Content-Type: application/json" \
  -d '{"answer": "root_override"}'

# Rejouer la salle 1 -> 409, "Salle déjà résolue"
curl -X POST $BASE_URL/sessions/1/rooms/1/submit \
  -H "Content-Type: application/json" \
  -d '{"answer": "root_override"}'
```

**Salle 2 — Proxy & Logs** (le token admin accepté dans les logs, casse exacte)

```bash
# -> 200, "reward": "privileges_intermediaires", "current_room": 3
curl -X POST $BASE_URL/sessions/1/rooms/2/submit \
  -H "Content-Type: application/json" \
  -d '{"answer": "ADMIN_TOKEN_X987F"}'
```

**Salle 3 — Contre-Mesures** (corps différent : `{"conditions": {...}}`, avec les
mêmes clés et les mêmes types que l'état donné dans l'énoncé)

```bash
# Format "answer" -> 422
curl -X POST $BASE_URL/sessions/1/rooms/3/submit \
  -H "Content-Type: application/json" \
  -d '{"answer": "x"}'

# Conditions vides -> 422
curl -X POST $BASE_URL/sessions/1/rooms/3/submit \
  -H "Content-Type: application/json" \
  -d '{"conditions": {}}'

# Mauvaises conditions -> 200, "success": false
curl -X POST $BASE_URL/sessions/1/rooms/3/submit \
  -H "Content-Type: application/json" \
  -d '{"conditions": {"bypass_firewall": true, "override_lock": "LOCKED", "port_status": 443}}'

# Bonnes conditions -> 200, "reward": "module_dechiffrement", "current_room": 4
curl -X POST $BASE_URL/sessions/1/rooms/3/submit \
  -H "Content-Type: application/json" \
  -d '{"conditions": {"bypass_firewall": true, "override_lock": "ACTIVE", "port_status": 80}}'
```

**Salle 4 — Noyau Central** (commande de reboot, espaces ignorés)

```bash
# -> 200, "success": true, "game_status": "victory"
curl -X POST $BASE_URL/sessions/1/rooms/4/submit \
  -H "Content-Type: application/json" \
  -d '{"answer": "system.reboot(true)"}'

# Répondre après la victoire -> 409, "La partie est terminée"
curl -X POST $BASE_URL/sessions/1/rooms/4/submit \
  -H "Content-Type: application/json" \
  -d '{"answer": "system.reboot(true)"}'

# État final -> "status": "victory", inventaire entièrement à true,
# "temps_restant" figé au moment de la victoire
curl $BASE_URL/sessions/1/state
```

### Changer d'équipe

Un joueur ne peut être que dans une équipe à la fois.

```bash
# Créer une 2e équipe -> 200, id 2
curl -X POST $BASE_URL/sessions/start \
  -H "Content-Type: application/json" \
  -d '{"team_name": "Blue Team"}'

# Le joueur 1 est encore dans l'équipe 1 -> 409
curl -X POST $BASE_URL/sessions/2/players \
  -H "Content-Type: application/json" \
  -d '{"player_id": 1}'

# Il quitte l'équipe 1 -> 200 (autorisé même après la fin de la partie)
curl -X DELETE $BASE_URL/sessions/1/players/1

# Puis rejoint l'équipe 2 -> 200
curl -X POST $BASE_URL/sessions/2/players \
  -H "Content-Type: application/json" \
  -d '{"player_id": 1}'

# Retirer un joueur qui n'est pas dans l'équipe -> 404
curl -X DELETE $BASE_URL/sessions/1/players/1
```

## 7. Tout lancer d'un coup

Le script [`tests/curl_requests.sh`](../tests/curl_requests.sh) enchaîne toutes
ces requêtes dans le même ordre, compare chaque code HTTP à celui attendu et
affiche le bilan (`✅` / `❌`). À lancer sur un serveur **tout juste démarré** :

```bash
./tests/curl_requests.sh
# ou sur une autre adresse :
BASE_URL=http://127.0.0.1:8001 ./tests/curl_requests.sh
```

## 8. Tests automatiques

Les mêmes cas, plus le game over du timer, sont couverts par pytest :

```bash
python -m pytest -q
```
