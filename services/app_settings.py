import json
import os

from config import DEFAULT_ELETTORI_SEZIONE, SETTINGS_PATH

DEFAULTS = {
    "elettori_sezione_default": DEFAULT_ELETTORI_SEZIONE,
}


def load_settings() -> dict:
    if not os.path.isfile(SETTINGS_PATH):
        return dict(DEFAULTS)
    with open(SETTINGS_PATH, encoding="utf-8") as f:
        data = json.load(f)
    out = dict(DEFAULTS)
    out.update(data)
    return out


def save_settings(data: dict) -> dict:
    current = load_settings()
    if "elettori_sezione_default" in data:
        val = int(data["elettori_sezione_default"])
        current["elettori_sezione_default"] = max(1, val)
    os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(current, f, ensure_ascii=False, indent=2)
    return current


def elettori_sezione_default() -> int:
    return int(load_settings().get("elettori_sezione_default", DEFAULT_ELETTORI_SEZIONE))
