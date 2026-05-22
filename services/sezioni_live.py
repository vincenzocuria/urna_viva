def build_sezioni_live(session: dict) -> list:
    candidati = {c["id"]: c for c in session.get("candidati", [])}
    out = []
    for sec in session.get("sezioni", []):
        vv = sec.get("voti_validi", 0)
        voti = sec.get("voti", {}) or {}
        leader_id = None
        leader_voti = 0
        if vv > 0 and voti:
            leader_id = max(voti.keys(), key=lambda k: voti.get(k, 0))
            leader_voti = voti.get(leader_id, 0)
        elett = int(sec.get("elettori", 0))
        scrut = int(sec.get("schede_scrutinate", 0))
        leader = candidati.get(leader_id) if leader_id else None
        leader_nome = leader["nome"] if leader else None
        if leader and leader.get("lista"):
            leader_nome = f"{leader['lista']} — {leader['nome']}"
        pct_leader = round(100.0 * leader_voti / vv, 1) if vv else 0.0
        out.append(
            {
                "id": sec.get("id"),
                "nome": sec.get("nome", f"Sezione {sec.get('id')}"),
                "elettori": elett,
                "schede_scrutinate": scrut,
                "voti_validi": vv,
                "avanzamento_pct": round(100.0 * scrut / elett, 1) if elett else 0.0,
                "leader_nome": leader_nome,
                "leader_pct": pct_leader,
                "ha_dati": scrut > 0,
            }
        )
    return out
