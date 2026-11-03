# EVIDENCE

## Brique 1 — Outil

## Brique 3 — Règle imposée par le code

## Brique 6 — Données sales

**Ce que je montre** : de vraies données ouvertes (vgsales, Zenodo, CC BY 4.0) nettoyées par 6 règles écrites, avec un journal.
- Deux règles viennent d'un document : ventes en millions (page Zenodo de Gregory Smith) ; DS sortie en 2004 (Nintendo).
- Une contradiction relevée entre la documentation (plus de 100 000 exemplaires) et le fichier (618 jeux à 0.01).

**Fichiers** : `nettoyer.py`, `donnees/vgsales_brut.csv`, `donnees/vgsales_propre.csv`, `donnees/journal_nettoyage.md`, `tests/test_nettoyer.py`.

**Commande pour reproduire** :
```
python nettoyer.py
.venv/Scripts/python -m pytest
```

**Résultat attendu** : 16 598 lignes au départ, 16 322 après nettoyage, 5 tests passés.

## Brique 8 — Incertitude

## Brique 9 — Comparaison mesurée
