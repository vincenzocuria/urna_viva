from config import TOLLERANZA_VOTI


def _nome_sezione(section: dict) -> str:
    return section.get("nome", section.get("id", "?"))


def validate_section(
    section: dict, candidati_ids: list, liste: bool = False
) -> tuple[list[str], list[str]]:
    errors = []
    warnings = []
    nome = _nome_sezione(section)
    elettori = section.get("elettori", 0)
    scrutinate = section.get("schede_scrutinate", 0)
    if scrutinate > elettori:
        errors.append(
            f"Sezione {nome}: schede scrutinate ({scrutinate}) > elettori ({elettori})"
        )
    voti_validi = section.get("voti_validi", 0)
    somma_voti = sum(section.get("voti", {}).get(cid, 0) for cid in candidati_ids)
    if not liste and voti_validi > 0:
        diff = somma_voti - voti_validi
        if diff > TOLLERANZA_VOTI:
            errors.append(
                f"Sezione {nome}: somma voti candidati ({somma_voti}) "
                f"supera i voti validi ({voti_validi})"
            )
        elif diff < -TOLLERANZA_VOTI:
            mancano = voti_validi - somma_voti
            warnings.append(
                f"Sezione {nome}: spoglio incompleto — "
                f"mancano {mancano} voti da distribuire ai candidati "
                f"({somma_voti}/{voti_validi})"
            )
    altri = (
        section.get("nulli", 0)
        + section.get("contestati", 0)
        + section.get("bianche", 0)
    )
    if voti_validi + altri > scrutinate + TOLLERANZA_VOTI:
        errors.append(
            f"Sezione {nome}: voti validi + nulli/contestati/bianche "
            f"superano le schede scrutinate"
        )
    return errors, warnings


def validate_session(session: dict) -> dict:
    candidati_ids = [c["id"] for c in session["candidati"]]
    errors = []
    warnings = []
    modalita = session.get("modalita_inserimento", "sezione")
    liste = session.get("meta", {}).get("tipo") == "liste"
    if modalita == "cumulativo":
        sec_errors, sec_warnings = validate_section(
            session["cumulativo"], candidati_ids, liste
        )
        errors.extend(sec_errors)
        warnings.extend(sec_warnings)
    else:
        for sec in session["sezioni"]:
            sec_errors, sec_warnings = validate_section(sec, candidati_ids, liste)
            errors.extend(sec_errors)
            warnings.extend(sec_warnings)
            if sec.get("schede_scrutinate", 0) == 0:
                warnings.append(f"Sezione {sec.get('nome')}: nessun dato inserito")
    tot_elettori = sum(s["elettori"] for s in session["sezioni"])
    if tot_elettori == 0:
        errors.append("Elettorato totale nullo")
    return {"errors": errors, "warnings": warnings, "valid": len(errors) == 0}
