from calculators.common import build_candidate_rows, esito_elezione, pct
from services.liste_candidati import capolista_of, group_by_lista, totale_lista


def project(session: dict, metodo: str) -> dict:
    from services.projection import project_cumulative, project_weighted

    if metodo == "cumulativo" or session.get("modalita_inserimento") == "cumulativo":
        return project_cumulative(session)
    return project_weighted(session)


def _capolista_esito_rows(candidati: list, voti: dict, voti_validi: float) -> list:
    rows = []
    for g in group_by_lista(candidati):
        cap = capolista_of(g["candidati"])
        if not cap:
            continue
        tot = totale_lista(voti, g["candidati"])
        rows.append(
            {
                "id": cap["id"],
                "nome": cap["nome"],
                "voti_proiettati": tot,
                "pct_proiettate": pct(tot, voti_validi),
            }
        )
    return rows


def format_result(raw: dict, session: dict) -> dict:
    candidati = session["candidati"]
    rows = build_candidate_rows(
        candidati,
        raw["voti_reali"],
        raw["voti_proiettati"],
        raw["voti_validi_reali"],
        raw["voti_validi_proiettati"],
    )
    cap_rows = _capolista_esito_rows(
        candidati, raw["voti_proiettati"], raw["voti_validi_proiettati"]
    )
    esito = esito_elezione(cap_rows, raw["voti_validi_proiettati"], raw["avanzamento"])
    for r in rows:
        if r["lista"]:
            tag = " ★" if any(
                c["id"] == r["id"] and c.get("capolista") for c in candidati
            ) else ""
            r["nome_display"] = f"{r['lista']} — {r['nome']}{tag}"
        else:
            r["nome_display"] = r["nome"]
    return {**raw, "candidati": rows, "esito": esito, "tipo_label": "Liste / preferenze"}
