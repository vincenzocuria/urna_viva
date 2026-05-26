from calculators import direct_mayor, list_system
from services.projection_zona import (
    medie_quote_per_zona,
    medie_tassi_schede,
    quote_per_sezione,
    tassi_per_sezione,
)


def _aggregate_from_sections(session: dict) -> dict:
    candidati_ids = [c["id"] for c in session["candidati"]]
    voti_reali = {cid: 0 for cid in candidati_ids}
    tot = {
        "schede_scrutinate": 0,
        "voti_validi": 0,
        "nulli": 0,
        "contestati": 0,
        "bianche": 0,
        "elettori": 0,
    }
    for sec in session["sezioni"]:
        tot["elettori"] += sec["elettori"]
        tot["schede_scrutinate"] += sec.get("schede_scrutinate", 0)
        tot["voti_validi"] += sec.get("voti_validi", 0)
        tot["nulli"] += sec.get("nulli", 0)
        tot["contestati"] += sec.get("contestati", 0)
        tot["bianche"] += sec.get("bianche", 0)
        for cid in candidati_ids:
            voti_reali[cid] += sec.get("voti", {}).get(cid, 0)
    return {"tot": tot, "voti_reali": voti_reali}


def _proietta_schede_altri(
    session: dict,
    media_t_zona: dict,
    media_t_glob: dict,
) -> dict:
    nulli_p = contestati_p = bianche_p = schede_p = 0
    for sec in session["sezioni"]:
        elett = sec["elettori"]
        scr = sec.get("schede_scrutinate", 0)
        if scr > 0:
            t = {
                "nulli": sec.get("nulli", 0) / scr,
                "bianche": sec.get("bianche", 0) / scr,
                "contestati": sec.get("contestati", 0) / scr,
            }
            schede_p += elett
        else:
            t = tassi_per_sezione(sec, media_t_zona, media_t_glob)
            schede_p += elett
        nulli_p += round(t["nulli"] * elett)
        bianche_p += round(t["bianche"] * elett)
        contestati_p += round(t["contestati"] * elett)
    return {
        "schede_proiettate": schede_p,
        "nulli_proiettati": nulli_p,
        "bianche_proiettate": bianche_p,
        "contestati_proiettati": contestati_p,
    }


def project_weighted(session: dict) -> dict:
    agg = _aggregate_from_sections(session)
    if session.get("meta", {}).get("tipo") == "liste":
        from services.projection_liste import project_weighted_liste

        return project_weighted_liste(session, agg)
    candidati_ids = [c["id"] for c in session["candidati"]]
    tot = agg["tot"]
    voti_reali = agg["voti_reali"]
    voti_proiettati = {cid: 0.0 for cid in candidati_ids}
    elettori_totali = tot["elettori"] or 1
    sezioni_con_dati = [
        s for s in session["sezioni"] if s.get("schede_scrutinate", 0) > 0
    ]
    media_q_zona, media_q_glob = medie_quote_per_zona(sezioni_con_dati, candidati_ids)
    media_t_zona, media_t_glob = medie_tassi_schede(sezioni_con_dati)

    for sec in session["sezioni"]:
        elettori = sec["elettori"]
        quote = quote_per_sezione(sec, candidati_ids, media_q_zona, media_q_glob)
        tassi = tassi_per_sezione(sec, media_t_zona, media_t_glob)
        validi_proj = tassi["validi"] * elettori
        for cid in candidati_ids:
            voti_proiettati[cid] += quote[cid] * validi_proj

    altri = _proietta_schede_altri(session, media_t_zona, media_t_glob)
    voti_validi_proiettati = sum(voti_proiettati.values()) or 1
    avanzamento = tot["schede_scrutinate"] / elettori_totali if elettori_totali else 0
    return {
        "metodo": "pesata_sezione",
        "metodo_label": "Proiezione pesata per sezione (per zona)",
        "voti_reali": voti_reali,
        "voti_proiettati": voti_proiettati,
        "voti_validi_reali": tot["voti_validi"],
        "voti_validi_proiettati": voti_validi_proiettati,
        "schede_scrutinate": tot["schede_scrutinate"],
        "schede_totali": elettori_totali,
        "avanzamento": round(avanzamento, 4),
        "avanzamento_pct": round(avanzamento * 100, 1),
        "nulli": tot["nulli"],
        "contestati": tot["contestati"],
        "bianche": tot["bianche"],
        **altri,
    }


def project_cumulative(session: dict) -> dict:
    candidati_ids = [c["id"] for c in session["candidati"]]
    cum = session.get("cumulativo", {})
    elettori_totali = sum(s["elettori"] for s in session["sezioni"]) or 1
    scrutinate = cum.get("schede_scrutinate", 0)
    voti_validi_reali = cum.get("voti_validi", 0)
    voti_reali = {cid: cum.get("voti", {}).get(cid, 0) for cid in candidati_ids}
    peso = scrutinate / elettori_totali if elettori_totali and scrutinate else 0
    if peso <= 0:
        voti_proiettati = {cid: 0.0 for cid in candidati_ids}
        voti_validi_proiettati = 0
        altri = {
            "schede_proiettate": 0,
            "nulli_proiettati": 0,
            "bianche_proiettate": 0,
            "contestati_proiettati": 0,
        }
    else:
        voti_proiettati = {cid: voti_reali[cid] / peso for cid in candidati_ids}
        voti_validi_proiettati = sum(voti_proiettati.values())
        altri = {
            "schede_proiettate": elettori_totali,
            "nulli_proiettati": round(cum.get("nulli", 0) / peso),
            "bianche_proiettate": round(cum.get("bianche", 0) / peso),
            "contestati_proiettati": round(cum.get("contestati", 0) / peso),
        }
    avanzamento = scrutinate / elettori_totali if elettori_totali else 0
    return {
        "metodo": "cumulativa",
        "metodo_label": "Proiezione cumulativa (estrapolazione lineare)",
        "voti_reali": voti_reali,
        "voti_proiettati": voti_proiettati,
        "voti_validi_reali": voti_validi_reali,
        "voti_validi_proiettati": voti_validi_proiettati or 1,
        "schede_scrutinate": scrutinate,
        "schede_totali": elettori_totali,
        "avanzamento": round(avanzamento, 4),
        "avanzamento_pct": round(avanzamento * 100, 1),
        "nulli": cum.get("nulli", 0),
        "contestati": cum.get("contestati", 0),
        "bianche": cum.get("bianche", 0),
        **altri,
    }


def compute_projection(session: dict, metodo: str | None = None) -> dict:
    if metodo is None:
        metodo = (
            "cumulativo"
            if session.get("modalita_inserimento") == "cumulativo"
            else "pesata"
        )
    tipo = session["meta"]["tipo"]
    if metodo == "pesata" and session.get("modalita_inserimento") != "cumulativo":
        raw = project_weighted(session)
    else:
        raw = project_cumulative(session)
    calc = list_system if tipo == "liste" else direct_mayor
    return calc.format_result(raw, session)
