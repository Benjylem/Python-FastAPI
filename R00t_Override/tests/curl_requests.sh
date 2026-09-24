#!/usr/bin/env bash
# Requêtes curl pour tester l'API à la main (pendant de la suite pytest).
# Détail de chaque requête et réponses attendues : docs/tests-curl.md
#
# Lancer d'abord le serveur (sur un serveur tout juste démarré, car le script
# suppose les données de départ) : uvicorn app.main:app --reload
# Puis : ./tests/curl_requests.sh   (ou BASE_URL=http://autre:port ./tests/curl_requests.sh)

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
JSON="Content-Type: application/json"
OK=0
KO=0

# run "<description>" <code HTTP attendu> <arguments curl...>
run() {
    local label="$1" attendu="$2"
    shift 2
    local reponse code
    reponse=$(curl -s -w "\n%{http_code}" "$@")
    code="${reponse##*$'\n'}"
    if [ "$code" = "$attendu" ]; then
        echo "✅ [$code] $label"
        OK=$((OK + 1))
    else
        echo "❌ [$code, attendu $attendu] $label"
        echo "   ${reponse%$'\n'*}"
        KO=$((KO + 1))
    fi
}

echo "--- Health check ---"
run "GET /"                                   200 "$BASE_URL/"

echo "--- Rooms (carte publique) ---"
run "GET /rooms/ (liste des salles)"          200 "$BASE_URL/rooms/"
run "GET /rooms/1 (nom et bio)"               200 "$BASE_URL/rooms/1"
run "GET /rooms/99 (salle inconnue)"          404 "$BASE_URL/rooms/99"

echo "--- Players ---"
run "GET /players/"                           200 "$BASE_URL/players/"
run "GET /players/1"                          200 "$BASE_URL/players/1"
run "GET /players/999 (joueur inconnu)"       404 "$BASE_URL/players/999"
run "POST /players/ (création d'Alice)"       200 -X POST "$BASE_URL/players/" -H "$JSON" -d '{"name": "Alice"}'
run "POST /players/ (nom trop court)"         422 -X POST "$BASE_URL/players/" -H "$JSON" -d '{"name": "Al"}'
run "PUT /players/1 (Joe devient Joseph)"     200 -X PUT "$BASE_URL/players/1" -H "$JSON" -d '{"name": "Joseph"}'
run "PUT /players/999 (joueur inconnu)"       404 -X PUT "$BASE_URL/players/999" -H "$JSON" -d '{"name": "Ghost"}'
run "DELETE /players/2"                       204 -X DELETE "$BASE_URL/players/2"
run "DELETE /players/999 (joueur inconnu)"    404 -X DELETE "$BASE_URL/players/999"

echo "--- Session : création et lobby ---"
run "POST /sessions/start (équipe 1)"         200 -X POST "$BASE_URL/sessions/start" -H "$JSON" -d '{"team_name": "Root Squad"}'
run "POST /sessions/start (nom vide)"         422 -X POST "$BASE_URL/sessions/start" -H "$JSON" -d '{"team_name": "   "}'
run "GET /sessions/1/state (lobby)"           200 "$BASE_URL/sessions/1/state"
run "GET /sessions/999/state (inconnue)"      404 "$BASE_URL/sessions/999/state"
run "GET enigma en lobby"                     409 "$BASE_URL/sessions/1/rooms/1/enigma"
run "POST submit en lobby"                    409 -X POST "$BASE_URL/sessions/1/rooms/1/submit" -H "$JSON" -d '{"answer": "root_override"}'
run "POST launch sans joueur"                 409 -X POST "$BASE_URL/sessions/1/launch"

echo "--- Session : équipe ---"
run "POST rejoindre l'équipe (joueur 1)"      200 -X POST "$BASE_URL/sessions/1/players" -H "$JSON" -d '{"player_id": 1}'
run "POST rejoindre deux fois"                409 -X POST "$BASE_URL/sessions/1/players" -H "$JSON" -d '{"player_id": 1}'
run "POST rejoindre (joueur inconnu)"         404 -X POST "$BASE_URL/sessions/1/players" -H "$JSON" -d '{"player_id": 999}'

