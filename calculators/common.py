from config import SCRUTINIO_INCERTO_SOGLIA, SOGLIA_VITTORIA


def pct(part: float, total: float) -> float:
    if total <= 0:
        return 0.0
    return round(100.0 * part / total, 2)


def esito_elezione(voti_proiettati: list, voti_validi_totali: float, avanzamento: float) -> dict:
    if voti_validi_totali <= 0:
        return {
            "stato": "incerto",
            "messaggio": "Nessun voto valido registrato",
            "vincitore_id": None,
            "ballottaggio": [],
        }
    sorted_c = sorted(voti_proiettati, key=lambda x: x["voti_proiettati"], reverse=True)
    top = sorted_c[0]
    quota = top["voti_proiettati"] / voti_validi_totali
    soglia = SOGLIA_VITTORIA + (1 / voti_validi_totali if voti_validi_totali else 0)
    if quota > SOGLIA_VITTORIA:
        stato = "vittoria_primo_turno"
        messaggio = f"Vittoria al primo turno: {top['nome']}"
        ballottaggio = []
    else:
        stato = "ballottaggio"
        messaggio = (
            "Ballottaggio probabile tra i primi due "
            "(secondo turno non simulato: possibili spostamenti di voto)"
        )
        ballottaggio = sorted_c[:2]
    if avanzamento < SCRUTINIO_INCERTO_SOGLIA and stato != "vittoria_primo_turno":
        stato = "incerto"
        messaggio = f"Scrutinio al {round(avanzamento * 100, 1)}% - esito ancora incerto"
    return {
        "stato": stato,
        "messaggio": messaggio,
        "vincitore_id": top["id"] if stato == "vittoria_primo_turno" else None,
        "ballottaggio": ballottaggio,
        "soglia_pct": round(SOGLIA_VITTORIA * 100, 2),
    }


def build_candidate_rows(
    candidati: list,
    voti_reali: dict,
    voti_proiettati: dict,
    voti_validi_reali: int,
    voti_validi_proiettati: float,
) -> list:
    rows = []
    for c in candidati:
        cid = c["id"]
        vr = voti_reali.get(cid, 0)
        vp = voti_proiettati.get(cid, 0)
        rows.append(
            {
                "id": cid,
                "nome": c["nome"],
                "lista": c.get("lista", ""),
                "voti_reali": vr,
                "pct_reali": pct(vr, voti_validi_reali),
                "voti_proiettati": round(vp),
                "pct_proiettate": pct(vp, voti_validi_proiettati),
                "delta_soglia": round(
                    pct(vp, voti_validi_proiettati) - SOGLIA_VITTORIA * 100, 2
                ),
            }
        )
    return rows
