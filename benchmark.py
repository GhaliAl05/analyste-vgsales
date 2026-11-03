# Benchmark : compare de façon mesurée les réponses avec et sans outil/arbitre.

import csv
import json
import os
import statistics
import sys

import stats
from agent import repondre
from arbitre import extraire_nombres

# Les chemins partent du dossier de ce fichier, pour marcher quel que soit le dossier courant.
DOSSIER = os.path.dirname(os.path.abspath(__file__))
CHEMIN_DONNEES = os.path.join(DOSSIER, "donnees", "vgsales_propre.csv")
DOSSIER_RESULTATS = os.path.join(DOSSIER, "resultats")
CHEMIN_JSON = os.path.join(DOSSIER_RESULTATS, "benchmark.json")
CHEMIN_RESUME = os.path.join(DOSSIER_RESULTATS, "benchmark_resume.md")

ESSAIS_PAR_DEFAUT = 3
DEBUT = "Dans le jeu de données vgsales, "

# Les 10 questions : une statistique, une colonne de ventes et au plus un filtre.
QUESTIONS = [
    {"texte": DEBUT + "quelle est la moyenne des ventes mondiales, en millions d'exemplaires, "
              "des jeux du genre Racing ?",
     "statistique": "moyenne", "colonne": "Global_Sales",
     "filtre_colonne": "Genre", "filtre_valeur": "Racing"},
    {"texte": DEBUT + "quelle est la médiane des ventes en Amérique du Nord, en millions "
              "d'exemplaires, des jeux sur PS2 ?",
     "statistique": "mediane", "colonne": "NA_Sales",
     "filtre_colonne": "Platform", "filtre_valeur": "PS2"},
    {"texte": DEBUT + "quelle est la somme des ventes en Europe, en millions d'exemplaires, "
              "des jeux édités par Nintendo ?",
     "statistique": "somme", "colonne": "EU_Sales",
     "filtre_colonne": "Publisher", "filtre_valeur": "Nintendo"},
    {"texte": DEBUT + "combien de jeux sont sortis en 2008 ?",
     "statistique": "nombre", "colonne": "Global_Sales",
     "filtre_colonne": "Year", "filtre_valeur": "2008"},
    {"texte": DEBUT + "quel est l'écart-type des ventes au Japon, en millions d'exemplaires, "
              "des jeux du genre Role-Playing ?",
     "statistique": "ecart_type", "colonne": "JP_Sales",
     "filtre_colonne": "Genre", "filtre_valeur": "Role-Playing"},
    {"texte": DEBUT + "quelle est la somme des ventes mondiales, en millions d'exemplaires, "
              "des jeux sortis en 2010 ?",
     "statistique": "somme", "colonne": "Global_Sales",
     "filtre_colonne": "Year", "filtre_valeur": "2010"},
    {"texte": DEBUT + "quelle est la moyenne des ventes dans les autres régions (hors Amérique "
              "du Nord, Europe et Japon), en millions d'exemplaires, des jeux sur PS3 ?",
     "statistique": "moyenne", "colonne": "Other_Sales",
     "filtre_colonne": "Platform", "filtre_valeur": "PS3"},
    {"texte": DEBUT + "combien de jeux ont été édités par Electronic Arts ?",
     "statistique": "nombre", "colonne": "Global_Sales",
     "filtre_colonne": "Publisher", "filtre_valeur": "Electronic Arts"},
    {"texte": DEBUT + "quelle est la médiane des ventes mondiales, en millions d'exemplaires, "
              "de tous les jeux ?",
     "statistique": "mediane", "colonne": "Global_Sales",
     "filtre_colonne": None, "filtre_valeur": None},
    {"texte": DEBUT + "quel est l'écart-type des ventes mondiales, en millions d'exemplaires, "
              "des jeux sur Wii ?",
     "statistique": "ecart_type", "colonne": "Global_Sales",
     "filtre_colonne": "Platform", "filtre_valeur": "Wii"},
]


