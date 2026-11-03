# Nettoyage du fichier brut vgsales_brut.csv (données sales) vers un CSV propre.

import csv
import os

# Les chemins partent du dossier de ce fichier, pour marcher quel que soit le dossier courant.
DOSSIER_DONNEES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "donnees")
CHEMIN_BRUT = os.path.join(DOSSIER_DONNEES, "vgsales_brut.csv")
CHEMIN_PROPRE = os.path.join(DOSSIER_DONNEES, "vgsales_propre.csv")
CHEMIN_JOURNAL = os.path.join(DOSSIER_DONNEES, "journal_nettoyage.md")


def lire_csv(chemin):
    """Lit un fichier CSV et renvoie la liste des lignes (dictionnaires) et la liste des colonnes."""
    with open(chemin, newline="", encoding="utf-8") as fichier:
        lecteur = csv.DictReader(fichier)
        lignes = list(lecteur)
        colonnes = lecteur.fieldnames
    return lignes, colonnes


def retirer_annees_inconnues(lignes):
    """Règle 1 : retire les lignes dont l'année vaut "N/A". Renvoie (lignes gardées, nombre retiré)."""
    gardees = []
    for ligne in lignes:
        if ligne["Year"] != "N/A":
            gardees.append(ligne)
    return gardees, len(lignes) - len(gardees)


def retirer_annees_apres_2016(lignes):
    """Règle 2 : retire les lignes dont l'année est supérieure à 2016. Renvoie (lignes gardées, nombre retiré)."""
    gardees = []
    for ligne in lignes:
        if int(ligne["Year"]) <= 2016:
            gardees.append(ligne)
    return gardees, len(lignes) - len(gardees)


def retirer_ds_avant_2004(lignes):
    """Règle 3 : retire les jeux DS datés d'avant 2004. Renvoie (lignes gardées, nombre retiré)."""
    gardees = []
    for ligne in lignes:
        if ligne["Platform"] == "DS" and int(ligne["Year"]) < 2004:
            continue
        gardees.append(ligne)
    return gardees, len(lignes) - len(gardees)


def remplacer_editeurs_inconnus(lignes):
    """Règle 4 : remplace l'éditeur "N/A" ou "Unknown" par "Inconnu". Renvoie (lignes, nombre modifié)."""
    nb_modifiees = 0
    for ligne in lignes:
        if ligne["Publisher"] == "N/A" or ligne["Publisher"] == "Unknown":
            ligne["Publisher"] = "Inconnu"
            nb_modifiees = nb_modifiees + 1
    return lignes, nb_modifiees


def corriger_libelles_editeurs(lignes):
    """Règle 5 : unifie les éditeurs écrits de deux façons. Renvoie (lignes, nombre modifié)."""
    corrections = {
        "Big Ben Interactive": "Bigben Interactive",
        "Milestone S.r.l": "Milestone S.r.l.",
    }
    nb_modifiees = 0
    for ligne in lignes:
        if ligne["Publisher"] in corrections:
            ligne["Publisher"] = corrections[ligne["Publisher"]]
            nb_modifiees = nb_modifiees + 1
    return lignes, nb_modifiees


def corriger_doubles_espaces(lignes):
    """Règle 6 : remplace les doubles espaces du nom par un seul espace. Renvoie (lignes, nombre modifié)."""
    nb_modifiees = 0
    for ligne in lignes:
        nom = ligne["Name"]
        if "  " in nom:
            while "  " in nom:
                nom = nom.replace("  ", " ")
            ligne["Name"] = nom
            nb_modifiees = nb_modifiees + 1
    return lignes, nb_modifiees


def ecrire_csv(chemin, lignes, colonnes):
    """Écrit les lignes dans un fichier CSV avec les colonnes données, dans le même ordre."""
    with open(chemin, "w", newline="", encoding="utf-8") as fichier:
        ecrivain = csv.DictWriter(fichier, fieldnames=colonnes)
        ecrivain.writeheader()
        ecrivain.writerows(lignes)


