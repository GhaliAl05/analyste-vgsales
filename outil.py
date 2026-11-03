# Outil de calcul appelé par le modèle : reçoit une requête et renvoie un résultat chiffré.

import csv
import os

import stats

# Le chemin part du dossier de ce fichier, pour marcher quel que soit le dossier courant.
DOSSIER_DONNEES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "donnees")
CHEMIN_PROPRE = os.path.join(DOSSIER_DONNEES, "vgsales_propre.csv")

# Les valeurs acceptées par l'outil.
STATISTIQUES = ["nombre", "somme", "moyenne", "mediane", "ecart_type", "intervalle_confiance"]

# En dessous de ce nombre de jeux, l'intervalle de confiance n'est pas fiable.
MINIMUM_INTERVALLE = 30
COLONNES_VENTES = ["Global_Sales", "NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales"]
COLONNES_FILTRE = ["Genre", "Platform", "Publisher", "Year"]


def charger():
    """Lit le CSV propre et renvoie la liste des jeux, avec les 5 colonnes de ventes converties en float."""
    with open(CHEMIN_PROPRE, newline="", encoding="utf-8") as fichier:
        lignes = list(csv.DictReader(fichier))
    for ligne in lignes:
        for colonne in COLONNES_VENTES:
            ligne[colonne] = float(ligne[colonne])
    return lignes


def filtrer(lignes, filtre_colonne, filtre_valeur):
    """Garde les jeux dont la colonne filtre_colonne vaut filtre_valeur (texte, sans tenir compte des majuscules)."""
    valeur_cherchee = str(filtre_valeur).lower()
    gardees = []
    for ligne in lignes:
        if str(ligne[filtre_colonne]).lower() == valeur_cherchee:
            gardees.append(ligne)
    return gardees


def appliquer_statistique(statistique, valeurs):
    """Calcule la statistique demandée (un nom de STATISTIQUES) sur la liste de nombres valeurs."""
    if statistique == "nombre":
        return len(valeurs)
    if statistique == "somme":
        return sum(valeurs)
    if statistique == "moyenne":
        return stats.moyenne(valeurs)
    if statistique == "mediane":
        return stats.mediane(valeurs)
    if statistique == "intervalle_confiance":
        # Le résultat principal d'un intervalle est la moyenne ; les bornes sont ajoutées dans calculer.
        return stats.moyenne(valeurs)
    return stats.ecart_type(valeurs)


def calculer(statistique, colonne, filtre_colonne=None, filtre_valeur=None):
    """Calcule une statistique sur une colonne de ventes, avec un filtre facultatif.

    Renvoie un dictionnaire avec le résultat, ou {"erreur": message} si la demande est invalide.
    """
    if statistique not in STATISTIQUES:
        return {"erreur": "Statistique inconnue : " + str(statistique)
                + ". Valeurs acceptées : " + ", ".join(STATISTIQUES) + "."}
    if colonne not in COLONNES_VENTES:
        return {"erreur": "Colonne inconnue : " + str(colonne)
                + ". Valeurs acceptées : " + ", ".join(COLONNES_VENTES) + "."}

    lignes = charger()
    texte_filtre = "aucun"
    if filtre_colonne is not None or filtre_valeur is not None:
        if filtre_colonne not in COLONNES_FILTRE:
            return {"erreur": "Colonne de filtre inconnue : " + str(filtre_colonne)
                    + ". Valeurs acceptées : " + ", ".join(COLONNES_FILTRE) + "."}
        if filtre_valeur is None:
            return {"erreur": "Il manque filtre_valeur : donne la valeur cherchée dans la colonne "
                    + filtre_colonne + "."}
        lignes = filtrer(lignes, filtre_colonne, filtre_valeur)
        texte_filtre = filtre_colonne + " = " + str(filtre_valeur)

    if len(lignes) == 0:
        return {"erreur": "Aucun jeu ne correspond au filtre " + texte_filtre
                + ". Vérifie l'orthographe de la valeur."}
    if statistique == "ecart_type" and len(lignes) < 2:
        return {"erreur": "L'écart-type demande au moins 2 jeux, or un seul jeu correspond au filtre "
                + texte_filtre + "."}
    if statistique == "intervalle_confiance" and len(lignes) < MINIMUM_INTERVALLE:
        return {"erreur": "Trop peu de jeux pour un intervalle fiable, il en faut au moins "
                + str(MINIMUM_INTERVALLE) + " ; le filtre " + texte_filtre + " n'en donne que "
                + str(len(lignes)) + "."}

    valeurs = []
    for ligne in lignes:
        valeurs.append(ligne[colonne])

    resultat = {
        "statistique": statistique,
        "colonne": colonne,
        "filtre": texte_filtre,
        "resultat": round(appliquer_statistique(statistique, valeurs), 3),
        "n": len(valeurs),
    }
    if statistique == "intervalle_confiance":
        borne_basse, borne_haute = stats.intervalle_confiance_95(valeurs)
        resultat["borne_basse"] = round(borne_basse, 3)
        resultat["borne_haute"] = round(borne_haute, 3)
        resultat["niveau"] = 95
    return resultat


# Description de l'outil au format « tools » d'Ollama (servira à l'étape suivante).
DESCRIPTION_OUTIL = {
    "type": "function",
    "function": {
        "name": "calculer",
        "description": "Calcule une statistique sur les ventes de jeux vidéo (en millions d'exemplaires), "
                       "sur tous les jeux ou sur ceux qui correspondent à un filtre. "
                       "Pour une question sur l'incertitude, la marge d'erreur ou un intervalle, "
                       "utilise la statistique intervalle_confiance : elle renvoie la moyenne "
                       "et les bornes de son intervalle de confiance à 95 % (au moins 30 jeux).",
        "parameters": {
            "type": "object",
            "properties": {
                "statistique": {
                    "type": "string",
                    "enum": STATISTIQUES,
                    "description": "La statistique à calculer. intervalle_confiance donne "
                                   "la moyenne avec sa marge d'erreur à 95 %.",
                },
                "colonne": {
                    "type": "string",
                    "enum": COLONNES_VENTES,
                    "description": "La colonne de ventes : mondiales, Amérique du Nord, Europe, Japon ou autres.",
                },
                "filtre_colonne": {
                    "type": "string",
                    "enum": COLONNES_FILTRE,
                    "description": "Facultatif : la colonne sur laquelle filtrer les jeux.",
                },
                "filtre_valeur": {
                    "type": "string",
                    "description": "Facultatif : la valeur cherchée dans filtre_colonne (par exemple Sports, Wii, Nintendo, 2006).",
                },
            },
            "required": ["statistique", "colonne"],
        },
    },
}