echo "--- Session : lancement et timer ---"
run "POST launch (chrono de 60 min)"          200 -X POST "$BASE_URL/sessions/1/launch"
run "POST launch une 2e fois"                 409 -X POST "$BASE_URL/sessions/1/launch"
run "GET state (temps_restant ~3600)"         200 "$BASE_URL/sessions/1/state"

echo "--- Session : partie complète ---"
run "GET enigma salle 1"                      200 "$BASE_URL/sessions/1/rooms/1/enigma"
run "GET enigma salle 2 (verrouillée)"        403 "$BASE_URL/sessions/1/rooms/2/enigma"
run "POST salle 2 trop tôt"                   403 -X POST "$BASE_URL/sessions/1/rooms/2/submit" -H "$JSON" -d '{"answer": "ADMIN_TOKEN_X987F"}'
run "POST salle 1 réponse vide"               422 -X POST "$BASE_URL/sessions/1/rooms/1/submit" -H "$JSON" -d '{"answer": "   "}'
run "POST salle 1 mauvaise réponse"           200 -X POST "$BASE_URL/sessions/1/rooms/1/submit" -H "$JSON" -d '{"answer": "faux"}'
run "POST salle 1 bonne réponse"              200 -X POST "$BASE_URL/sessions/1/rooms/1/submit" -H "$JSON" -d '{"answer": "root_override"}'
run "POST salle 1 déjà résolue"               409 -X POST "$BASE_URL/sessions/1/rooms/1/submit" -H "$JSON" -d '{"answer": "root_override"}'
run "POST salle 2 bonne réponse"              200 -X POST "$BASE_URL/sessions/1/rooms/2/submit" -H "$JSON" -d '{"answer": "ADMIN_TOKEN_X987F"}'
run "POST salle 3 format answer"              422 -X POST "$BASE_URL/sessions/1/rooms/3/submit" -H "$JSON" -d '{"answer": "x"}'
run "POST salle 3 conditions vides"           422 -X POST "$BASE_URL/sessions/1/rooms/3/submit" -H "$JSON" -d '{"conditions": {}}'
run "POST salle 3 mauvaises conditions"       200 -X POST "$BASE_URL/sessions/1/rooms/3/submit" -H "$JSON" -d '{"conditions": {"bypass_firewall": true, "override_lock": "LOCKED", "port_status": 443}}'
run "POST salle 3 bonnes conditions"          200 -X POST "$BASE_URL/sessions/1/rooms/3/submit" -H "$JSON" -d '{"conditions": {"bypass_firewall": true, "override_lock": "ACTIVE", "port_status": 80}}'
run "POST salle 4 patch final (victoire)"     200 -X POST "$BASE_URL/sessions/1/rooms/4/submit" -H "$JSON" -d '{"answer": "system.reboot(true)"}'
run "POST après la victoire"                  409 -X POST "$BASE_URL/sessions/1/rooms/4/submit" -H "$JSON" -d '{"answer": "system.reboot(true)"}'
run "GET state (victory, inventaire plein)"   200 "$BASE_URL/sessions/1/state"

echo "--- Session : changer d'équipe ---"
run "POST /sessions/start (équipe 2)"         200 -X POST "$BASE_URL/sessions/start" -H "$JSON" -d '{"team_name": "Blue Team"}'
run "POST joueur 1 déjà dans l'équipe 1"      409 -X POST "$BASE_URL/sessions/2/players" -H "$JSON" -d '{"player_id": 1}'
run "DELETE joueur 1 quitte l'équipe 1"       200 -X DELETE "$BASE_URL/sessions/1/players/1"
run "POST joueur 1 rejoint l'équipe 2"        200 -X POST "$BASE_URL/sessions/2/players" -H "$JSON" -d '{"player_id": 1}'
run "DELETE joueur absent de l'équipe"        404 -X DELETE "$BASE_URL/sessions/1/players/1"

echo
echo "Résultat : $OK OK, $KO KO"
[ "$KO" -eq 0 ]
