# Analyste vgsales avec arbitre

Un petit modèle de langage local répond à des questions sur les ventes de jeux vidéo en appelant mon outil de calcul en Python.
Un arbitre, lui aussi écrit en Python, bloque toute réponse qui contient un nombre que l'outil n'a pas calculé.

**Auteur** : Ghali Al Mouzani (GhaliAl05 sur GitHub). Cours Coding for AI & Data Science, aivancity, PGE3, 2026-2027.

## Résultat principal

Le benchmark compte 10 questions à réponse connue, posées 3 fois chacune :
- le système (modèle + outil + arbitre) répond juste **30 fois sur 30** ;
- le modèle seul répond juste **0 fois sur 30**.

Le détail, un échec expliqué et les limites sont dans [EVIDENCE.md](EVIDENCE.md), section Brique 9.

## Le modèle

- **Modèle** : Qwen3.5-4B quantifié Q4_K_M (`qwen3.5:4b-q4_K_M`), en local via Ollama (`http://127.0.0.1:11434`).
- **Réglages** : `num_ctx = 8192`, réflexion désactivée, `num_predict = 512`.
- **Matériel de test** : PC Windows, 8 Go de RAM, sans carte graphique dédiée.
- **Durées mesurées** : environ 1 à 2 minutes par réponse. Le benchmark complet a pris près de 2 heures.

## Installation et lancement

Ces commandes sont à taper dans PowerShell, à la racine du dépôt cloné.

1. Installer Ollama depuis https://ollama.com, puis vérifier qu'il tourne (`ollama serve` s'il n'est pas lancé).
2. Télécharger le modèle :
   ```
   ollama pull qwen3.5:4b-q4_K_M
   ```
3. Créer l'environnement Python :
   ```
   python -m venv .venv
   ```
4. Installer la seule dépendance, pytest :
   ```
   .venv\Scripts\python -m pip install -r requirements.txt
   ```
5. Nettoyer les données. Le script lit `donnees/vgsales_brut.csv` et réécrit `donnees/vgsales_propre.csv` et `donnees/journal_nettoyage.md` :
   ```
   .venv\Scripts\python nettoyer.py
   ```
6. Lancer les tests (Ollama n'est pas nécessaire) :
   ```
   .venv\Scripts\python -m pytest -q
   ```
7. Poser une question, avec le système (outil + arbitre) puis au modèle seul :
   ```
   .venv\Scripts\python agent.py "Quelle est la moyenne des ventes mondiales des jeux de genre Sports ?"
   .venv\Scripts\python agent.py "Quelle est la moyenne des ventes mondiales des jeux de genre Sports ?" --sans-outil
   ```
   Chaque appel enregistre sa trace dans `traces/`.
8. Vérifier le benchmark en version courte (2 questions, 1 essai), puis lancer le benchmark complet (10 questions, 3 essais, près de 2 heures) :
   ```
   .venv\Scripts\python benchmark.py --rapide
   .venv\Scripts\python benchmark.py
   ```
   Les résultats sont écrits dans `resultats/benchmark.json`, mis à jour après chaque réponse, et `resultats/benchmark_resume.md`. L'option `--essais N` change le nombre d'essais.

## Structure du dépôt

| Fichier | Rôle |
|---|---|
| `nettoyer.py` | Nettoie les données brutes selon 6 règles écrites et produit un journal |
| `stats.py` | Fonctions de statistiques simples : moyenne, médiane, écart-type, intervalle de confiance à 95 % |
| `outil.py` | L'outil `calculer` appelé par le modèle : une statistique sur une colonne de ventes, avec un filtre facultatif |
| `arbitre.py` | L'arbitre : bloque toute réponse contenant un nombre non calculé par l'outil (tolérance 1 %) |
| `agent.py` | Dialogue avec Ollama, exécute les appels d'outil, passe la réponse à l'arbitre, enregistre la trace |
| `benchmark.py` | Compare le modèle seul et le système sur 10 questions à réponse connue |
| `tests/` | Tests pytest (nettoyage, outil, arbitre, benchmark), sans appel au modèle |
| `donnees/` | Données brutes, données propres et journal de nettoyage |
| `traces/` | Traces JSON de vrais échanges avec le modèle |
| `resultats/` | Résultats du benchmark (JSON complet et résumé Markdown) |
| `ai_log/` | Journal de chaque séance et export des conversations avec Claude Code |
| `EVIDENCE.md` | Les preuves de chaque brique : fichiers, commandes, résultats attendus, limites |
| `CLAUDE.md` | Les règles du projet données à Claude Code |
| `requirements.txt` | La seule dépendance externe : pytest |

## Briques réalisées

- [x] **Brique 1 — Outil** : le modèle appelle ma fonction `calculer()` au lieu de répondre de mémoire.
- [x] **Brique 3 — Règle imposée par le code** : l'arbitre bloque tout nombre non calculé, et un test de triche le prouve.
- [x] **Brique 6 — Données sales** : de vraies données ouvertes nettoyées par 6 règles écrites, avec un journal.
- [x] **Brique 8 — Incertitude** : un intervalle de confiance à 95 % de la moyenne, ajouté à l'outil.
- [x] **Brique 9 — Comparaison mesurée** : benchmark du modèle seul contre le système, avec une vérité calculée indépendamment.

Le détail de chaque brique est dans [EVIDENCE.md](EVIDENCE.md).

## Données

- **Fichier** : `vgsales.csv`, de Gregory Smith, collecté sur vgchartz.com.
- **Source** : publié sur Zenodo (https://zenodo.org/records/5898311), sous licence CC BY 4.0.
- **Unité** : les ventes sont en millions d'exemplaires.

## Sécurité

Le dépôt ne contient aucune clé d'API ni donnée personnelle. Tout tourne en local : le modèle comme les calculs.
