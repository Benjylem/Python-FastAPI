"""Comportement de Door.est_ouverte, testé directement sur les objets domaine."""

from app.domain.Door import Door
from app.domain.session import Inventaire

REWARD = "cle_validation_externe"


def _door() -> Door:
    return Door(1, "Sas Pare-feu", "porte", True, REWARD, "Bien joué équipe !")


def test_porte_fermee_si_inventaire_vide():
    inventaire = Inventaire([REWARD])
    porte = _door()
    assert not porte.est_ouverte(inventaire)


def test_porte_ouverte_si_reward_present():
    inventaire = Inventaire([REWARD])
    inventaire.ajouter(REWARD)
    porte = _door()
    assert porte.est_ouverte(inventaire)


def test_porte_sans_condition_reste_fermee():
    inventaire = Inventaire([REWARD])
    porte = Door(2, "Sas ouvert", "porte", False, None, "ras")
    assert not porte.est_ouverte(inventaire)


def test_deux_inventaires_ne_s_influencent_pas():
    porte = _door()
    inventaire_equipe_a = Inventaire([REWARD])
    inventaire_equipe_b = Inventaire([REWARD])
    inventaire_equipe_a.ajouter(REWARD)
    assert porte.est_ouverte(inventaire_equipe_a)
    assert not porte.est_ouverte(inventaire_equipe_b)
