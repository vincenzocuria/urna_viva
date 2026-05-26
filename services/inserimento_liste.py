def liste_verbale_da_form(form) -> dict[str, int]:
    out: dict[str, int] = {}
    for key, raw in form.items():
        if not key.startswith("lista_verbale__"):
            continue
        nome = key[len("lista_verbale__") :]
        if not nome or not str(raw).strip():
            continue
        out[nome] = max(0, int(raw))
    return out
