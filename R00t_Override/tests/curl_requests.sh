#!/usr/bin/env bash
# Parcours complet de l'API en curl (pendant manuel de la suite pytest).
# Chaque requête affiche la réponse et vérifie le code HTTP attendu ; bilan à la fin.
#
# 1. Lancer le serveur depuis R00t_Override/ :  uvicorn app.main:app
# 2. Dans un autre terminal :                     ./tests/curl_requests.sh
#    (ou BASE_URL=http://autre:port ./tests/curl_requests.sh)
#
# Le script crée ses propres équipes et joueurs : il peut être relancé sans
# redémarrer le serveur.

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
JSON="Content-Type: application/json"
OK=0
KO=0
BODY=""

vert() { printf '\033[32m%s\033[0m\n' "$1"; }
rouge() { printf '\033[31m%s\033[0m\n' "$1"; }

# check "<description>" <code HTTP attendu> <arguments curl...>
check() {
    local label="$1" attendu="$2"
    shift 2
    local reponse code
    reponse=$(curl -s -w '\n%{http_code}' "$@")
    code="${reponse##*$'\n'}"
    BODY="${reponse%$'\n'*}"
    echo
    if [ "$code" = "$attendu" ]; then
        vert "✔ [$code] $label"
        OK=$((OK + 1))
    else
        rouge "✘ [$code, attendu $attendu] $label"
        KO=$((KO + 1))
    fi
    [ -n "$BODY" ] && echo "  $BODY"
}

# Extrait un champ du dernier corps JSON reçu (sans dépendre de jq).
champ() {
    python3 -c "import json,sys; print(json.loads(sys.argv[1])$1)" "$BODY"
}

if ! curl -s -o /dev/null "$BASE_URL/"; then
    rouge "Serveur injoignable sur $BASE_URL : lance d'abord 'uvicorn app.main:app' depuis R00t_Override/"
    exit 1
fi

echo "=== Health check ==="
check "GET / (health check)" 200 "$BASE_URL/"

echo
echo "=== Rooms : carte publique (nom + bio, sans énoncé) ==="
check "Lister les salles" 200 "$BASE_URL/rooms/"
check "Détail salle 1" 200 "$BASE_URL/rooms/1"
check "Salle inconnue" 404 "$BASE_URL/rooms/99"

echo
echo "=== Players ==="
check "Lister les joueurs" 200 "$BASE_URL/players/"
check "Créer Alice" 200 -X POST "$BASE_URL/players/" -H "$JSON" -d '{"name": "Alice"}'
ALICE=$(champ '["id"]')
check "Créer Bob" 200 -X POST "$BASE_URL/players/" -H "$JSON" -d '{"name": "Bob"}'
BOB=$(champ '["id"]')
check "Lire Alice" 200 "$BASE_URL/players/$ALICE"
check "Joueur inconnu" 404 "$BASE_URL/players/999999"
check "Nom trop court" 422 -X POST "$BASE_URL/players/" -H "$JSON" -d '{"name": "Al"}'
check "Renommer Bob en Bobby" 200 -X PUT "$BASE_URL/players/$BOB" -H "$JSON" -d '{"name": "Bobby"}'
check "Renommer un joueur inconnu" 404 -X PUT "$BASE_URL/players/999999" -H "$JSON" -d '{"name": "Ghost"}'

echo
echo "=== Session : création de l'équipe (lobby) ==="
check "Créer l'équipe Hackers" 200 -X POST "$BASE_URL/sessions/start" -H "$JSON" -d '{"team_name": "Hackers"}'
S=$(champ '["id"]')
check "Nom d'équipe vide" 422 -X POST "$BASE_URL/sessions/start" -H "$JSON" -d '{"team_name": "   "}'
check "Session inconnue" 404 "$BASE_URL/sessions/999999/state"
check "Lancer sans joueur" 409 -X POST "$BASE_URL/sessions/$S/launch"
check "Énoncé avant lancement" 409 "$BASE_URL/sessions/$S/rooms/1/enigma"
check "Réponse avant lancement" 409 -X POST "$BASE_URL/sessions/$S/rooms/1/submit" -H "$JSON" -d '{"answer": "root_override"}'

echo
echo "=== Session : composition de l'équipe ==="
check "Alice rejoint" 200 -X POST "$BASE_URL/sessions/$S/players" -H "$JSON" -d "{\"player_id\": $ALICE}"
check "Alice rejoint deux fois" 409 -X POST "$BASE_URL/sessions/$S/players" -H "$JSON" -d "{\"player_id\": $ALICE}"
check "Joueur inconnu rejoint" 404 -X POST "$BASE_URL/sessions/$S/players" -H "$JSON" -d '{"player_id": 999999}'
check "Lancer la partie" 200 -X POST "$BASE_URL/sessions/$S/launch"
check "Lancer une deuxième fois" 409 -X POST "$BASE_URL/sessions/$S/launch"

