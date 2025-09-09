import json
import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import requests

# Icônes par catégorie
CATEGORY_ICONS = {
    "MOVIE": "🎬",
    "GAME": "🎮",
    "MUSIC": "🎵",
    "OTHER": "📌"
}

CATEGORY_COLORS = {
    "MOVIE": "#f39c12",  # orange
    "GAME": "#27ae60",   # vert
    "MUSIC": "#9235ba",  # violet
    "OTHER": "#3498db"   # bleu
}


def load_events(api_ids=None):
    """
    Charge les événements depuis l’API si api_ids est fourni,
    sinon depuis data/events.json en local.
    """
    if api_ids:
        events = []
        for eid in api_ids:
            try:
                resp = requests.get(f"https://api.restful-api.dev/objects/{eid}", timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    if "data" in data:
                        events.append(data["data"])
            except Exception as e:
                print(f"⚠️ Erreur API pour ID {eid}: {e}")
        return events

    # Fallback → fichier local
    with open("data/events.json", "r", encoding="utf-8") as f:
        return json.load(f)




def group_by_category(events):
    """Regroupe les événements par catégorie"""
    grouped = {}
    for event in events:
        cat = event["category"].upper()
        grouped.setdefault(cat, []).append(event)
    return grouped


def filter_today(events):
    """Retourne les événements de la date du jour"""
    today_str = datetime.today().strftime("%Y-%m-%d")
    return [e for e in events if e["datetime"].startswith(today_str)]


def generate_html(events):
    """Génère un fichier HTML avec Jinja2"""
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("schedule.html")

    grouped = group_by_category(events)

    output = template.render(events_grouped=grouped, icons=CATEGORY_ICONS, category_colors=CATEGORY_COLORS)
    os.makedirs("output", exist_ok=True)
    with open("output/schedule.html", "w", encoding="utf-8") as f:
        f.write(output)


def generate_markdown(events):
    """Génère un résumé en Markdown"""
    grouped = group_by_category(events)
    today_events = filter_today(events)

    lines = ["# Weekly Entertainment Summary\n"]
    for cat, evts in grouped.items():
        lines.append(f"- {CATEGORY_ICONS.get(cat, '')} {cat}: {len(evts)} events")

    lines.append("\n## Today's Events\n")
    if today_events:
        for e in today_events:
            lines.append(f"- {e['name']} at {e.get('location', 'TBA')} ({e['datetime']})")
    else:
        lines.append("No events today.")

    os.makedirs("output", exist_ok=True)
    with open("output/summary.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    ids_file = "data/event_ids.json"
    api_ids = None

    # Vérification du fichier d’IDs
    if os.path.exists(ids_file):
        try:
            with open(ids_file, "r", encoding="utf-8") as f:
                api_ids = json.load(f)
            if not api_ids:  # fichier vide
                print("⚠️ event_ids.json est vide → utilisation du fichier local events.json")
                api_ids = None
        except Exception as e:
            print(f"⚠️ Impossible de lire {ids_file} ({e}) → fallback local")
            api_ids = None
    else:
        print("⚠️ Aucun fichier event_ids.json trouvé → utilisation de events.json")

    # Charger les événements
    events = load_events(api_ids=api_ids)

    # Générer les sorties
    generate_html(events)
    generate_markdown(events)

    print(" Résultats générés dans le dossier /output/")
if __name__ == "__main__":
    main()
