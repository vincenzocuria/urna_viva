from services.sezione_live_dettaglio import enrich_sezione_live


def stima_schede_votate_finale(session: dict) -> dict:
    sezioni = session.get("sezioni", [])
    elett_tot = sum(int(s.get("elettori", 0)) for s in sezioni)
    arrivate = sum(int(s.get("schede_scrutinate", 0)) for s in sezioni)
    elett_con_arrivo = sum(
        int(s.get("elettori", 0))
        for s in sezioni
        if int(s.get("schede_scrutinate", 0)) > 0
    )
    sezioni_con_arrivo = sum(
        1 for s in sezioni if int(s.get("schede_scrutinate", 0)) > 0
    )
    completo = elett_tot > 0 and elett_con_arrivo >= elett_tot
    if elett_con_arrivo <= 0 or elett_tot <= 0:
        stima = arrivate
    elif completo:
        stima = arrivate
    else:
        stima = round(arrivate * elett_tot / elett_con_arrivo)
    return {
        "arrivate": arrivate,
        "stima_finale": stima,
        "elettori": elett_tot,
        "completo": completo,
        "sezioni_con_arrivo": sezioni_con_arrivo,
        "sezioni_totali": len(sezioni),
    }


def build_sezioni_live(session: dict) -> list:
    return [enrich_sezione_live(sec, session) for sec in session.get("sezioni", [])]
