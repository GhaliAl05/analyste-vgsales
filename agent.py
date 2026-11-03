# Agent : dialogue avec le modèle local via Ollama et orchestre les appels à l'outil et à l'arbitre.

import json
import os
import sys
import time
import urllib.error
import urllib.request

from outil import DESCRIPTION_OUTIL, calculer

# Réglages faciles à modifier.
OLLAMA_URL = "http://127.0.0.1:11434"
MODELE = "qwen3.5:4b-q4_K_M"
NUM_CTX = 8192
TOURS_MAX = 5
REFLEXION = False
TEMPERATURE = 0.2

# Le dossier des traces part du dossier de ce fichier.
DOSSIER_TRACES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "traces")

CONSIGNE = (
    "Tu réponds à des questions sur les ventes mondiales de jeux vidéo "
    "(fichier vgsales, ventes en millions d'exemplaires, années 1980 à 2016). "
    "Tu dois TOUJOURS utiliser l'outil calculer, jamais répondre de mémoire. "
    "Quand tu as le résultat, réponds en une phrase en reprenant le nombre exact "
    "renvoyé par l'outil et le nombre de jeux utilisés."
)


def appeler_modele(messages, avec_outil):
    """Envoie les messages à l'API /api/chat d'Ollama et renvoie sa réponse JSON complète."""
    requete = {
        "model": MODELE,
        "messages": messages,
        "stream": False,
        "think": REFLEXION,
        "options": {"num_ctx": NUM_CTX, "temperature": TEMPERATURE},
    }
    if avec_outil:
        requete["tools"] = [DESCRIPTION_OUTIL]

    donnees = json.dumps(requete).encode("utf-8")
    demande = urllib.request.Request(
        OLLAMA_URL + "/api/chat",
        data=donnees,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(demande, timeout=300) as reponse:
            return json.loads(reponse.read().decode("utf-8"))
    except urllib.error.HTTPError as erreur:
        detail = erreur.read().decode("utf-8")
        raise RuntimeError("Ollama a renvoyé une erreur " + str(erreur.code) + " : " + detail)
    except urllib.error.URLError:
        raise RuntimeError("Impossible de joindre Ollama à " + OLLAMA_URL
                           + ". Lance Ollama (ollama serve) puis réessaie.")


def executer_appel(appel):
    """Exécute un appel d'outil demandé par le modèle et renvoie le résultat de calculer."""
    fonction = appel.get("function", {})
    if fonction.get("name") != "calculer":
        return {"erreur": "Outil inconnu : " + str(fonction.get("name")) + ". Seul l'outil calculer existe."}
    arguments = fonction.get("arguments")
    if not isinstance(arguments, dict):
        return {"erreur": "Les arguments de calculer doivent être un objet JSON."}
    return calculer(
        arguments.get("statistique"),
        arguments.get("colonne"),
        arguments.get("filtre_colonne"),
        arguments.get("filtre_valeur"),
    )


def noter_appel_modele(etapes, reponse):
    """Ajoute aux étapes le nombre de jetons lus (prompt) et produits (réponse) par le modèle."""
    etapes.append({
        "type": "modele",
        "prompt_eval_count": reponse.get("prompt_eval_count"),
        "eval_count": reponse.get("eval_count"),
    })


def repondre(question, avec_outil=True):
    """Pose la question au modèle (avec ou sans l'outil) et renvoie la trace complète de l'échange."""
    debut = time.perf_counter()
    etapes = []
    tours = 0
    reponse_finale = "Pas de réponse finale après " + str(TOURS_MAX) + " tours."

    if avec_outil:
        messages = [
            {"role": "system", "content": CONSIGNE},
            {"role": "user", "content": question},
        ]
        while tours < TOURS_MAX:
            tours = tours + 1
            reponse = appeler_modele(messages, True)
            noter_appel_modele(etapes, reponse)
            message = reponse["message"]
            messages.append(message)
            appels = message.get("tool_calls")
            if not appels:
                reponse_finale = message.get("content", "")
                break
            for appel in appels:
                resultat = executer_appel(appel)
                arguments = appel.get("function", {}).get("arguments")
                print("Appel de l'outil :", json.dumps(arguments, ensure_ascii=False))
                print("Résultat :", json.dumps(resultat, ensure_ascii=False))
                etapes.append({"type": "outil", "arguments": arguments, "resultat": resultat})
                messages.append({
                    "role": "tool",
                    "tool_name": "calculer",
                    "content": json.dumps(resultat, ensure_ascii=False),
                })
    else:
        messages = [{"role": "user", "content": question}]
        tours = 1
        reponse = appeler_modele(messages, False)
        noter_appel_modele(etapes, reponse)
        reponse_finale = reponse["message"].get("content", "")

    return {
        "question": question,
        "avec_outil": avec_outil,
        "etapes": etapes,
        "reponse_finale": reponse_finale,
        "tours": tours,
        "duree_secondes": round(time.perf_counter() - debut, 2),
    }


def enregistrer_trace(trace):
    """Écrit la trace en JSON lisible dans traces/, avec la date et l'heure dans le nom, et renvoie le chemin."""
    nom = "trace_" + time.strftime("%Y-%m-%d_%H-%M-%S") + ".json"
    chemin = os.path.join(DOSSIER_TRACES, nom)
    with open(chemin, "w", encoding="utf-8") as fichier:
        json.dump(trace, fichier, indent=2, ensure_ascii=False)
    return chemin


def main():
    """Lit la question sur la ligne de commande, interroge le modèle et affiche la réponse."""
    sys.stdout.reconfigure(encoding="utf-8")
    arguments = sys.argv[1:]
    avec_outil = True
    if "--sans-outil" in arguments:
        avec_outil = False
        arguments.remove("--sans-outil")
    if len(arguments) == 0:
        print('Utilisation : python agent.py "ma question" [--sans-outil]')
        return

    question = " ".join(arguments)
    try:
        trace = repondre(question, avec_outil)
    except RuntimeError as erreur:
        print("Erreur :", erreur)
        return

    print("Réponse finale :", trace["reponse_finale"])
    print("Trace enregistrée :", enregistrer_trace(trace))


if __name__ == "__main__":
    main()
