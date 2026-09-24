# Tester l'API à la main avec curl

Ce guide liste une requête `curl` par cas à vérifier, avec le résultat attendu.
Il couvre tout ce qui est implémenté pour l'instant : `rooms`, `players` et `sessions`.

> Toutes les données sont en mémoire : chaque redémarrage du serveur remet l'API
> à zéro. Relance le serveur avant de repasser les tests.

## 1. Lancer le serveur

Depuis le dossier `R00t_Override/` :

```bash
conda activate r00t_override
uvicorn app.main:app --reload
```

L'API écoute sur `http://127.0.0.1:8000`. La doc interactive Swagger est aussi
disponible sur <http://127.0.0.1:8000/docs>.

Dans un second terminal, définis l'URL de base :

```bash
BASE_URL=http://127.0.0.1:8000
```

Pour voir le code HTTP en plus du corps de la réponse, ajoute
`-w "\nHTTP %{http_code}\n"` à n'importe quelle commande (ou utilise `-i` pour
voir tous les en-têtes).

## 2. Health check

```bash
curl $BASE_URL/
```

Attendu : `200`, `{"status": "ok", "message": "..."}`

## 3. Rooms

### Lister les salles

```bash
curl $BASE_URL/rooms/
```

Attendu : `200`, `[1, 2, 3, 4]`

### Détail d'une salle

```bash
curl $BASE_URL/rooms/1
```

