#!/usr/bin/env bash
# Requêtes curl pour tester l'API à la main (pendant de la suite pytest).
# Lancer d'abord le serveur : uvicorn app.main:app --reload
# Puis : ./tests/curl_requests.sh   (ou BASE_URL=http://autre:port ./tests/curl_requests.sh)

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
JSON="Content-Type: application/json"

run() {
    echo
    echo "### $1"
    shift
    curl -s -w "\n-> HTTP %{http_code}\n" "$@"
}

# --- Health check ---
run "GET / (health check)"                   "$BASE_URL/"

# --- Rooms ---
run "GET /rooms/ (liste des salles)"         "$BASE_URL/rooms/"
run "GET /rooms/1 (détail salle 1)"          "$BASE_URL/rooms/1"
run "GET /rooms/99 (salle inconnue -> 404)"  "$BASE_URL/rooms/99"

run "POST /rooms/1/submit (bonne réponse)" -X POST "$BASE_URL/rooms/1/submit" \
    -H "$JSON" -d '{"answer": "cle_externe_valide"}'
run "POST /rooms/1/submit (mauvaise réponse)" -X POST "$BASE_URL/rooms/1/submit" \
    -H "$JSON" -d '{"answer": "mauvaise_reponse"}'
run "POST /rooms/1/submit (réponse vide -> 422)" -X POST "$BASE_URL/rooms/1/submit" \
    -H "$JSON" -d '{"answer": "   "}'
run "POST /rooms/99/submit (salle inconnue -> 404)" -X POST "$BASE_URL/rooms/99/submit" \
    -H "$JSON" -d '{"answer": "x"}'
run "POST /rooms/2/submit (bonne réponse)" -X POST "$BASE_URL/rooms/2/submit" \
    -H "$JSON" -d '{"answer": "admin_token_1337"}'

run "POST /rooms/3/submit (mauvais format -> 422)" -X POST "$BASE_URL/rooms/3/submit" \
    -H "$JSON" -d '{"answer": "x"}'
run "POST /rooms/3/submit (conditions incomplètes)" -X POST "$BASE_URL/rooms/3/submit" \
    -H "$JSON" -d '{"conditions": {"firewall_neutralise": true, "boucle_stoppee": false}}'
run "POST /rooms/3/submit (conditions vides -> 422)" -X POST "$BASE_URL/rooms/3/submit" \
    -H "$JSON" -d '{"conditions": {}}'
run "POST /rooms/3/submit (bonnes conditions)" -X POST "$BASE_URL/rooms/3/submit" \
    -H "$JSON" -d '{"conditions": {"firewall_neutralise": true, "boucle_stoppee": true}}'

run "GET /rooms/status/game (avant victoire)" "$BASE_URL/rooms/status/game"
run "POST /rooms/4/submit (patch final -> victory)" -X POST "$BASE_URL/rooms/4/submit" \
    -H "$JSON" -d '{"answer": "reboot --force --patch=core"}'
run "GET /rooms/status/game (après victoire)" "$BASE_URL/rooms/status/game"

# --- Players ---
run "GET /players/"                          "$BASE_URL/players/"
run "GET /players/1"                         "$BASE_URL/players/1"
run "GET /players/999 (-> 404)"              "$BASE_URL/players/999"
run "POST /players/ (création)" -X POST "$BASE_URL/players/" \
    -H "$JSON" -d '{"name": "Alice", "reward1": false, "reward2": false, "reward3": false}'
run "POST /players/ (nom trop court -> 422)" -X POST "$BASE_URL/players/" \
    -H "$JSON" -d '{"name": "Al", "reward1": false, "reward2": false, "reward3": false}'
run "PUT /players/1 (mise à jour)" -X PUT "$BASE_URL/players/1" \
    -H "$JSON" -d '{"name": "Joseph", "reward1": true, "reward2": false, "reward3": false}'
run "PUT /players/999 (-> 404)" -X PUT "$BASE_URL/players/999" \
    -H "$JSON" -d '{"name": "Ghost", "reward1": false, "reward2": false, "reward3": false}'
run "DELETE /players/2"                      -X DELETE "$BASE_URL/players/2"
run "DELETE /players/999 (-> 404)"           -X DELETE "$BASE_URL/players/999"

# --- Sessions ---
run "POST /sessions/start" -X POST "$BASE_URL/sessions/start" \
    -H "$JSON" -d '{"team_name": "Root Squad"}'
run "POST /sessions/start (nom vide -> 422)" -X POST "$BASE_URL/sessions/start" \
    -H "$JSON" -d '{"team_name": "   "}'
run "GET /sessions/1/state"                  "$BASE_URL/sessions/1/state"
run "GET /sessions/999/state (-> 404)"       "$BASE_URL/sessions/999/state"

# --- Partie dans la session 1 ---
run "GET /sessions/1/rooms/1/enigma"         "$BASE_URL/sessions/1/rooms/1/enigma"
run "GET /sessions/1/rooms/2/enigma (verrouillée -> 403)" "$BASE_URL/sessions/1/rooms/2/enigma"
run "POST salle 2 trop tôt (-> 403)" -X POST "$BASE_URL/sessions/1/rooms/2/submit" \
    -H "$JSON" -d '{"answer": "admin_token_1337"}'
run "POST salle 1 mauvaise réponse" -X POST "$BASE_URL/sessions/1/rooms/1/submit" \
    -H "$JSON" -d '{"answer": "faux"}'
run "POST salle 1 bonne réponse (-> current_room 2)" -X POST "$BASE_URL/sessions/1/rooms/1/submit" \
    -H "$JSON" -d '{"answer": "cle_externe_valide"}'
run "POST salle 1 déjà résolue (-> 409)" -X POST "$BASE_URL/sessions/1/rooms/1/submit" \
    -H "$JSON" -d '{"answer": "cle_externe_valide"}'
run "POST salle 2 bonne réponse" -X POST "$BASE_URL/sessions/1/rooms/2/submit" \
    -H "$JSON" -d '{"answer": "admin_token_1337"}'
run "POST salle 3 bonnes conditions" -X POST "$BASE_URL/sessions/1/rooms/3/submit" \
    -H "$JSON" -d '{"conditions": {"firewall_neutralise": true, "boucle_stoppee": true}}'
run "POST salle 4 patch final (-> victory)" -X POST "$BASE_URL/sessions/1/rooms/4/submit" \
    -H "$JSON" -d '{"answer": "reboot --force --patch=core"}'
run "POST après victoire (-> 409)" -X POST "$BASE_URL/sessions/1/rooms/4/submit" \
    -H "$JSON" -d '{"answer": "reboot --force --patch=core"}'
