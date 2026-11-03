# Règles du projet (valables pour toutes les sessions)

## Dépendances
- Python bibliothèque standard uniquement (csv, json, urllib, statistics, re, math, os, sys, time). Pas de pandas.
- Seule dépendance externe autorisée : pytest.

## Style de code
- Le code doit être le plus simple possible : je dois pouvoir expliquer chaque ligne à l'oral.
- Pas de classes, pas de décorateurs, pas de compréhensions imbriquées, pas d'astuces.
- Des fonctions courtes, chacune avec une docstring en français.
- Commentaires et noms de variables en français.

## Modèle
- Le modèle est appelé via Ollama à l'adresse http://127.0.0.1:11434.
- Modèle : qwen3.5:4b-q4_K_M, avec num_ctx = 8192.

## Sécurité
- Ne jamais écrire de clé d'API, de mot de passe ou de donnée personnelle dans un fichier du dépôt.

## Méthode de travail
- Avant de modifier plusieurs fichiers, explique-moi ton plan et attends mon accord.
- Après chaque fonction écrite, explique-la-moi en quelques phrases simples.
