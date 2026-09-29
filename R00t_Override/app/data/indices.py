# Indices d'Eve, en dur, par id de salle : du plus vague au plus précis.
# Chaque indice révélé coûte du temps à l'équipe (voir PENALITE_INDICE dans
# app/domain/session.py). Aucun indice ne donne la réponse telle quelle.
indices: dict[int, list[str]] = {
    1: [
        "Ce « == » à la fin de la clé ne te dit rien ? C'est la signature d'un encodage très courant.",
        "C'est du Base64. Dans un terminal : echo 'cm9vdF9vdmVycmlkZQ==' | base64 -d",
        "La clé en clair est deux mots reliés par un underscore : le nom même de l'opération en cours.",
    ],
    2: [
        "Ignore les lignes INFO : le token intéressant apparaît lors d'une élévation de privilèges.",
        "Plusieurs tokens admin apparaissent, mais un seul a le statut GRANTED.",
        "Le proxy respecte la casse : recopie le token exactement comme dans la ligne GRANTED.",
    ],
    3: [
        "Renvoie exactement les trois mêmes clés que dans l'état actuel, sans en ajouter.",
        'Les types comptent : un booléen reste un booléen, une chaîne une chaîne, et un port un entier (80, pas "80").',
        "Contourner le pare-feu = true, le verrou passe de LOCKED à ACTIVE, et le port HTTP standard est le 80.",
    ],
    4: [
        "On te demande un appel de méthode, au format objet.methode(argument).",
        "L'objet s'appelle system et la méthode reboot.",
        "Le booléen vrai s'écrit en minuscules, comme en JSON : true.",
    ],
}
