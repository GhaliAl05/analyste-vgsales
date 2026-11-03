# Tests du nettoyage : fichier propre régénéré par main(), et règle 1 sur des lignes inventées.

import os
import sys

# Permet d'importer nettoyer.py, qui se trouve dans le dossier parent.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import nettoyer


def lire_fichier_propre():
    """Régénère le fichier propre à partir du fichier brut, puis renvoie ses lignes."""
    nettoyer.main()
    lignes, colonnes = nettoyer.lire_csv(nettoyer.CHEMIN_PROPRE)
    return lignes


def test_nombre_de_lignes():
    """Le fichier propre doit contenir 16322 lignes."""
    lignes = lire_fichier_propre()
    assert len(lignes) == 16322


def test_annees_valides():
    """Aucune année "N/A" ni supérieure à 2016."""
    lignes = lire_fichier_propre()
    for ligne in lignes:
        assert ligne["Year"] != "N/A"
        assert int(ligne["Year"]) <= 2016


def test_editeurs_corriges():
    """Aucun éditeur "N/A", "Unknown" ou "Big Ben Interactive"."""
    lignes = lire_fichier_propre()
    for ligne in lignes:
        assert ligne["Publisher"] not in ["N/A", "Unknown", "Big Ben Interactive"]


def test_noms_sans_double_espace():
    """Aucun nom ne contient deux espaces à la suite."""
    lignes = lire_fichier_propre()
    for ligne in lignes:
        assert "  " not in ligne["Name"]


def test_regle_1_sur_trois_lignes():
    """La règle 1 retire seulement la ligne dont l'année vaut "N/A"."""
    lignes = [
        {"Name": "Jeu A", "Year": "2005"},
        {"Name": "Jeu B", "Year": "N/A"},
        {"Name": "Jeu C", "Year": "2010"},
    ]
    gardees, nb_retirees = nettoyer.retirer_annees_inconnues(lignes)
    assert len(gardees) == 2
    assert nb_retirees == 1
    assert gardees[0]["Name"] == "Jeu A"
    assert gardees[1]["Name"] == "Jeu C"
