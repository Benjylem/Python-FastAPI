from app.domain.Room import Salle
from app.domain.Enigme import EnigmeChaine

enigme = EnigmeChaine(1, "prompt", "reponse")

def test_salle_sans_doors_a_sa_propre_liste():
    salle_a = Salle(1, "A", "bio", enigme)
    salle_b = Salle(2, "B", "bio", enigme)
    salle_a.doors.append("Porte A")
    assert not salle_a.doors is salle_b.doors
    assert  salle_b.doors == []
