import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "user_config.json")

def get_theme():
    if not os.path.exists(CONFIG_PATH):
        return "Clair"
    with open(CONFIG_PATH, "r") as f:
        data = json.load(f)
        return data.get("theme", "Clair")

def set_theme(theme):
    data = {"theme": theme}
    with open(CONFIG_PATH, "w") as f:
        json.dump(data, f)