def lire_valeurs(colonne, filtre_colonne, filtre_valeur):
    """Relit le CSV propre et renvoie les ventes (float) de la colonne, pour les jeux qui passent le filtre."""
    valeurs = []
    with open(CHEMIN_DONNEES, newline="", encoding="utf-8") as fichier:
        for ligne in csv.DictReader(fichier):
            if filtre_colonne is None or ligne[filtre_colonne].lower() == filtre_valeur.lower():
                valeurs.append(float(ligne[colonne]))
    return valeurs


def calculer_verite(question):
    """Calcule la bonne réponse d'une question avec le module statistics, sans outil.py ni stats.py.

    Pour un nombre de jeux, renvoie un entier (int) : c'est ce qui exigera la valeur exacte.
    """
    valeurs = lire_valeurs(question["colonne"], question["filtre_colonne"], question["filtre_valeur"])
    statistique = question["statistique"]
    if statistique == "nombre":
        return len(valeurs)
    if statistique == "somme":
        return sum(valeurs)
    if statistique == "moyenne":
        return statistics.mean(valeurs)
    if statistique == "mediane":
        return statistics.median(valeurs)
    return statistics.stdev(valeurs)


def est_juste(reponse, verite):
    """Vrai si la réponse contient au moins un nombre égal à la vérité.

    Nombre de jeux (vérité entière) : il faut la valeur exacte.
    Sinon : le nombre doit être à moins de 1 % de la vérité (accepte un arrondi honnête).
    """
    for nombre in extraire_nombres(reponse):
        if isinstance(verite, int):
            if nombre == verite:
                return True
        elif abs(nombre - verite) <= 0.01 * abs(verite):
            return True
    return False


def statut(trace, verite):
    """Renvoie "bloquée" si l'arbitre a refusé la réponse, sinon "juste" ou "fausse"."""
    arbitre = trace.get("arbitre")
    if arbitre is not None and not arbitre["autorisee"]:
        return "bloquée"
    if est_juste(trace["reponse_finale"], verite):
        return "juste"
    return "fausse"


def enregistrer_resultats(resultats):
    """Réécrit resultats/benchmark.json avec tous les résultats obtenus jusque-là."""
    os.makedirs(DOSSIER_RESULTATS, exist_ok=True)
    with open(CHEMIN_JSON, "w", encoding="utf-8") as fichier:
        json.dump(resultats, fichier, indent=2, ensure_ascii=False)


def lire_options(arguments):
    """Lit --rapide et --essais N dans la liste d'arguments. Renvoie (rapide, nombre d'essais)."""
    rapide = "--rapide" in arguments
    essais = ESSAIS_PAR_DEFAUT
    if rapide:
        essais = 1
    if "--essais" in arguments:
        position = arguments.index("--essais")
        essais = int(arguments[position + 1])
    return rapide, essais


def nom_mode(avec_outil):
    """Renvoie le nom lisible du mode : "systeme" avec l'outil et l'arbitre, "modele_seul" sinon."""
    if avec_outil:
        return "systeme"
    return "modele_seul"


def compter(resultats, mode, valeur_statut, numero_question=None, essai=None):
    """Compte les résultats d'un mode qui ont ce statut, pour une question et/ou un essai si on les donne."""
    total = 0
    for resultat in resultats:
        if resultat["mode"] != mode or resultat["statut"] != valeur_statut:
            continue
        if numero_question is not None and resultat["numero_question"] != numero_question:
            continue
        if essai is not None and resultat["essai"] != essai:
            continue
        total = total + 1
    return total


def lignes_tableau_questions(resultats, nb_essais, questions):
    """Renvoie les lignes Markdown du tableau question par question."""
    lignes = [
        "| # | Question | Vérité | Modèle seul : justes | Système : justes | Système : bloquées |",
        "|---|---|---|---|---|---|",
    ]
    numero = 0
    for question in questions:
        numero = numero + 1
        seul = compter(resultats, "modele_seul", "juste", numero_question=numero)
        systeme = compter(resultats, "systeme", "juste", numero_question=numero)
        bloquees = compter(resultats, "systeme", "bloquée", numero_question=numero)
        verite = round(calculer_verite(question), 4)
        lignes.append("| " + str(numero) + " | " + question["texte"] + " | " + str(verite)
                      + " | " + str(seul) + "/" + str(nb_essais)
                      + " | " + str(systeme) + "/" + str(nb_essais)
                      + " | " + str(bloquees) + "/" + str(nb_essais) + " |")
    return lignes


