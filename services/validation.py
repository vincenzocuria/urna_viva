from config import TOLLERANZA_VOTI


def validate_section(section: dict, candidati_ids: list) -> list[str]:
    errors = []
    elettori = section.get("elettori", 0)
    scrutinate = section.get("schede_scrutinate", 0)
    if scrutinate > elettori:
        errors.append(
            f"Sezione {section.get('nome', section.get('id'))}: "
            f"schede scrutinate ({scrutinate}) > elettori ({elettori})"
        )
    voti_validi = section.get("voti_validi", 0)
    somma_voti = sum(section.get("voti", {}).get(cid, 0) for cid in candidati_ids)
    if abs(somma_voti - voti_validi) > TOLLERANZA_VOTI:
        errors.append(
            f"Sezione {section.get('nome', section.get('id'))}: "
            f"somma voti candidati ({somma_voti}) "
            f"non coincide con voti validi ({voti_validi})"
        )
    altri = (
        section.get("nulli", 0)
        + section.get("contestati", 0)
        + section.get("bianche", 0)
    )
    if voti_validi + altri > scrutinate + TOLLERANZA_VOTI:
        errors.append(
            f"Sezione {section.get('nome', section.get('id'))}: "
            f"voti validi + nulli/contestati/bianche superano le schede scrutinate"
        )
    return errors


def validate_session(session: dict) -> dict:
    candidati_ids = [c["id"] for c in session["candidati"]]
    errors = []
    warnings = []
    modalita = session.get("modalita_inserimento", "sezione")
    if modalita == "cumulativo":
        errors.extend(validate_section(session["cumulativo"], candidati_ids))
    else:
        for sec in session["sezioni"]:
            errors.extend(validate_section(sec, candidati_ids))
            if sec.get("schede_scrutinate", 0) == 0:
                warnings.append(f"Sezione {sec.get('nome')}: nessun dato inserito")
    tot_elettori = sum(s["elettori"] for s in session["sezioni"])
    if tot_elettori == 0:
        errors.append("Elettorato totale nullo")
    return {"errors": errors, "warnings": warnings, "valid": len(errors) == 0}
