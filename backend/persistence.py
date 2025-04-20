# =============================================================
# file: persistence.py
# =============================================================
from pathlib import Path
import json
from typing import Dict

from models import Project

DATA_PATH = Path("/data/projects.json")


def _ensure_file():
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not DATA_PATH.exists():
        DATA_PATH.write_text("[]", encoding="utf-8")


def load_projects() -> Dict[str, Project]:
    _ensure_file()
    with DATA_PATH.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    projects = {proj["id"]: Project.parse_obj(proj) for proj in raw}
    return projects


def save_projects(projects: Dict[str, Project]):
    _ensure_file()
    serializable = [proj.dict(by_alias=True) for proj in projects.values()]
    with DATA_PATH.open("w", encoding="utf-8") as f:
        json.dump(serializable, f, ensure_ascii=False, indent=2, default=str)
