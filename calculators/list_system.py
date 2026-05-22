from calculators.common import build_candidate_rows, esito_elezione


def project(session: dict, metodo: str) -> dict:
    from services.projection import project_cumulative, project_weighted

    if metodo == "cumulativo" or session.get("modalita_inserimento") == "cumulativo":
        return project_cumulative(session)
    return project_weighted(session)


def format_result(raw: dict, session: dict) -> dict:
    candidati = session["candidati"]
    rows = build_candidate_rows(
        candidati,
        raw["voti_reali"],
        raw["voti_proiettati"],
        raw["voti_validi_reali"],
        raw["voti_validi_proiettati"],
    )
    esito = esito_elezione(rows, raw["voti_validi_proiettati"], raw["avanzamento"])
    for r in rows:
        if r["lista"]:
            r["nome_display"] = f"{r['lista']} — {r['nome']}"
        else:
            r["nome_display"] = r["nome"]
    return {**raw, "candidati": rows, "esito": esito, "tipo_label": "Liste / capolista"}
