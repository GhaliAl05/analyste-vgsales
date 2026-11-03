# Tests de stats.py et de l'outil calculer (outil.py), sans appeler le modèle.

import csv
import math
import os
import statistics
import sys

# Permet d'importer stats.py et outil.py, qui se trouvent dans le dossier parent.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import outil
import stats


def lire_csv_independant():
    """Relit le CSV propre sans passer par outil.py, pour un calcul de contrôle indépendant."""
    with open(outil.CHEMIN_PROPRE, newline="", encoding="utf-8") as fichier:
        return list(csv.DictReader(fichier))


# --- Exemples du corrigé de la séance 2 ---

def test_moyenne():
    """La moyenne de 1, 2, 3, 4 vaut 2.5."""
    assert stats.moyenne([1, 2, 3, 4]) == 2.5


def test_mediane_impaire():
    """Avec un nombre impair de valeurs, la médiane est celle du milieu."""
    assert stats.mediane([5, 1, 3]) == 3


def test_mediane_paire():
    """Avec un nombre pair de valeurs, la médiane est la moyenne des deux du milieu."""
    assert stats.mediane([4, 1, 3, 2]) == 2.5


def test_mediane_ne_modifie_pas_la_liste():
    """La médiane trie une copie : la liste reçue reste dans le même ordre."""
    liste = [4, 1, 3, 2]
    stats.mediane(liste)
    assert liste == [4, 1, 3, 2]


def test_ecart_type():
    """L'écart-type échantillon de cet exemple vaut environ 2.138."""
    assert abs(stats.ecart_type([2, 4, 4, 4, 5, 5, 7, 9]) - 2.138) < 0.001


def test_ecart_type_valeurs_identiques():
    """Des valeurs toutes égales ont un écart-type nul."""
    assert stats.ecart_type([5, 5, 5]) == 0


# --- calculer sur les vraies données, comparé au module statistics ---

def test_moyenne_sports():
    """La moyenne de Global_Sales des jeux Sports correspond au calcul fait avec statistics."""
    ventes = []
    for ligne in lire_csv_independant():
        if ligne["Genre"] == "Sports":
            ventes.append(float(ligne["Global_Sales"]))
    reponse = outil.calculer("moyenne", "Global_Sales", "Genre", "Sports")
    assert reponse["resultat"] == round(statistics.mean(ventes), 3)
    assert reponse["n"] == len(ventes)
    assert reponse["filtre"] == "Genre = Sports"


def test_nombre_wii():
    """Le nombre de jeux Wii correspond au comptage fait directement dans le CSV."""
    compte = 0
    for ligne in lire_csv_independant():
        if ligne["Platform"] == "Wii":
            compte = compte + 1
    reponse = outil.calculer("nombre", "Global_Sales", "Platform", "Wii")
    assert reponse["resultat"] == compte
    assert reponse["n"] == compte


# --- Souplesse du filtre ---

def test_annee_nombre_ou_texte():
    """L'année donnée comme nombre (2006) donne le même résultat que le texte "2006"."""
    avec_nombre = outil.calculer("nombre", "Global_Sales", "Year", 2006)
    avec_texte = outil.calculer("nombre", "Global_Sales", "Year", "2006")
    assert avec_nombre["resultat"] == avec_texte["resultat"]
    assert avec_nombre["resultat"] > 0


def test_majuscules_ignorees():
    """ "sports" en minuscules donne le même résultat que "Sports"."""
    minuscules = outil.calculer("moyenne", "Global_Sales", "Genre", "sports")
    normal = outil.calculer("moyenne", "Global_Sales", "Genre", "Sports")
    assert minuscules["resultat"] == normal["resultat"]
    assert minuscules["n"] == normal["n"]


# --- Cas d'erreur : un dictionnaire avec la clé "erreur", jamais de plantage ---

def test_statistique_inconnue():
    """Une statistique inconnue renvoie une erreur."""
    assert "erreur" in outil.calculer("maximum", "Global_Sales")


def test_colonne_inconnue():
    """Une colonne de ventes inconnue renvoie une erreur."""
    assert "erreur" in outil.calculer("moyenne", "FR_Sales")


def test_filtre_sans_resultat():
    """Un filtre qui ne trouve aucun jeu renvoie une erreur."""
    assert "erreur" in outil.calculer("moyenne", "Global_Sales", "Genre", "Cuisine")


def test_ecart_type_un_seul_jeu():
    """L'écart-type sur un seul jeu (seul jeu de l'éditeur Valve) renvoie une erreur."""
    assert "erreur" in outil.calculer("ecart_type", "Global_Sales", "Publisher", "Valve")


# --- Intervalle de confiance à 95 % ---

def intervalle_independant(xs):
    """Calcule l'intervalle à 95 % avec statistics et math, sans passer par stats.py."""
    m = statistics.mean(xs)
    marge = 1.96 * statistics.stdev(xs) / math.sqrt(len(xs))
    return (m - marge, m + marge)


def test_intervalle_confiance_95():
    """Sur les nombres de 1 à 40, les bornes correspondent au calcul indépendant."""
    xs = list(range(1, 41))
    borne_basse, borne_haute = stats.intervalle_confiance_95(xs)
    attendu_basse, attendu_haute = intervalle_independant(xs)
    assert abs(borne_basse - attendu_basse) < 1e-9
    assert abs(borne_haute - attendu_haute) < 1e-9


def test_intervalle_confiance_sports():
    """L'intervalle des ventes mondiales des jeux Sports correspond au calcul indépendant."""
    ventes = []
    for ligne in lire_csv_independant():
        if ligne["Genre"] == "Sports":
            ventes.append(float(ligne["Global_Sales"]))
    attendu_basse, attendu_haute = intervalle_independant(ventes)
    reponse = outil.calculer("intervalle_confiance", "Global_Sales", "Genre", "Sports")
    assert reponse["borne_basse"] == round(attendu_basse, 3)
    assert reponse["borne_haute"] == round(attendu_haute, 3)
    assert reponse["resultat"] == round(statistics.mean(ventes), 3)
    assert reponse["n"] == len(ventes)
    assert reponse["niveau"] == 95


def test_intervalle_trop_peu_de_jeux():
    """Moins de 30 jeux (9 jeux sortis en 1980) : l'intervalle renvoie une erreur."""
    reponse = outil.calculer("intervalle_confiance", "Global_Sales", "Year", "1980")
    assert "erreur" in reponse
    assert "au moins 30" in reponse["erreur"]
