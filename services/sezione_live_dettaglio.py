from services.liste_candidati import capolista_of, group_by_lista, totale_lista


def _pct(part: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round(100.0 * part / total, 1)


def _leader_liste(candidati: list, voti: dict, vv: int) -> tuple[str | None, float, float]:
    best_nome = None
    best_tot = 0
    for g in group_by_lista(candidati):
        tot = totale_lista(voti, g["candidati"])
        if tot > best_tot:
            cap = capolista_of(g["candidati"])
            cap_nome = cap["nome"] if cap else "?"
            best_nome = f"{g['nome']} — {cap_nome}"
            best_tot = tot
    pct = _pct(best_tot, vv)
    return best_nome, pct, best_tot


def _leader_diretto(candidati_map: dict, voti: dict, vv: int) -> tuple[str | None, float, float]:
    if not voti or vv <= 0:
        return None, 0.0, 0
    leader_id = max(voti.keys(), key=lambda k: int(voti.get(k, 0) or 0))
    leader = candidati_map.get(leader_id)
    leader_voti = int(voti.get(leader_id, 0) or 0)
    nome = leader["nome"] if leader else None
    return nome, _pct(leader_voti, vv), leader_voti


def build_sezione_dettaglio(sec: dict, session: dict) -> dict:
    candidati = session.get("candidati", [])
    voti = sec.get("voti", {}) or {}
    vv = int(sec.get("voti_validi", 0))
    nulli = int(sec.get("nulli", 0))
    bianche = int(sec.get("bianche", 0))
    contestati = int(sec.get("contestati", 0))
    is_liste = session.get("meta", {}).get("tipo") == "liste"
    somma_voti = sum(int(voti.get(c["id"], 0) or 0) for c in candidati)

    base = {
        "nulli": nulli,
        "bianche": bianche,
        "contestati": contestati,
        "voti_validi": vv,
        "spoglio_pct": _pct(somma_voti, vv),
        "mancano": max(0, vv - somma_voti),
    }

    if is_liste:
        liste = []
        for g in group_by_lista(candidati, capolista_first=True):
            cap = capolista_of(g["candidati"])
            cap_id = cap["id"] if cap else None
            tot = totale_lista(voti, g["candidati"])
            cap_voti = int(voti.get(cap_id, 0) or 0) if cap_id else 0
            membri = []
            for c in g["candidati"]:
                is_cap = c["id"] == cap_id
                v = cap_voti if is_cap else int(voti.get(c["id"], 0) or 0)
                membri.append(
                    {
                        "nome": c["nome"],
                        "voti": v,
                        "capolista": is_cap,
                    }
                )
            membri.sort(key=lambda m: (0 if m["capolista"] else 1, -m["voti"]))
            liste.append(
                {
                    "nome": g["nome"],
                    "capolista": cap["nome"] if cap else "",
                    "totale": tot,
                    "pct": _pct(tot, vv),
                    "candidati": membri,
                }
            )
        liste.sort(key=lambda l: l["totale"], reverse=True)
        return {**base, "liste": liste}

    rows = []
    for c in candidati:
        v = int(voti.get(c["id"], 0) or 0)
        rows.append({"nome": c["nome"], "voti": v, "pct": _pct(v, vv)})
    rows.sort(key=lambda r: r["voti"], reverse=True)
    return {**base, "candidati": rows}


def enrich_sezione_live(sec: dict, session: dict) -> dict:
    candidati_list = session.get("candidati", [])
    candidati_map = {c["id"]: c for c in candidati_list}
    voti = sec.get("voti", {}) or {}
    vv = int(sec.get("voti_validi", 0))
    elett = int(sec.get("elettori", 0))
    scrut = int(sec.get("schede_scrutinate", 0))
    is_liste = session.get("meta", {}).get("tipo") == "liste"

    if is_liste:
        leader_nome, pct_leader, _ = _leader_liste(candidati_list, voti, vv)
    else:
        leader_nome, pct_leader, _ = _leader_diretto(candidati_map, voti, vv)

    return {
        "id": sec.get("id"),
        "nome": sec.get("nome", f"Sezione {sec.get('id')}"),
        "elettori": elett,
        "schede_scrutinate": scrut,
        "voti_validi": vv,
        "avanzamento_pct": _pct(scrut, elett),
        "leader_nome": leader_nome,
        "leader_pct": pct_leader,
        "ha_dati": scrut > 0,
        "dettaglio": build_sezione_dettaglio(sec, session),
    }
