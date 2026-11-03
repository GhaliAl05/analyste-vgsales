# Fonctions de statistiques simples (somme, moyenne, médiane, intervalles) sur les données nettoyées.


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
