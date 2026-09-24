from app.domain.Enigme import EnigmeChaine, EnigmeConditionnelle, EnigmePatch

# Salles en dur pour tester ; remplacé plus tard par les vraies données/DB.
# Chaque salle porte son propre objet Enigme : une seule source de vérité par id,
# au lieu de deux dicts (salles / enigmes) tenus en synchro à la main.
salles = {
    1: {
        "name": "Pare-Feu",
        "bio": "Obtenez la Clé de Validation Externe",
        "enigme": EnigmeChaine(1, "Décode la chaîne fournie", reponse_attendue="cle_externe_valide"),
    },
    2: {
        "name": "Proxy",
        "bio": "Décrochez les Privilèges Intermédiaires",
        "enigme": EnigmeChaine(2, "Trouve le token dans les logs", reponse_attendue="admin_token_1337"),
    },
    3: {
        "name": "Contre-Mesures",
        "bio": "Récupérez le Module de Déchiffrement du Cœur",
        "enigme": EnigmeConditionnelle(
            3,
            "Neutralise la boucle de rétroaction",
            conditions_attendues={"firewall_neutralise": True, "boucle_stoppee": True},
        ),
    },
    4: {
        "name": "Noyau Central",
        "bio": "Injectez le patch et validez le reboot",
        "enigme": EnigmePatch(4, "Injecte le patch final", reponse_attendue="reboot --force --patch=core"),
    },
}
