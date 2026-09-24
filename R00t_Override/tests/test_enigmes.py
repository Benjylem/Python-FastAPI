"""Règles de validation des énigmes, testées directement sur les objets domaine."""

from app.domain.Room import salles

SALLE3_OK = {"bypass_firewall": True, "override_lock": "ACTIVE", "port_status": 80}


def test_salle1_accepts_decoded_key_ignoring_case_and_spaces():
    assert salles[1].enigme.check_solution("root_override")
    assert salles[1].enigme.check_solution("  ROOT_Override ")


def test_salle1_rejects_encoded_key():
    # le joueur doit renvoyer la clé décodée, pas la chaîne Base64
    assert not salles[1].enigme.check_solution("cm9vdF9vdmVycmlkZQ==")


def test_salle2_accepts_exact_token():
    assert salles[2].enigme.check_solution("ADMIN_TOKEN_X987F")


def test_salle2_is_case_sensitive():
    # leurre présent dans les logs avec status=DENIED
    assert not salles[2].enigme.check_solution("admin_token_x987f")


def test_salle3_accepts_exact_conditions():
    assert salles[3].enigme.check_solution(SALLE3_OK)


def test_salle3_rejects_wrong_value():
    assert not salles[3].enigme.check_solution({**SALLE3_OK, "bypass_firewall": False})


def test_salle3_rejects_int_instead_of_bool():
    # en Python 1 == True : la comparaison de types doit l'empêcher
    assert not salles[3].enigme.check_solution({**SALLE3_OK, "bypass_firewall": 1})


def test_salle3_rejects_port_as_string():
    assert not salles[3].enigme.check_solution({**SALLE3_OK, "port_status": "80"})


def test_salle3_rejects_extra_key():
    assert not salles[3].enigme.check_solution({**SALLE3_OK, "debug": True})


def test_salle4_ignores_case_and_spaces():
    assert salles[4].enigme.check_solution("system.reboot(true)")
    assert salles[4].enigme.check_solution("  System.Reboot( TRUE ) ")


def test_salle4_rejects_wrong_patch():
    assert not salles[4].enigme.check_solution("system.reboot(false)")
