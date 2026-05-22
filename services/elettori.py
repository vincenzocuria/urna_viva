def totale_elettori(session: dict) -> int:
    return sum(int(s.get("elettori", 0)) for s in session.get("sezioni", []))


def sync_elettori_totale(session: dict) -> int:
    tot = totale_elettori(session)
    session.setdefault("meta", {})["elettori_totale"] = tot
    return tot
