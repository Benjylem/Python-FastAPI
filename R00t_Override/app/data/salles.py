from app.domain.Door import Door
from app.domain.Enigme import EnigmeChaine, EnigmeConditionnelle, EnigmePatch
from app.domain.Room import Salle

# Extrait de log fictif de la salle 2 : le token admin est noyé parmi des leurres
# (token expiré, token invité, casse différente).
LOGS_PROXY = """\
[2026-09-24 03:12:01] INFO  proxy: connexion entrante 10.0.3.14 -> gateway
[2026-09-24 03:12:04] WARN  auth: token expiré rejeté (GUEST_TOKEN_A11C2)
[2026-09-24 03:12:09] INFO  auth: session ouverte user=eve role=guest
[2026-09-24 03:13:27] DEBUG auth: élévation demandée role=admin token=ADMIN_TOKEN_X987F status=GRANTED
[2026-09-24 03:13:30] WARN  auth: tentative rejetée role=admin token=admin_token_x987f status=DENIED
[2026-09-24 03:14:02] INFO  proxy: purge du cache terminée"""

REWARD_SALLE_1 = "cle_validation_externe"
MESSAGE_EVE_1 = "Joli coup, le pare-feu externe est aveuglé ! Mais ne crions pas victoire trop vite, l'IA redirige les flux de données. Pour avancer plus loin dans le serveur, il va falloir fouiller ses vieux journaux de bord. Regardez les logs du proxy, trouvez-moi ce foutu token administrateur avant qu'elle ne ferme la brèche !"

REWARD_SALLE_2 = "privileges_intermediaires"
MESSAGE_EVE_2 = "Bien reçu, j'ai les privilèges intermédiaires ! On est passés de l'autre côté de la porte de service. Par contre, ça bouge dans le sous-système... L'IA a activé ses matrices de contre-mesures automatiques pour nous griller les circuits. Analysez son script de défense et neutralisez ses boucles logiques avant que notre session ne saute !"

REWARD_SALLE_3 = "module_dechiffrement"
MESSAGE_EVE_3 = "C'est passé ! Les contre-mesures sont neutralisées, le chemin est libre jusqu'au cœur. On y est presque... Le terminal principal s'ouvre, mais son script de black-out est sur le point de s'exécuter. Préparez-vous, il ne reste plus qu'à lui balancer le patch de reboot final dans le code source. Ne tremblez pas !"

MESSAGE_VICTOIRE = "C'COMPILÉ ! Regardez le dashboard... Le compte à rebours s'est arrêté à zéro ! L'IA est redémarrée en mode sans échec et le trafic mondial est rétabli. Bien joué l'équipe, on l'a échappé belle. Le WWW est sauvé, vous méritez bien une bonne pause café !"

# Salles en dur pour tester ; remplacé plus tard par les vraies données/DB.
# Chaque salle porte son propre objet Enigme : une seule source de vérité par id.
_SALLES = [
    Salle(
        1,
        "Pare-Feu",
        "Obtenez la Clé de Validation Externe",
        EnigmeChaine(
            1,
            "Le pare-feu a intercepté une clé encodée : cm9vdF9vdmVycmlkZQ== . "
            "Décode-la et renvoie la clé en clair.",
            reponse_attendue="root_override",
            ignorer_casse=True,
        ),
        reward=REWARD_SALLE_1,
        doors=[
            Door(1, "Pare-Feu contourné", "Clé Obtenue !", True, REWARD_SALLE_1, MESSAGE_EVE_1)
        ]
    ),
    Salle(
        2,
        "Proxy & Logs",
        "Décrochez les Privilèges Intermédiaires",
        EnigmeChaine(
            2,
            "Analyse les logs du proxy et renvoie le token admin qui a été accepté.\n" + LOGS_PROXY,
            reponse_attendue="ADMIN_TOKEN_X987F",
        ),
        reward=REWARD_SALLE_2,
        doors=[
            Door(2, "Logs analysés", "Token identifié", True, REWARD_SALLE_2, MESSAGE_EVE_2)
        ]
    ),
    Salle(
        3,
        "Contre-Mesures",
        "Récupérez le Module de Déchiffrement du Cœur",
        EnigmeConditionnelle(
            3,
            'Contre-mesure active. État actuel : {"bypass_firewall": false, '
            '"override_lock": "LOCKED", "port_status": 443}. Pour la neutraliser : '
            "contourne le pare-feu, passe le verrou en mode ACTIVE et bascule le trafic "
            "sur le port HTTP standard. Renvoie l'état corrigé (mêmes clés, mêmes types).",
            conditions_attendues={"bypass_firewall": True, "override_lock": "ACTIVE", "port_status": 80},
        ),
        reward=REWARD_SALLE_3,
        doors=[
            Door(3, "Contre-mesure désactivé", "By-pass actif !", True, REWARD_SALLE_3, MESSAGE_EVE_3)
        ]
    ),
    Salle(
        4,
        "Noyau Central",
        "Injectez le patch et validez le reboot",
        EnigmePatch(
            4,
            "Le noyau attend la commande de redémarrage forcé : appelle la méthode reboot "
            "de l'objet system avec le booléen vrai.",
            reponse_attendue="system.reboot(true)",
        ),
        message_victoire=MESSAGE_VICTOIRE
    ),
]

# Index par id, utilisé par les routes : l'id n'est écrit qu'une fois, dans la Salle.
salles: dict[int, Salle] = {salle.id: salle for salle in _SALLES}
