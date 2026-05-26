def _section_vv_somma(section: dict, candidati_ids: list) -> tuple[int, int]:
    scr = int(section.get("schede_scrutinate", 0))
    if scr <= 0:
        return 0, 0
    altri = (
        int(section.get("nulli", 0))
        + int(section.get("contestati", 0))
        + int(section.get("bianche", 0))
    )
    vv = int(section.get("voti_validi", 0))
    if vv <= 0:
        vv = max(0, scr - altri)
    somma = sum(int(section.get("voti", {}).get(cid, 0)) for cid in candidati_ids)
    return vv, somma


def _pct(somma: int, voti_validi: int) -> float:
    if voti_validi <= 0:
        return 0.0
    return round(min(100.0, 100.0 * somma / voti_validi), 1)


def section_spoglio_progress(section: dict, candidati_ids: list) -> dict:
    vv, somma = _section_vv_somma(section, candidati_ids)
    return {
        "pct": _pct(somma, vv),
        "somma": somma,
        "voti_validi": vv,
        "mancano": max(0, vv - somma),
    }


def compute_spoglio_progress(session: dict) -> dict:
    candidati_ids = [c["id"] for c in session["candidati"]]
    modalita = session.get("modalita_inserimento", "sezione")

    if modalita == "cumulativo":
        info = section_spoglio_progress(session["cumulativo"], candidati_ids)
        return {"totale": info, "sezioni": {}}

    sezioni = {
        sec["id"]: section_spoglio_progress(sec, candidati_ids)
        for sec in session["sezioni"]
    }
    tot_vv = sum(s["voti_validi"] for s in sezioni.values())
    tot_somma = sum(s["somma"] for s in sezioni.values())
    return {
        "totale": {
            "pct": _pct(tot_somma, tot_vv),
            "somma": tot_somma,
            "voti_validi": tot_vv,
            "mancano": max(0, tot_vv - tot_somma),
        },
        "sezioni": sezioni,
    }
