import json
import requests
import os

API_URL = "https://api.restful-api.dev/objects"

def post_events(filepath="data/events.json", output_ids="data/event_ids.json"):
    """Envoie chaque événement vers restful-api.dev et sauvegarde les IDs créés"""
    with open(filepath, "r", encoding="utf-8") as f:
        events = json.load(f)

    created_ids = []

    for e in events:
        payload = {"data": e}
        print(f"📤 Envoi de l'événement: {e['name']}")
        response = requests.post(API_URL, json=payload)

        if response.status_code in (200, 201):
            result = response.json()
            created_ids.append(result["id"])
            print(f" Créé avec ID: {result['id']}")
        else:
            print(f" Erreur pour {e['name']} ({response.status_code}): {response.text}")

    # Sauvegarde des IDs dans un fichier
    os.makedirs(os.path.dirname(output_ids), exist_ok=True)
    with open(output_ids, "w", encoding="utf-8") as f:
        json.dump(created_ids, f, indent=2)

    print("\n Tous les événements traités")
    print(f" {len(created_ids)} IDs sauvegardés dans {output_ids}")

if __name__ == "__main__":
    post_events()
