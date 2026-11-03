# Journal de nettoyage

Fichier source : `donnees/vgsales_brut.csv` (16598 lignes).
Fichier produit : `donnees/vgsales_propre.csv`.

## Règle 1 : retirer les lignes où Year vaut "N/A"

- Justification : sans année, les données sont inutilisables pour les questions par période.
- Lignes retirées : 271
- Lignes restantes : 16327

## Règle 2 : retirer les lignes où Year est supérieur à 2016

- Justification : les données s'arrêtent en 2016 (3 jeux en 2017, 1 en 2020, aucun en 2018-2019).
- Lignes retirées : 4
- Lignes restantes : 16323

## Règle 3 : retirer les lignes où Platform vaut "DS" et Year est inférieur à 2004

- Justification : la DS est sortie en 2004, une date antérieure est impossible.
- Lignes retirées : 1
- Lignes restantes : 16322

## Règle 4 : remplacer Publisher "N/A" et "Unknown" par "Inconnu"

- Justification : deux marqueurs différents pour la même information manquante.
- Lignes modifiées : 136
- Lignes restantes : 16322

## Règle 5 : "Big Ben Interactive" devient "Bigben Interactive", "Milestone S.r.l" devient "Milestone S.r.l."

- Justification : un même éditeur écrit de deux façons serait compté comme deux éditeurs.
- Lignes modifiées : 9
- Lignes restantes : 16322

## Règle 6 : dans Name, remplacer les doubles espaces par un seul espace

- Justification : les doubles espaces sont des fautes de saisie qui gênent la recherche par nom.
- Lignes modifiées : 5
- Lignes restantes : 16322

## Choix volontaires

- Les deux lignes Madden NFL 13 / PS3 / 2012 sont gardées : ventes différentes, aucune preuve de doublon.
- Global_Sales n'est pas modifié : les écarts de 0.02 avec la somme des régions sont des arrondis.

## Règles venant d'un document

- Les ventes sont en millions d'exemplaires (source : page Zenodo du jeu de données, Gregory Smith, https://zenodo.org/records/5898311).
- La DS est sortie en 2004 (source : Nintendo).

## Remarque

La page Zenodo annonce des jeux à plus de 100 000 exemplaires, mais des jeux ont Global_Sales = 0.01 (10 000 exemplaires) : 618 dans le fichier brut, 603 après nettoyage. Ce seuil n'est donc pas respecté dans le fichier.
