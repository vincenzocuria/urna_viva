import json
import os
import uuid
from datetime import datetime

from config import DATA_DIR


def _path(session_id: str) -> str:
    return os.path.join(DATA_DIR, f"{session_id}.json")


def new_session(
    comune: str,
    tipo: str,
    candidati: list,
    sezioni: list,
    abitanti: int | None = None,
) -> dict:
    session_id = str(uuid.uuid4())[:8]
    now = datetime.now().isoformat(timespec="seconds")
    candidati_norm = [
        {
            "id": c.get("id") or str(i + 1),
            "nome": c["nome"].strip(),
            "lista": c.get("lista", "").strip(),
        }
        for i, c in enumerate(candidati)
    ]
    sezioni_norm = [
        {
            "id": s.get("id") or str(i + 1),
            "nome": s.get("nome") or f"Sezione {i + 1}",
            "zona": (s.get("zona") or "").strip(),
            "elettori": int(s["elettori"]),
            "schede_scrutinate": 0,
            "voti_validi": 0,
            "nulli": 0,
            "contestati": 0,
            "bianche": 0,
            "voti": {c["id"]: 0 for c in candidati_norm},
        }
        for i, s in enumerate(sezioni)
    ]
    cumulativo = _empty_totale(candidati_norm)
    elettori_totale = sum(int(s["elettori"]) for s in sezioni_norm)
    return {
        "id": session_id,
        "meta": {
            "comune": comune.strip(),
            "tipo": tipo,
            "abitanti": abitanti,
            "elettori_totale": elettori_totale,
            "creato": now,
            "aggiornato": now,
            "logo": None,
        },
        "candidati": candidati_norm,
        "sezioni": sezioni_norm,
        "cumulativo": cumulativo,
        "modalita_inserimento": "sezione",
        "storico": [],
    }


def _empty_totale(candidati: list) -> dict:
    return {
        "schede_scrutinate": 0,
        "voti_validi": 0,
        "nulli": 0,
        "contestati": 0,
        "bianche": 0,
        "voti": {c["id"]: 0 for c in candidati},
    }


def save(session: dict) -> None:
    from services.elettori import sync_elettori_totale

    sync_elettori_totale(session)
    session["meta"]["aggiornato"] = datetime.now().isoformat(timespec="seconds")
    path = _path(session["id"])
    with open(path, "w", encoding="utf-8") as f:
        json.dump(session, f, ensure_ascii=False, indent=2)


def load(session_id: str) -> dict | None:
    path = _path(session_id)
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def list_sessions() -> list:
    if not os.path.isdir(DATA_DIR):
        return []
    out = []
    for name in os.listdir(DATA_DIR):
        if not name.endswith(".json"):
            continue
        sid = name[:-5]
        s = load(sid)
        if s:
            out.append(
                {
                    "id": sid,
                    "comune": s["meta"]["comune"],
                    "tipo": s["meta"]["tipo"],
                    "aggiornato": s["meta"].get("aggiornato"),
                    "storico_count": len(s.get("storico", [])),
                }
            )
    return sorted(out, key=lambda x: x.get("aggiornato") or "", reverse=True)


def append_storico(session: dict, nota: str = "") -> None:
    from services.projection import compute_projection

    snap = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "nota": nota,
        "proiezione": compute_projection(session),
    }
    session.setdefault("storico", []).append(snap)
