# EVIDENCE

## Brique 1 — Outil

**Ce que je montre** : le modèle Qwen3.5-4B (local, via Ollama) appelle ma fonction `calculer()`.
- La trace montre l'appel réel, ses arguments, le résultat renvoyé par l'outil et la réponse finale qui reprend ce résultat.
- En comparaison, sans outil, le modèle répond hors sujet : un chiffre d'affaires en dollars, cité de mémoire.

**Fichiers** : `outil.py`, `stats.py`, `agent.py`, `tests/test_outil.py`, `traces/trace_2026-11-03_13-51-46.json` (avec outil), `traces/trace_2026-11-03_13-53-28.json` (sans outil).

**Commandes pour reproduire** :
```
python agent.py "Quelle est la moyenne des ventes mondiales des jeux de genre Sports ?"
python agent.py "Quelle est la moyenne des ventes mondiales des jeux de genre Sports ?" --sans-outil
.venv/Scripts/python -m pytest
```

**Résultat attendu** : appel de `calculer("moyenne", "Global_Sales", "Genre", "Sports")`, résultat 0.568 sur 2304 jeux, repris dans la réponse finale ; 19 tests passés (dont 15 pour l'outil).
Chaque nouvelle exécution produit une nouvelle trace dans `traces/`, et la formulation de la réponse du modèle peut varier d'un essai à l'autre.

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
