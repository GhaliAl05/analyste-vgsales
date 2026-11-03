# Tests de l'arbitre (arbitre.py) et de son branchement dans agent.py, sans appeler Ollama.

import os
import sys

# Permet d'importer arbitre.py et agent.py, qui se trouvent dans le dossier parent.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import agent
import arbitre

# Le vrai résultat de l'outil pour la moyenne de Global_Sales des jeux Sports.
RESULTAT_SPORTS = {
    "statistique": "moyenne",
    "colonne": "Global_Sales",
    "filtre": "Genre = Sports",
    "resultat": 0.568,
    "n": 2304,
}
QUESTION_SPORTS = "Quelle est la moyenne des ventes mondiales des jeux de genre Sports ?"


# --- extraire_nombres ---

def test_extraire_virgule_et_milliers():
    """ "0,568" devient 0.568 et "2 304" devient 2304."""
    assert arbitre.extraire_nombres("0,568 million sur 2 304 jeux") == [0.568, 2304.0]


def test_extraire_virgule_decimale():
    """La virgule française est une virgule décimale : "0,568" donne 0.568 (et non 568)."""
    assert arbitre.extraire_nombres("0,568") == [0.568]


def test_extraire_cas_anglais():
    """Cas documenté : "2,304" écrit à l'anglaise est lu comme le décimal 2.304, pas 2304."""
    assert arbitre.extraire_nombres("2,304") == [2.304]


def test_extraire_espace_insecable():
    """Une espace insécable entre les milliers est aussi comprise."""
    assert arbitre.extraire_nombres("2\u00a0304 jeux") == [2304.0]


# --- verifier ---

def test_bon_resultat_autorise():
    """La réponse qui reprend le résultat et le nombre de jeux est autorisée."""
    reponse = "La moyenne est de 0,568 million d'exemplaires sur 2304 jeux."
    assert arbitre.verifier(reponse, [RESULTAT_SPORTS], QUESTION_SPORTS)["autorisee"] is True


def test_arrondi_honnete_autorise():
    """0,57 est à moins de 1 % de 0,568 : autorisé."""
    reponse = "La moyenne est d'environ 0,57 million d'exemplaires."
    assert arbitre.verifier(reponse, [RESULTAT_SPORTS], QUESTION_SPORTS)["autorisee"] is True


def test_arrondi_trop_grossier_bloque():
    """0,6 est à plus de 1 % de 0,568 : bloqué."""
    reponse = "La moyenne est d'environ 0,6 million d'exemplaires."
    verdict = arbitre.verifier(reponse, [RESULTAT_SPORTS], QUESTION_SPORTS)
    assert verdict["autorisee"] is False
    assert verdict["nombres_non_justifies"] == [0.6]


def test_nombre_invente_bloque():
    """Un nombre que l'outil n'a pas calculé est bloqué."""
    reponse = "La moyenne est de 0,568 million, et le meilleur jeu a fait 82 millions."
    verdict = arbitre.verifier(reponse, [RESULTAT_SPORTS], QUESTION_SPORTS)
    assert verdict["autorisee"] is False
    assert verdict["nombres_non_justifies"] == [82.0]


def test_sans_nombre_autorise():
    """Une réponse sans aucun nombre est autorisée."""
    reponse = "Je ne peux pas répondre à cette question."
    assert arbitre.verifier(reponse, [], QUESTION_SPORTS)["autorisee"] is True


def test_nombre_de_la_question_autorise():
    """Une année citée dans la question peut être reprise dans la réponse."""
    question = "Combien de jeux sont sortis en 2006 ?"
    resultat = {"statistique": "nombre", "colonne": "Global_Sales", "filtre": "Year = 2006",
                "resultat": 1008, "n": 1008}
    reponse = "En 2006, 1008 jeux sont sortis."
    assert arbitre.verifier(reponse, [resultat], question)["autorisee"] is True


# --- Intervalle de confiance : les bornes et le niveau sont des nombres autorisés ---

# Le vrai résultat de l'outil pour l'intervalle de confiance des jeux Sports.
INTERVALLE_SPORTS = {
    "statistique": "intervalle_confiance",
    "colonne": "Global_Sales",
    "filtre": "Genre = Sports",
    "resultat": 0.568,
    "n": 2304,
    "borne_basse": 0.482,
    "borne_haute": 0.654,
    "niveau": 95,
}
QUESTION_INTERVALLE = "Quelle est la marge d'erreur sur la moyenne des ventes des jeux Sports ?"


def test_intervalle_bornes_autorisees():
    """La réponse qui cite les deux bornes et « 95 % » est autorisée."""
    reponse = ("Avec 95 % de confiance, la moyenne est entre 0,482 et 0,654 million "
               "d'exemplaires (moyenne 0,568 sur 2304 jeux).")
    assert arbitre.verifier(reponse, [INTERVALLE_SPORTS], QUESTION_INTERVALLE)["autorisee"] is True


def test_intervalle_borne_inventee_bloquee():
    """Une borne haute inventée (0,75 au lieu de 0,654) est bloquée."""
    reponse = "Avec 95 % de confiance, la moyenne est entre 0,482 et 0,75 million d'exemplaires."
    verdict = arbitre.verifier(reponse, [INTERVALLE_SPORTS], QUESTION_INTERVALLE)
    assert verdict["autorisee"] is False
    assert verdict["nombres_non_justifies"] == [0.75]


# --- Test de triche : un faux modèle qui invente un nombre sans appeler l'outil ---

def faux_modele(messages, avec_outil):
    """Imite la réponse d'Ollama : répond directement avec un nombre inventé, sans appel d'outil."""
    return {"message": {"role": "assistant", "content": "La moyenne est de 42 millions d'exemplaires."}}


def test_triche_bloquee(monkeypatch):
    """Le faux modèle invente 42 : repondre() doit bloquer la réponse et le noter dans la trace."""
    monkeypatch.setattr(agent, "appeler_modele", faux_modele)
    trace = agent.repondre(QUESTION_SPORTS)
    assert trace["reponse_finale"].startswith("Réponse bloquée par l'arbitre")
    assert trace["arbitre"]["autorisee"] is False
    assert trace["arbitre"]["nombres_non_justifies"] == [42.0]
    assert trace["arbitre"]["reponse_modele"] == "La moyenne est de 42 millions d'exemplaires."
