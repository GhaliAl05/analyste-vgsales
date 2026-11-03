# Fonctions de statistiques simples (somme, moyenne, médiane, écart-type, intervalle de confiance) sur les données nettoyées.


def moyenne(xs):
    """Renvoie la moyenne de la liste xs : la somme des valeurs divisée par leur nombre."""
    return sum(xs) / len(xs)


def mediane(xs):
    """Renvoie la médiane de xs (la valeur du milieu une fois triée). Ne modifie pas la liste reçue."""
    t = sorted(xs)
    n = len(t)
    if n % 2 == 1:
        return t[n // 2]
    return (t[n // 2 - 1] + t[n // 2]) / 2


def ecart_type(xs):
    """Renvoie l'écart-type « échantillon » de xs (division par n - 1). Demande au moins 2 valeurs."""
    m = moyenne(xs)
    return (sum((x - m) ** 2 for x in xs) / (len(xs) - 1)) ** 0.5


def intervalle_confiance_95(xs):
    """Renvoie (borne_basse, borne_haute), l'intervalle de confiance à 95 % de la moyenne de xs.

    Formule : moyenne ± 1.96 × écart-type / racine(n).
    1.96 vient de la loi normale : 95 % des valeurs tombent à moins de 1.96 écart-type
    du centre. C'est ce qui donne le niveau de 95 %.
    On divise par racine(n) car la moyenne de n valeurs varie moins qu'une valeur seule :
    sa dispersion vaut écart-type / racine(n). Plus il y a de jeux, plus l'intervalle est étroit.
    """
    m = moyenne(xs)
    marge = 1.96 * ecart_type(xs) / len(xs) ** 0.5
    return (m - marge, m + marge)