def ecrire_journal(chemin, etapes, nb_depart):
    """Écrit le journal de nettoyage en Markdown à partir de la liste des étapes."""
    texte = "# Journal de nettoyage\n\n"
    texte = texte + "Fichier source : `donnees/vgsales_brut.csv` (" + str(nb_depart) + " lignes).\n"
    texte = texte + "Fichier produit : `donnees/vgsales_propre.csv`.\n\n"
    numero = 1
    for etape in etapes:
        texte = texte + "## Règle " + str(numero) + " : " + etape["regle"] + "\n\n"
        texte = texte + "- Justification : " + etape["justification"] + "\n"
        texte = texte + "- Lignes " + etape["action"] + " : " + str(etape["nombre"]) + "\n"
        texte = texte + "- Lignes restantes : " + str(etape["restantes"]) + "\n\n"
        numero = numero + 1
    texte = texte + "## Choix volontaires\n\n"
    texte = texte + "- Les deux lignes Madden NFL 13 / PS3 / 2012 sont gardées : ventes différentes, aucune preuve de doublon.\n"
    texte = texte + "- Global_Sales n'est pas modifié : les écarts de 0.02 avec la somme des régions sont des arrondis.\n\n"
    texte = texte + "## Règles venant d'un document\n\n"
    texte = texte + "- Les ventes sont en millions d'exemplaires (source : page Zenodo du jeu de données, Gregory Smith, https://zenodo.org/records/5898311).\n"
    texte = texte + "- La DS est sortie en 2004 (source : Nintendo).\n\n"
    texte = texte + "## Remarque\n\n"
    texte = texte + "La page Zenodo annonce des jeux à plus de 100 000 exemplaires, mais des jeux ont Global_Sales = 0.01 "
    texte = texte + "(10 000 exemplaires) : 618 dans le fichier brut, 603 après nettoyage. "
    texte = texte + "Ce seuil n'est donc pas respecté dans le fichier.\n"
    with open(chemin, "w", encoding="utf-8") as fichier:
        fichier.write(texte)


def main():
    """Applique les 6 règles dans l'ordre, puis écrit le fichier propre et le journal."""
    lignes, colonnes = lire_csv(CHEMIN_BRUT)
    nb_depart = len(lignes)
    etapes = []

    lignes, nombre = retirer_annees_inconnues(lignes)
    etapes.append({"regle": "retirer les lignes où Year vaut \"N/A\"",
                   "justification": "sans année, les données sont inutilisables pour les questions par période.",
                   "action": "retirées", "nombre": nombre, "restantes": len(lignes)})

    lignes, nombre = retirer_annees_apres_2016(lignes)
    etapes.append({"regle": "retirer les lignes où Year est supérieur à 2016",
                   "justification": "les données s'arrêtent en 2016 (3 jeux en 2017, 1 en 2020, aucun en 2018-2019).",
                   "action": "retirées", "nombre": nombre, "restantes": len(lignes)})

    lignes, nombre = retirer_ds_avant_2004(lignes)
    etapes.append({"regle": "retirer les lignes où Platform vaut \"DS\" et Year est inférieur à 2004",
                   "justification": "la DS est sortie en 2004, une date antérieure est impossible.",
                   "action": "retirées", "nombre": nombre, "restantes": len(lignes)})

    lignes, nombre = remplacer_editeurs_inconnus(lignes)
    etapes.append({"regle": "remplacer Publisher \"N/A\" et \"Unknown\" par \"Inconnu\"",
                   "justification": "deux marqueurs différents pour la même information manquante.",
                   "action": "modifiées", "nombre": nombre, "restantes": len(lignes)})

    lignes, nombre = corriger_libelles_editeurs(lignes)
    etapes.append({"regle": "\"Big Ben Interactive\" devient \"Bigben Interactive\", \"Milestone S.r.l\" devient \"Milestone S.r.l.\"",
                   "justification": "un même éditeur écrit de deux façons serait compté comme deux éditeurs.",
                   "action": "modifiées", "nombre": nombre, "restantes": len(lignes)})

    lignes, nombre = corriger_doubles_espaces(lignes)
    etapes.append({"regle": "dans Name, remplacer les doubles espaces par un seul espace",
                   "justification": "les doubles espaces sont des fautes de saisie qui gênent la recherche par nom.",
                   "action": "modifiées", "nombre": nombre, "restantes": len(lignes)})

    ecrire_csv(CHEMIN_PROPRE, lignes, colonnes)
    ecrire_journal(CHEMIN_JOURNAL, etapes, nb_depart)
    print("Nettoyage terminé :", len(lignes), "lignes écrites dans", CHEMIN_PROPRE)


if __name__ == "__main__":
    main()
