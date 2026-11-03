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

**Ce que je montre** : une règle imposée par le code et non par le prompt : aucune réponse finale ne peut contenir un nombre qui n'a pas été calculé par l'outil (tolérance de 1 % pour les arrondis).
- Toute réponse du modèle passe obligatoirement par l'arbitre (`agent.py`, fonction `appliquer_arbitre`).
- Un test remplace le modèle par un faux modèle qui triche (« 42 millions » sans appel d'outil) : la réponse est bloquée.

**Fichiers** : `arbitre.py`, `agent.py`, `tests/test_arbitre.py`, `traces/trace_2026-11-03_14-23-46.json` (une vraie réponse autorisée par l'arbitre).

**Commandes pour reproduire** :
```
.venv/Scripts/python -m pytest tests/test_arbitre.py
python agent.py "Quelle est la moyenne des ventes mondiales des jeux de genre Sports ?"
```
Le test de triche est `test_triche_bloquee`.

**Résultat attendu** : 11 tests passés ; la vraie réponse (0,568 sur 2304 jeux) est autorisée, avec `"arbitre": {"autorisee": true, ...}` dans la trace.

**Ce que les tests ont révélé** : la fonction `extraire()` reprise du `comparer.py` du cours lisait « 0,568 » comme 568 (la virgule suivie de 3 chiffres était prise pour un séparateur de milliers anglais). L'arbitre aurait bloqué les bonnes réponses. J'ai retiré la virgule du premier crochet ; un test documente le cas anglais (« 2,304 » est lu 2.304).

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

**Ce que je montre** : un intervalle de confiance à 95 % de la moyenne (moyenne ± 1,96 × écart-type / racine(n), au moins 30 jeux), intégré à l'outil comme 6e statistique.
- Le modèle choisit de lui-même la statistique `intervalle_confiance` quand la question porte sur un intervalle.
- L'arbitre autorise les bornes et le niveau 95, car ce sont des valeurs renvoyées par l'outil.
- Résultat réel : moyenne des ventes Sports 0,568 million, intervalle [0,482 ; 0,654] sur 2304 jeux.

**Fichiers** : `stats.py`, `outil.py`, `arbitre.py`, `tests/test_outil.py`, `tests/test_arbitre.py`, `traces/trace_2026-11-03_15-09-45.json`.

**Commandes pour reproduire** :
```
.venv\Scripts\python -m pytest -q
.venv\Scripts\python agent.py "Quel est l'intervalle de confiance à 95 % de la moyenne des ventes mondiales des jeux de genre Sports ?"
```

**Résultat attendu** : 35 tests passés ; appel de `calculer("intervalle_confiance", "Global_Sales", "Genre", "Sports")`, bornes 0.482 et 0.654 reprises dans la réponse finale, avec `"arbitre": {"autorisee": true, ...}` dans la trace.

**Ce que ces données ne permettent pas de conclure** :
1. L'intervalle suppose un échantillon tiré au hasard ; or le fichier ne contient que les jeux recensés par VGChartz (avec un seuil annoncé de 100 000 exemplaires qui n'est pas respecté). Il mesure la variabilité statistique, pas les biais de collecte, et ne dit rien des jeux absents du fichier.
2. La moyenne n'est pas le jeu typique : les ventes sont très inégales. Le jeu Sports le plus vendu, Wii Sports (Wii, 2006), atteint 82,74 millions, alors que la médiane des jeux Sports n'est que de 0,22 million : la moitié des jeux vendent moins de 0,22 million, bien en dessous de la moyenne de 0,568 tirée vers le haut par quelques gros succès.
3. Ces chiffres décrivent une association, pas une cause : ils ne montrent pas que le genre Sports fait vendre davantage.

## Brique 9 — Comparaison mesurée

**Ce que je montre** : sur 10 questions à réponse connue, le modèle seul se trompe à chaque fois et mon système (outil + arbitre) répond juste à chaque fois.
- Chaque question porte sur une seule statistique (moyenne, médiane, somme, nombre, écart-type) avec au plus un filtre (Genre, Platform, Publisher, Year). Les cinq colonnes de ventes sont utilisées.
- La vérité est calculée indépendamment dans `benchmark.py` : le CSV propre est relu avec `csv` et le module `statistics`, sans `outil.py` ni `stats.py`.
- Les deux modes ont fait 3 essais chacun, avec le même modèle Qwen3.5-4B local (Ollama, température 0.2, 512 jetons de réponse au plus).
- Une réponse est juste si elle contient un nombre à moins de 1 % de la vérité. Pour un nombre de jeux, il faut la valeur exacte.

| Mode | Essai 1 | Essai 2 | Essai 3 | Moyenne ± écart-type | Réponses bloquées |
|---|---|---|---|---|---|
| Modèle seul | 0 % | 0 % | 0 % | 0 % ± 0 | — (pas d'arbitre) |
| Système (outil + arbitre) | 100 % | 100 % | 100 % | 100 % ± 0 | 0 sur 30 |

Les 30 réponses du modèle seul se répartissent ainsi :
- 27 donnent un chiffre inventé, présenté comme le résultat d'un calcul sur le fichier.
- 3 sont coupées par la limite de 512 jetons avant leur conclusion, après avoir cité des chiffres eux aussi inventés.
- Aucune ne dit ne pas avoir accès aux données.

**Fichiers** : `benchmark.py`, `tests/test_benchmark.py`, `resultats/benchmark.json` (les 60 réponses avec leur trace complète), `resultats/benchmark_resume.md`.

**Commandes pour reproduire** :
```
.venv\Scripts\python -m pytest -q
.venv\Scripts\python benchmark.py --rapide
.venv\Scripts\python benchmark.py
```
Le benchmark complet a duré près de 2 heures sur mon PC, car les réponses ralentissent au fil des essais. `--rapide` (2 questions, 1 essai) sert à vérifier que tout marche avant de lancer le benchmark complet.

**Résultat attendu** :
- Tests : 53 passés, dont 18 pour le benchmark.
- Benchmark : le système obtient 30 réponses justes sur 30 et aucune bloquée ; le modèle seul obtient 0 sur 30.
- Le texte des réponses peut varier d'une exécution à l'autre.

**Un échec expliqué** (question 1, essai 2, dans `resultats/benchmark.json`) :
- Question : moyenne des ventes mondiales, en millions d'exemplaires, des jeux du genre Racing. Vérité : 0,5928 million, sur 1226 jeux.
- Ce que le modèle seul répond : « Le nombre total de jeux classés dans ce genre dans le jeu de données complet est de **20**. » puis « La moyenne des ventes mondiales pour les jeux du genre Racing est d'environ **6,925 millions** d'exemplaires. »
- Pourquoi c'est faux : la division 138,5 / 20 = 6,925 est juste, mais ses deux entrées sont inventées. Il n'y a pas 20 jeux Racing mais 1226, et la colonne `World_Sales` qu'il cite n'existe pas. Le modèle n'a jamais vu le fichier : il imagine quelques grands titres (Gran Turismo, Forza…), si bien que sa moyenne est 12 fois trop grande. Le ton reste assuré (« jeu de données complet »), rien ne signale au lecteur que les chiffres sont inventés.
- Ce que le système fait sur la même question :
  - le modèle appelle `calculer("moyenne", "Global_Sales", "Genre", "Racing")` ;
  - l'outil renvoie `{"resultat": 0.593, "n": 1226}` ;
  - le modèle répond « La moyenne des ventes mondiales des jeux du genre Racing est de 0,593 millions d'exemplaires pour 1226 jeux. » ;
  - l'arbitre autorise la réponse (`"autorisee": true`, aucun nombre non justifié), car 0,593 et 1226 viennent de l'outil.

**Limites de ce benchmark** :
1. Les questions ont été choisies dans le périmètre de l'outil (une statistique, au plus un filtre). Le benchmark mesure la fiabilité sur ce type de questions, pas sur des questions hors périmètre (classement, comparaison de deux groupes, plusieurs filtres).
2. Le modèle seul n'a pas accès au fichier. La comparaison montre donc l'apport de l'outil, pas une faiblesse de raisonnement du modèle : on ne peut pas calculer une médiane sur des données qu'on n'a pas.
3. L'arbitre n'a eu à bloquer aucune réponse ici. Ce benchmark ne mesure donc pas son efficacité, qui est démontrée par le test de triche de la brique 3 (`test_triche_bloquee`).
4. 30 sur 30 ne prouve pas que le système ne se trompe jamais. Ce sont 3 essais des mêmes 10 questions, pas 30 cas indépendants. À température 0.2, les essais se ressemblent beaucoup : l'écart-type nul reflète cette répétition plus qu'une garantie.
5. La règle de correction est souple : une réponse est jugée juste si au moins un de ses nombres correspond à la vérité. Une réponse qui cite plusieurs chiffres au hasard pourrait tomber juste par chance. Ici cela n'a avantagé aucun des deux modes : le modèle seul n'a jamais touché la bonne valeur, et le système ne cite que le résultat de l'outil et le nombre de jeux.
6. La limite de 512 jetons a coupé 3 réponses du modèle seul sur 30 avant leur conclusion (Q1 essai 1, Q2 essais 2 et 3), après des chiffres déjà inventés. Même si ces 3 réponses avaient abouti au bon chiffre, le modèle seul serait au plus à 10 %, contre 100 % pour le système : la conclusion ne change pas.
