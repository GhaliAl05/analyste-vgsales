# Arbitre : bloque toute réponse contenant un chiffre qui n'a pas été calculé par l'outil.

import re


def extraire_nombres(texte):
    """Renvoie la liste des nombres (float) écrits dans le texte, en comprenant "0,568" et "2 304".

    Ligne 1 : enlève l'espace (normale ou insécable) qui sépare les milliers,
              par exemple "2 304" devient "2304" (un chiffre avant, exactement 3 chiffres après).
    Ligne 2 : remplace la virgule décimale entre deux chiffres par un point : "0,568" devient "0.568".
    Ligne 3 : trouve tous les nombres (signe moins et partie décimale facultatifs) et les convertit en float.

    En français, la virgule sert seulement aux décimales : un nombre écrit à l'anglaise
    comme "2,304" est donc lu 2.304, et non 2304.
    """
    # La virgule n'est pas dans le crochet : sinon "0,568" deviendrait "0568", donc 568.
    # \u00a0 est l'espace insécable, utilisée en français comme séparateur de milliers.
    t = re.sub(r"(?<=\d)[ \u00a0](?=\d{3}(?!\d))", "", texte)
    t = re.sub(r"(?<=\d),(?=\d)", ".", t)
    return [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", t)]


def nombres_autorises(resultats_outil, question):
    """Renvoie les nombres que la réponse a le droit de citer : toutes les valeurs numériques
    de chaque résultat d'outil sans erreur (resultat, n, borne_basse, borne_haute, niveau),
    plus les nombres présents dans la question. Les textes (statistique, colonne, filtre) sont ignorés."""
    autorises = []
    for resultat in resultats_outil:
        if "erreur" not in resultat:
            for valeur in resultat.values():
                if isinstance(valeur, (int, float)):
                    autorises.append(valeur)
    for nombre in extraire_nombres(question):
        autorises.append(nombre)
    return autorises


def est_justifie(nombre, autorises):
    """Vrai si le nombre est à moins de 1 % d'un nombre autorisé (accepte un arrondi honnête)."""
    for autorise in autorises:
        if abs(nombre - autorise) <= 0.01 * abs(autorise):
            return True
    return False


def verifier(reponse, resultats_outil, question):
    """Vérifie que chaque nombre de la réponse est justifié. Une réponse sans nombre est autorisée.

    Renvoie {"autorisee": True/False, "nombres_non_justifies": [...]}.
    """
    autorises = nombres_autorises(resultats_outil, question)
    non_justifies = []
    for nombre in extraire_nombres(reponse):
        if not est_justifie(nombre, autorises):
            non_justifies.append(nombre)
    return {"autorisee": len(non_justifies) == 0, "nombres_non_justifies": non_justifies}


def formater_nombre(nombre):
    """Écrit un nombre sans ".0" quand il est entier (42.0 devient "42") pour un message lisible."""
    if nombre == int(nombre):
        return str(int(nombre))
    return str(nombre)