Attendu : `200`, `id`, `name`, `bio` et `enigme` (l'énoncé). La réponse
attendue n'apparaît jamais.

### Salle inconnue

```bash
curl $BASE_URL/rooms/99
```

Attendu : `404`, `{"detail": "Salle introuvable"}`

### Salles 1, 2 et 4 : réponse texte

Format du corps : `{"answer": "<texte>"}`

```bash
# Bonne réponse salle 1 -> 200, "success": true
curl -X POST $BASE_URL/rooms/1/submit \
  -H "Content-Type: application/json" \
  -d '{"answer": "cle_externe_valide"}'

# Mauvaise réponse -> 200, "success": false
curl -X POST $BASE_URL/rooms/1/submit \
  -H "Content-Type: application/json" \
  -d '{"answer": "mauvaise_reponse"}'

# Réponse vide -> 422 (refusée par la validation)
curl -X POST $BASE_URL/rooms/1/submit \
  -H "Content-Type: application/json" \
  -d '{"answer": "   "}'

# Salle inconnue -> 404
curl -X POST $BASE_URL/rooms/99/submit \
  -H "Content-Type: application/json" \
  -d '{"answer": "x"}'

# Bonne réponse salle 2 -> 200, "success": true
curl -X POST $BASE_URL/rooms/2/submit \
  -H "Content-Type: application/json" \
  -d '{"answer": "admin_token_1337"}'
```

### Salle 3 : conditions booléennes

Format du corps : `{"conditions": {"<nom>": true|false, ...}}`

```bash
# Bonnes conditions -> 200, "success": true
curl -X POST $BASE_URL/rooms/3/submit \
  -H "Content-Type: application/json" \
  -d '{"conditions": {"firewall_neutralise": true, "boucle_stoppee": true}}'

# Conditions incomplètes -> 200, "success": false
curl -X POST $BASE_URL/rooms/3/submit \
  -H "Content-Type: application/json" \
  -d '{"conditions": {"firewall_neutralise": true, "boucle_stoppee": false}}'

# Conditions vides -> 422
curl -X POST $BASE_URL/rooms/3/submit \
  -H "Content-Type: application/json" \
  -d '{"conditions": {}}'

# Format "answer" des autres salles -> 422
curl -X POST $BASE_URL/rooms/3/submit \
  -H "Content-Type: application/json" \
  -d '{"answer": "x"}'
```

### Salle 4 et victoire

```bash
# État avant -> {"status": "in_progress"}
curl $BASE_URL/rooms/status/game

# Patch final -> 200, "success": true, "game_status": "victory"
curl -X POST $BASE_URL/rooms/4/submit \
  -H "Content-Type: application/json" \
  -d '{"answer": "reboot --force --patch=core"}'

# État après -> {"status": "victory"}
curl $BASE_URL/rooms/status/game
```

## 4. Players

Joueurs présents au démarrage : `1` (Joe) et `2` (Jasmine).
Format du corps : `name` (3 caractères minimum), `reward1`, `reward2`, `reward3` (booléens).

```bash
# Lister -> 200, Joe et Jasmine
curl $BASE_URL/players/

# Lire un joueur -> 200, Joe
curl $BASE_URL/players/1

# Joueur inconnu -> 404
curl $BASE_URL/players/999

# Créer -> 200, le joueur avec un nouvel id
curl -X POST $BASE_URL/players/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "reward1": false, "reward2": false, "reward3": false}'

# Nom trop court -> 422
curl -X POST $BASE_URL/players/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Al", "reward1": false, "reward2": false, "reward3": false}'

# Modifier -> 200, Joe devient Joseph avec reward1 à true
curl -X PUT $BASE_URL/players/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "Joseph", "reward1": true, "reward2": false, "reward3": false}'

# Modifier un joueur inconnu -> 404
curl -X PUT $BASE_URL/players/999 \
  -H "Content-Type: application/json" \
  -d '{"name": "Ghost", "reward1": false, "reward2": false, "reward3": false}'

# Supprimer -> 204 (pas de corps), puis GET /players/2 renvoie 404
curl -i -X DELETE $BASE_URL/players/2

# Supprimer un joueur inconnu -> 404
curl -X DELETE $BASE_URL/players/999
```

## 5. Sessions

```bash
# Démarrer une session -> 200, id, team_name, current_room: 1,
# status: "in_progress", started_at
curl -X POST $BASE_URL/sessions/start \
  -H "Content-Type: application/json" \
  -d '{"team_name": "Root Squad"}'

# Nom d'équipe vide -> 422
curl -X POST $BASE_URL/sessions/start \
  -H "Content-Type: application/json" \
  -d '{"team_name": "   "}'

# Lire l'état de la session créée -> 200
curl $BASE_URL/sessions/1/state

# Session inconnue -> 404
curl $BASE_URL/sessions/999/state
```

### Jouer une partie dans une session

Chaque session a sa propre progression (`current_room`). On ne peut répondre
qu'à la salle active : une salle suivante renvoie `403`, une salle déjà
résolue ou une partie terminée renvoie `409`.

```bash
# Énoncé de la salle active -> 200, "resolue": false
curl $BASE_URL/sessions/1/rooms/1/enigma

# Salle pas encore débloquée -> 403
curl $BASE_URL/sessions/1/rooms/2/enigma

# Répondre à la salle 2 trop tôt -> 403
curl -X POST $BASE_URL/sessions/1/rooms/2/submit \
  -H "Content-Type: application/json" \
  -d '{"answer": "admin_token_1337"}'

# Mauvaise réponse -> 200, "success": false, "current_room": 1
curl -X POST $BASE_URL/sessions/1/rooms/1/submit \
  -H "Content-Type: application/json" \
  -d '{"answer": "faux"}'

# Partie complète : chaque bonne réponse fait avancer current_room
curl -X POST $BASE_URL/sessions/1/rooms/1/submit \
  -H "Content-Type: application/json" \
  -d '{"answer": "cle_externe_valide"}'

# Rejouer une salle résolue -> 409
curl -X POST $BASE_URL/sessions/1/rooms/1/submit \
  -H "Content-Type: application/json" \
  -d '{"answer": "cle_externe_valide"}'

curl -X POST $BASE_URL/sessions/1/rooms/2/submit \
  -H "Content-Type: application/json" \
  -d '{"answer": "admin_token_1337"}'

curl -X POST $BASE_URL/sessions/1/rooms/3/submit \
  -H "Content-Type: application/json" \
  -d '{"conditions": {"firewall_neutralise": true, "boucle_stoppee": true}}'

# Dernière salle -> "status": "victory"
curl -X POST $BASE_URL/sessions/1/rooms/4/submit \
  -H "Content-Type: application/json" \
  -d '{"answer": "reboot --force --patch=core"}'

# Soumettre après la victoire -> 409
curl -X POST $BASE_URL/sessions/1/rooms/4/submit \
  -H "Content-Type: application/json" \
  -d '{"answer": "reboot --force --patch=core"}'
```

## 6. Tout lancer d'un coup

Le script [`tests/curl_requests.sh`](../tests/curl_requests.sh) enchaîne toutes
ces requêtes et affiche le code HTTP de chacune :

```bash
./tests/curl_requests.sh
# ou sur une autre adresse :
BASE_URL=http://127.0.0.1:8001 ./tests/curl_requests.sh
```

## 7. Tests automatiques

Les mêmes cas sont couverts par pytest :

```bash
python -m pytest -q
```
