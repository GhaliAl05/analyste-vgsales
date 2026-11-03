# Séance 2 — 3 novembre 2026 (après-midi)

Outils : Claude Code ; Claude (claude.ai) pour relire les plans.

- Brique 1, outil calculer : plan accepté avec un ajout de ma part : comparer le filtre en texte minuscule (str().lower()), parce que le modèle peut envoyer 2006 au lieu de "2006" ou "sports" au lieu de "Sports".
- Brique 1, agent.py : premier essai réel réussi (0,568 sur 2304 jeux, 72 s). Sans outil, le modèle répond hors sujet (chiffre d'affaires en dollars).
- Brique 3, arbitre : j'ai repris extraire() du comparer.py du cours. Mes tests ont montré qu'elle lit « 0,568 » comme 568 ; Claude Code a trouvé la cause (la virgule prise pour un séparateur de milliers anglais) et proposé de retirer la virgule du premier crochet ; j'ai validé cette correction, appliquée par Claude Code, avec un test qui documente le cas anglais.
- L'outil d'édition de Claude Code transformait \u00a0 en caractère invisible : j'ai exigé une écriture visible, plus facile à expliquer à l'oral.
