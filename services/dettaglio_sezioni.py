from services.projection import compute_projection
from services.projection_zona import (
    medie_quote_per_zona,
    medie_tassi_schede,
    quote_per_sezione,
    tassi_per_sezione,
)


def build_dettaglio(session: dict, metodo: str | None = None) -> dict:
    proiezione = compute_projection(session, metodo)
    candidati = session["candidati"]
    candidati_ids = [c["id"] for c in candidati]
    sezioni_con = [s for s in session["sezioni"] if s.get("schede_scrutinate", 0) > 0]
    media_q_zona, media_q_glob = medie_quote_per_zona(sezioni_con, candidati_ids)
    media_t_zona, media_t_glob = medie_tassi_schede(sezioni_con)

    righe = []
    for sec in session["sezioni"]:
        elett = sec["elettori"]
        scr = sec.get("schede_scrutinate", 0)
        quote = quote_per_sezione(sec, candidati_ids, media_q_zona, media_q_glob)
        tassi = tassi_per_sezione(sec, media_t_zona, media_t_glob)
        if scr > 0:
            t_nulli = sec.get("nulli", 0) / scr
            t_bianche = sec.get("bianche", 0) / scr
            t_cont = sec.get("contestati", 0) / scr
        else:
            t_nulli = tassi["nulli"]
            t_bianche = tassi["bianche"]
            t_cont = tassi["contestati"]
        scr_proj = elett
        voti_proj = {cid: int(round(quote[cid] * tassi["validi"] * elett)) for cid in candidati_ids}
        righe.append(
            {
                "id": sec["id"],
                "nome": sec.get("nome"),
                "zona": sec.get("zona") or "—",
                "elettori": elett,
                "schede_scrutinate": scr,
                "schede_proiettate": scr_proj,
                "avanzamento_pct": round(100 * scr / elett, 1) if elett else 0,
                "voti_validi": sec.get("voti_validi", 0),
                "nulli": sec.get("nulli", 0),
                "nulli_proiettati": round(t_nulli * elett),
                "bianche": sec.get("bianche", 0),
                "bianche_proiettate": round(t_bianche * elett),
                "contestati": sec.get("contestati", 0),
                "contestati_proiettati": round(t_cont * elett),
                "ha_dati": scr > 0,
                "usa_media_zona": scr == 0,
                "voti": {cid: sec.get("voti", {}).get(cid, 0) for cid in candidati_ids},
                "voti_proiettati": voti_proj,
                "quote_pct": {cid: round(quote[cid] * 100, 1) for cid in candidati_ids},
            }
        )
    zone_riepilogo = sorted(
        {r["zona"] for r in righe if r["zona"] != "—"}
    )
    return {
        "proiezione": proiezione,
        "righe": righe,
        "zone": zone_riepilogo,
        "metodo": proiezione.get("metodo_label"),
    }
