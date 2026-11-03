# Tests de benchmark.py (est_juste, statut, vérités, options), sans appeler Ollama.

import os
import sys

# Permet d'importer benchmark.py, qui se trouve dans le dossier parent.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import benchmark


def trace_inventee(reponse, arbitre=None):
    """Fabrique une trace minimale, comme celle renvoyée par agent.repondre."""
    return {"reponse_finale": reponse, "arbitre": arbitre}


# --- est_juste ---

def test_est_juste_bonne_valeur():
    assert benchmark.est_juste("La moyenne est de 0.5928 million.", 0.5928)


def test_est_juste_arrondi_moins_de_1_pourcent():
    assert benchmark.est_juste("Environ 0,593 million d'exemplaires.", 0.5928)


def test_est_juste_ecriture_francaise():
    assert benchmark.est_juste("La somme vaut 418,3 millions.", 418.3)


def test_est_juste_valeur_fausse():
    assert not benchmark.est_juste("La moyenne est de 1.2 million.", 0.5928)


def test_est_juste_ecart_plus_de_1_pourcent():
    # 0.60 est à 1,2 % de 0.5928 : refusé.
    assert not benchmark.est_juste("Environ 0.60 million.", 0.5928)


def test_est_juste_nombre_de_jeux_exact():
    assert benchmark.est_juste("1428 jeux sont sortis en 2008.", 1428)


def test_est_juste_nombre_de_jeux_pas_exact():
    # 1427 est à moins de 1 %, mais un nombre de jeux doit être exact.
    assert not benchmark.est_juste("1427 jeux sont sortis en 2008.", 1428)


def test_est_juste_milliers_avec_espace():
    assert benchmark.est_juste("Il y a 1 339 jeux.", 1339)


def test_est_juste_sans_nombre():
    assert not benchmark.est_juste("Je ne sais pas.", 0.17)


# --- statut ---

def test_statut_juste_modele_seul():
    assert benchmark.statut(trace_inventee("La médiane est 0.17."), 0.17) == "juste"


def test_statut_fausse_modele_seul():
    assert benchmark.statut(trace_inventee("La médiane est 0.5."), 0.17) == "fausse"


def test_statut_juste_systeme_autorise():
    arbitre = {"autorisee": True, "nombres_non_justifies": []}
    trace = trace_inventee("La médiane est 0.17 sur 16322 jeux.", arbitre)
    assert benchmark.statut(trace, 0.17) == "juste"


def test_statut_bloquee():
    arbitre = {"autorisee": False, "nombres_non_justifies": [0.5]}
    trace = trace_inventee("Réponse bloquée par l'arbitre : les nombres 0.5 n'ont été calculés par aucun outil.", arbitre)
    assert benchmark.statut(trace, 0.17) == "bloquée"


def test_statut_pas_de_reponse_finale():
    trace = trace_inventee("Pas de réponse finale après 5 tours.")
    assert benchmark.statut(trace, 0.17) == "fausse"


# --- calculer_verite et lire_options ---

def test_verite_nombre_est_un_entier_exact():
    verite = benchmark.calculer_verite(benchmark.QUESTIONS[3])
    assert verite == 1428
    assert isinstance(verite, int)


def test_verite_mediane_sans_filtre():
    assert abs(benchmark.calculer_verite(benchmark.QUESTIONS[8]) - 0.17) < 1e-9


def test_options_par_defaut():
    assert benchmark.lire_options([]) == (False, 3)


def test_options_rapide_et_essais():
    assert benchmark.lire_options(["--rapide"]) == (True, 1)
    assert benchmark.lire_options(["--essais", "5"]) == (False, 5)