echo
echo "=== Salle 1 : Pare-Feu (Base64) ==="
check "Énoncé salle 1" 200 "$BASE_URL/sessions/$S/rooms/1/enigma"
check "Énoncé salle 2 (verrouillée)" 403 "$BASE_URL/sessions/$S/rooms/2/enigma"
check "Réponse salle 2 trop tôt" 403 -X POST "$BASE_URL/sessions/$S/rooms/2/submit" -H "$JSON" -d '{"answer": "ADMIN_TOKEN_X987F"}'
check "Réponse vide" 422 -X POST "$BASE_URL/sessions/$S/rooms/1/submit" -H "$JSON" -d '{"answer": "   "}'
check "Chaîne encore encodée (success: false)" 200 -X POST "$BASE_URL/sessions/$S/rooms/1/submit" -H "$JSON" -d '{"answer": "cm9vdF9vdmVycmlkZQ=="}'
check "Bonne réponse (casse ignorée)" 200 -X POST "$BASE_URL/sessions/$S/rooms/1/submit" -H "$JSON" -d '{"answer": "ROOT_Override"}'
check "Salle 1 déjà résolue" 409 -X POST "$BASE_URL/sessions/$S/rooms/1/submit" -H "$JSON" -d '{"answer": "root_override"}'

echo
echo "=== Retardataire : Bob rejoint en cours de partie ==="
check "Bob rejoint (voit la progression)" 200 -X POST "$BASE_URL/sessions/$S/players" -H "$JSON" -d "{\"player_id\": $BOB}"

echo
echo "=== Salle 2 : Proxy & Logs ==="
check "Énoncé salle 2 (logs)" 200 "$BASE_URL/sessions/$S/rooms/2/enigma"
python3 -c "import json,sys; print(json.loads(sys.argv[1])['enigme'])" "$BODY"
check "Token leurre en minuscules (success: false)" 200 -X POST "$BASE_URL/sessions/$S/rooms/2/submit" -H "$JSON" -d '{"answer": "admin_token_x987f"}'
check "Bon token" 200 -X POST "$BASE_URL/sessions/$S/rooms/2/submit" -H "$JSON" -d '{"answer": "ADMIN_TOKEN_X987F"}'

echo
echo "=== Salle 3 : Contre-Mesures (JSON typé) ==="
check "Énoncé salle 3" 200 "$BASE_URL/sessions/$S/rooms/3/enigma"
check "Format answer au lieu de conditions" 422 -X POST "$BASE_URL/sessions/$S/rooms/3/submit" -H "$JSON" -d '{"answer": "x"}'
check "Conditions vides" 422 -X POST "$BASE_URL/sessions/$S/rooms/3/submit" -H "$JSON" -d '{"conditions": {}}'
check "1 au lieu de true (success: false)" 200 -X POST "$BASE_URL/sessions/$S/rooms/3/submit" -H "$JSON" \
    -d '{"conditions": {"bypass_firewall": 1, "override_lock": "ACTIVE", "port_status": 80}}'
check "Bonnes conditions" 200 -X POST "$BASE_URL/sessions/$S/rooms/3/submit" -H "$JSON" \
    -d '{"conditions": {"bypass_firewall": true, "override_lock": "ACTIVE", "port_status": 80}}'

echo
echo "=== Salle 4 : Noyau (patch final) ==="
check "Énoncé salle 4" 200 "$BASE_URL/sessions/$S/rooms/4/enigma"
check "Mauvais patch (success: false)" 200 -X POST "$BASE_URL/sessions/$S/rooms/4/submit" -H "$JSON" -d '{"answer": "system.reboot(false)"}'
check "Patch final (espaces + casse ignorés) -> victory" 200 -X POST "$BASE_URL/sessions/$S/rooms/4/submit" -H "$JSON" -d '{"answer": "  System.Reboot( TRUE ) "}'
check "Réponse après victoire" 409 -X POST "$BASE_URL/sessions/$S/rooms/4/submit" -H "$JSON" -d '{"answer": "system.reboot(true)"}'
check "État final (inventaire complet, victory)" 200 "$BASE_URL/sessions/$S/state"

echo
echo "=== Changement d'équipe ==="
check "Créer l'équipe Rivaux" 200 -X POST "$BASE_URL/sessions/start" -H "$JSON" -d '{"team_name": "Rivaux"}'
R=$(champ '["id"]')
check "Bob rejoint Rivaux sans quitter Hackers" 409 -X POST "$BASE_URL/sessions/$R/players" -H "$JSON" -d "{\"player_id\": $BOB}"
check "Bob quitte Hackers" 200 -X DELETE "$BASE_URL/sessions/$S/players/$BOB"
check "Bob rejoint Rivaux" 200 -X POST "$BASE_URL/sessions/$R/players" -H "$JSON" -d "{\"player_id\": $BOB}"
check "Quitter une équipe dont on ne fait pas partie" 404 -X DELETE "$BASE_URL/sessions/$S/players/$BOB"

echo
echo "=== Suppression des joueurs de test ==="
check "Supprimer Alice" 204 -X DELETE "$BASE_URL/players/$ALICE"
check "Supprimer Bob" 204 -X DELETE "$BASE_URL/players/$BOB"
check "Alice n'existe plus" 404 "$BASE_URL/players/$ALICE"

echo
echo "=========================================="
if [ "$KO" -eq 0 ]; then
    vert "Bilan : $OK OK, 0 KO"
else
    rouge "Bilan : $OK OK, $KO KO"
fi
[ "$KO" -eq 0 ]
