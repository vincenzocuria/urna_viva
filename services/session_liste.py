from services.liste_candidati import capolista_of, group_by_lista


def sync_voti_candidati(target: dict, candidati: list) -> None:
    old = target.get("voti", {})
    target["voti"] = {c["id"]: int(old.get(c["id"], 0) or 0) for c in candidati}


def migrate_session_to_liste(session: dict, candidati: list) -> None:
    session["meta"]["tipo"] = "liste"
    session["candidati"] = candidati
    for sec in session.get("sezioni", []):
        sync_voti_candidati(sec, candidati)
    sync_voti_candidati(session.get("cumulativo", {}), candidati)


def capolista_per_lista(candidati: list) -> list[dict]:
    rows = []
    for g in group_by_lista(candidati):
        cap = capolista_of(g["candidati"])
        if cap:
            rows.append(
                {
                    "lista": g["nome"],
                    "capolista_id": cap["id"],
                    "capolista_nome": cap["nome"],
                }
            )
    return rows
