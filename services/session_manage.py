import os

from config import DATA_DIR
from services.logo_service import remove_logo
from services.session_store import _path, load, save


def delete_session(session_id: str) -> bool:
    path = _path(session_id)
    if not os.path.isfile(path):
        return False
    os.remove(path)
    remove_logo(session_id)
    return True


def update_meta(session: dict, comune: str, abitanti: str | None) -> None:
    session.setdefault("meta", {})["comune"] = comune.strip()
    if abitanti and str(abitanti).isdigit():
        session["meta"]["abitanti"] = int(abitanti)
    else:
        session["meta"]["abitanti"] = None


def update_sezioni_config(session: dict, sezioni_input: list) -> None:
    old_by_id = {s["id"]: s for s in session.get("sezioni", [])}
    candidati_ids = [c["id"] for c in session["candidati"]]
    nuove = []
    for i, s in enumerate(sezioni_input):
        sid = s.get("id") or str(i + 1)
        old = old_by_id.get(sid, {})
        nuove.append(
            {
                "id": sid,
                "nome": s.get("nome") or f"Sezione {i + 1}",
                "zona": (s.get("zona") or "").strip(),
                "elettori": max(1, int(s.get("elettori", 100))),
                "schede_scrutinate": old.get("schede_scrutinate", 0),
                "voti_validi": old.get("voti_validi", 0),
                "nulli": old.get("nulli", 0),
                "contestati": old.get("contestati", 0),
                "bianche": old.get("bianche", 0),
                "voti": old.get("voti") or {cid: 0 for cid in candidati_ids},
            }
        )
    session["sezioni"] = nuove


def delete_storico_entry(session: dict, index: int) -> bool:
    storico = session.get("storico", [])
    if index < 0 or index >= len(storico):
        return False
    storico.pop(index)
    session["storico"] = storico
    return True


def update_storico_nota(session: dict, index: int, nota: str) -> bool:
    storico = session.get("storico", [])
    if index < 0 or index >= len(storico):
        return False
    storico[index]["nota"] = nota.strip()
    return True


def clear_storico(session: dict) -> None:
    session["storico"] = []
