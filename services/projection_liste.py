from services.liste_candidati import (
    capolista_of,
    group_by_lista,
    somma_preferenze_lista,
    totale_lista,
)
from services.projection_zona import (
    ZONA_DEFAULT,
    medie_quote_per_zona,
    medie_tassi_schede,
    quote_per_sezione,
    tassi_per_sezione,
)


def _zona_key(sec: dict) -> str:
    z = (sec.get("zona") or "").strip()
    return z if z else ZONA_DEFAULT


def capolista_ids(candidati: list) -> list[str]:
    out = []
    for g in group_by_lista(candidati):
        cap = capolista_of(g["candidati"])
        if cap:
            out.append(cap["id"])
    return out


def _capolista_candidati_map(candidati: list) -> dict[str, list]:
    out = {}
    for g in group_by_lista(candidati):
        cap = capolista_of(g["candidati"])
        if cap:
            out[cap["id"]] = g["candidati"]
    return out


def medie_quote_lista_per_zona(
    sezioni_con_dati: list, cap_map: dict[str, list]
) -> tuple[dict, dict]:
    per_zona: dict[str, dict[str, list[float]]] = {}
    globale: dict[str, list[float]] = {cid: [] for cid in cap_map}
    for sec in sezioni_con_dati:
        vv = int(sec.get("voti_validi", 0) or 0)
        if vv <= 0:
            continue
        zk = _zona_key(sec)
        per_zona.setdefault(zk, {cid: [] for cid in cap_map})
        voti = sec.get("voti", {})
        for cid, cands in cap_map.items():
            q = totale_lista(voti, cands) / vv
            per_zona[zk][cid].append(q)
            globale[cid].append(q)
    media_zona = {
        z: {cid: (sum(v) / len(v) if v else 0.0) for cid, v in data.items()}
        for z, data in per_zona.items()
    }
    media_globale = {
        cid: (sum(v) / len(v) if v else 0.0) for cid, v in globale.items()
    }
    return media_zona, media_globale


def quote_lista_sezione(
    sec: dict,
    cap_map: dict[str, list],
    media_zona: dict,
    media_globale: dict,
) -> dict[str, float]:
    vv = int(sec.get("voti_validi", 0) or 0)
    voti = sec.get("voti", {})
    if vv > 0:
        return {
            cid: totale_lista(voti, cands) / vv for cid, cands in cap_map.items()
        }
    ref = media_zona.get(_zona_key(sec)) or media_globale
    return {cid: ref.get(cid, 0.0) for cid in cap_map}


def project_weighted_liste(session: dict, agg: dict) -> dict:
    """Proiezione liste: sindaco = totale preferenze lista; consiglieri per preferenza."""
    candidati = session["candidati"]
    candidati_ids = [c["id"] for c in candidati]
    cap_map = _capolista_candidati_map(candidati)
    cap_ids = list(cap_map.keys())
    cap_set = set(cap_ids)
    tot = agg["tot"]
    voti_reali = agg["voti_reali"]
    voti_proiettati = {cid: 0.0 for cid in candidati_ids}
    elettori_totali = tot["elettori"] or 1
    sezioni_con_dati = [
        s for s in session["sezioni"] if s.get("schede_scrutinate", 0) > 0
    ]
    media_q_zona, media_q_glob = medie_quote_per_zona(
        sezioni_con_dati, candidati_ids
    )
    media_ql_zona, media_ql_glob = medie_quote_lista_per_zona(
        sezioni_con_dati, cap_map
    )
    media_t_zona, media_t_glob = medie_tassi_schede(sezioni_con_dati)

    for sec in session["sezioni"]:
        elettori = sec["elettori"]
        tassi = tassi_per_sezione(sec, media_t_zona, media_t_glob)
        validi_proj = tassi["validi"] * elettori
        quote_all = quote_per_sezione(sec, candidati_ids, media_q_zona, media_q_glob)
        quote_lista = quote_lista_sezione(sec, cap_map, media_ql_zona, media_ql_glob)
        for cid in candidati_ids:
            q = quote_lista[cid] if cid in cap_set else quote_all[cid]
            voti_proiettati[cid] += q * validi_proj

    from services.projection import _proietta_schede_altri

    altri = _proietta_schede_altri(session, media_t_zona, media_t_glob)
    voti_validi_proiettati = sum(voti_proiettati[cid] for cid in cap_ids) or 1.0
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
