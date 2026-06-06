import json
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
KB_DIR = BASE_DIR / "knowledge_base"
def load_json(filename):
    path = KB_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Knowledge base file not found: {path}")
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)
def load_knowledge_base():
    return {
        "tests": load_json("tests.json"),
        "conditions": load_json("conditions.json"),
        "rules": load_json("rules.json"),
        "red_flags": load_json("red_flags.json"),
        "severity_levels": load_json("severity_levels.json"),
        "units": load_json("units.json")
    }
