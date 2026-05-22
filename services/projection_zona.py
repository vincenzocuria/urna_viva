ZONA_DEFAULT = "_globale"


def _zona_key(sec: dict) -> str:
    z = (sec.get("zona") or "").strip()
    return z if z else ZONA_DEFAULT


def medie_quote_per_zona(sezioni_con_dati: list, candidati_ids: list) -> tuple:
    per_zona: dict[str, dict[str, list[float]]] = {}
    globale: dict[str, list[float]] = {cid: [] for cid in candidati_ids}
    for sec in sezioni_con_dati:
        vv = sec.get("voti_validi", 0)
        if vv <= 0:
            continue
        zk = _zona_key(sec)
        per_zona.setdefault(zk, {cid: [] for cid in candidati_ids})
        for cid in candidati_ids:
            q = sec.get("voti", {}).get(cid, 0) / vv
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


def medie_tassi_schede(sezioni_con_dati: list) -> tuple:
    per_zona: dict[str, list[dict]] = {}
    globale: list[dict] = []
    for sec in sezioni_con_dati:
        scr = sec.get("schede_scrutinate", 0)
        if scr <= 0:
            continue
        t = {
            "nulli": sec.get("nulli", 0) / scr,
            "bianche": sec.get("bianche", 0) / scr,
            "contestati": sec.get("contestati", 0) / scr,
            "validi": sec.get("voti_validi", 0) / scr,
        }
        zk = _zona_key(sec)
        per_zona.setdefault(zk, []).append(t)
        globale.append(t)
    def _avg(lst: list, key: str) -> float:
        if not lst:
            return 0.0
        return sum(x[key] for x in lst) / len(lst)

    media_zona = {
        z: {
            "nulli": _avg(items, "nulli"),
            "bianche": _avg(items, "bianche"),
            "contestati": _avg(items, "contestati"),
            "validi": _avg(items, "validi"),
        }
        for z, items in per_zona.items()
    }
    media_globale = {
        "nulli": _avg(globale, "nulli"),
        "bianche": _avg(globale, "bianche"),
        "contestati": _avg(globale, "contestati"),
        "validi": _avg(globale, "validi"),
    }
    return media_zona, media_globale


def tassi_per_sezione(sec: dict, media_zona: dict, media_globale: dict) -> dict:
    zk = _zona_key(sec)
    return media_zona.get(zk) or media_globale


def quote_per_sezione(
    sec: dict,
    candidati_ids: list,
    media_zona: dict,
    media_globale: dict,
) -> dict[str, float]:
    vv = sec.get("voti_validi", 0)
    if vv > 0:
        return {cid: sec.get("voti", {}).get(cid, 0) / vv for cid in candidati_ids}
    ref = media_zona.get(_zona_key(sec)) or media_globale
    return {cid: ref.get(cid, 0.0) for cid in candidati_ids}
