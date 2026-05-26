def _cap_schede(schede: int, max_elettori: int) -> int:
    return max(0, min(schede, max_elettori))


def registra_arrivo(
    target: dict, schede: int, max_elettori: int, conferma: bool
) -> str | None:
    nuove = _cap_schede(schede, max_elettori)
    vecchie = int(target.get("schede_scrutinate", 0))
    if vecchie > 0 and nuove != vecchie and not conferma:
        return "Per modificare le schede votate serve conferma esplicita."
    target["schede_scrutinate"] = nuove
    return None


def applica_spoglio(
    target: dict,
    nulli: int,
    contestati: int,
    bianche: int,
    voti: dict[str, int],
    liste: bool = False,
) -> str | None:
    scrutinate = int(target.get("schede_scrutinate", 0))
    if scrutinate <= 0:
        return "Registra prima le schede votate."
    nulli = max(0, nulli)
    contestati = max(0, contestati)
    bianche = max(0, bianche)
    altri = nulli + contestati + bianche
    if altri > scrutinate:
        return (
            f"Nulli ({nulli}) + contestati ({contestati}) + bianche ({bianche}) "
            f"= {altri}: superano le schede votate ({scrutinate})."
        )
    voti_validi = scrutinate - altri
    somma_voti = sum(voti.values())
    if not liste and somma_voti > voti_validi:
        return (
            f"Somma voti candidati ({somma_voti}) supera i voti validi ({voti_validi})."
        )
    target["nulli"] = nulli
    target["contestati"] = contestati
    target["bianche"] = bianche
    target["voti_validi"] = voti_validi
    target["voti"] = voti
    return None


def elettori_totali(session: dict) -> int:
    return sum(int(s.get("elettori", 0)) for s in session.get("sezioni", []))
