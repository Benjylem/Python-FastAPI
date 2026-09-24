from app.domain.Enigme import Enigme, EnigmeChaine, EnigmeConditionnelle, EnigmePatch
from app.domain.GameElement import GameElement


class Salle(GameElement):
    def __init__(self, id: int, name: str, bio: str, enigme: Enigme, reward: str | None = None):
        super().__init__(id, name, bio)
        self.enigme = enigme
        # Objet ajouté à l'inventaire de l'équipe quand la salle est validée
        # (None pour la salle finale : la réussir fait gagner la partie).
        self.reward = reward


# Extrait de log fictif de la salle 2 : le token admin est noyé parmi des leurres
# (token expiré, token invité, casse différente).
LOGS_PROXY = """\
[2026-09-24 03:12:01] INFO  proxy: connexion entrante 10.0.3.14 -> gateway
[2026-09-24 03:12:04] WARN  auth: token expiré rejeté (GUEST_TOKEN_A11C2)
[2026-09-24 03:12:09] INFO  auth: session ouverte user=eve role=guest
[2026-09-24 03:13:27] DEBUG auth: élévation demandée role=admin token=ADMIN_TOKEN_X987F status=GRANTED
[2026-09-24 03:13:30] WARN  auth: tentative rejetée role=admin token=admin_token_x987f status=DENIED
[2026-09-24 03:14:02] INFO  proxy: purge du cache terminée"""

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
        reward="cle_validation_externe",
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
        reward="privileges_intermediaires",
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
        reward="module_dechiffrement",
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
    ),
]

# Index par id, utilisé par les routes : l'id n'est écrit qu'une fois, dans la Salle.
salles: dict[int, Salle] = {salle.id: salle for salle in _SALLES}