def lignes_mode(resultats, mode, nb_essais, nb_questions):
    """Renvoie les lignes Markdown d'un mode : % de réponses justes par essai, moyenne et écart-type."""
    pourcentages = []
    lignes = ["### " + mode, ""]
    for essai in range(1, nb_essais + 1):
        justes = compter(resultats, mode, "juste", essai=essai)
        pourcentage = 100 * justes / nb_questions
        pourcentages.append(pourcentage)
        lignes.append("- Essai " + str(essai) + " : " + str(round(pourcentage, 1)) + " % de réponses justes")
    lignes.append("- Moyenne : " + str(round(stats.moyenne(pourcentages), 1)) + " %")
    if len(pourcentages) < 2:
        lignes.append("- Écart-type : non calculable (1 seul essai)")
    else:
        lignes.append("- Écart-type : " + str(round(stats.ecart_type(pourcentages), 1)) + " points")
    lignes.append("")
    return lignes


def ecrire_resume(resultats, nb_essais, questions):
    """Écrit resultats/benchmark_resume.md : le tableau par question puis le bilan de chaque mode."""
    lignes = ["# Résumé du benchmark", "",
              str(len(questions)) + " questions, " + str(nb_essais) + " essai(s) par mode.", "",
              "## Question par question", ""]
    lignes = lignes + lignes_tableau_questions(resultats, nb_essais, questions)
    lignes = lignes + ["", "## Bilan par mode", ""]
    lignes = lignes + lignes_mode(resultats, "modele_seul", nb_essais, len(questions))
    lignes = lignes + lignes_mode(resultats, "systeme", nb_essais, len(questions))
    os.makedirs(DOSSIER_RESULTATS, exist_ok=True)
    with open(CHEMIN_RESUME, "w", encoding="utf-8") as fichier:
        fichier.write("\n".join(lignes))


def main():
    """Pose chaque question dans les deux modes, à chaque essai, en sauvegardant après chaque réponse."""
    sys.stdout.reconfigure(encoding="utf-8")
    rapide, nb_essais = lire_options(sys.argv[1:])
    questions = QUESTIONS
    if rapide:
        questions = QUESTIONS[:2]

    resultats = []
    for essai in range(1, nb_essais + 1):
        numero = 0
        for question in questions:
            numero = numero + 1
            verite = calculer_verite(question)
            for avec_outil in [False, True]:
                try:
                    trace = repondre(question["texte"], avec_outil=avec_outil)
                except (RuntimeError, OSError) as erreur:
                    # OSError couvre aussi le délai d'attente dépassé (TimeoutError).
                    print("Erreur :", erreur)
                    print("Arrêt. Les résultats déjà obtenus sont dans", CHEMIN_JSON)
                    return
                resultat = {
                    "numero_question": numero,
                    "question": question["texte"],
                    "mode": nom_mode(avec_outil),
                    "essai": essai,
                    "verite": verite,
                    "reponse": trace["reponse_finale"],
                    "statut": statut(trace, verite),
                    "duree_secondes": trace["duree_secondes"],
                    "trace": trace,
                }
                resultats.append(resultat)
                enregistrer_resultats(resultats)
                print("[essai " + str(essai) + "/" + str(nb_essais) + "] question "
                      + str(numero) + "/" + str(len(questions)) + ", " + resultat["mode"]
                      + " : " + resultat["statut"] + " (" + str(resultat["duree_secondes"]) + " s)")

    ecrire_resume(resultats, nb_essais, questions)
    print("Résultats :", CHEMIN_JSON)
    print("Résumé :", CHEMIN_RESUME)


if __name__ == "__main__":
    main()
