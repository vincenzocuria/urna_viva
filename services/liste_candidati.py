def _nome_key(c: dict) -> str:
    return (c.get("nome") or "").strip().casefold()


def sort_candidati_alphabetic(candidati: list) -> list:
    order: list[str] = []
    buckets: dict[str, list] = {}
    for c in candidati:
        lista = (c.get("lista") or "").strip() or "Senza lista"
        if lista not in buckets:
            order.append(lista)
            buckets[lista] = []
        buckets[lista].append(c)
    out: list = []
    for lista in order:
        out.extend(sorted(buckets[lista], key=_nome_key))
    return out


def sort_candidati_in_lista(candidati_lista: list, *, capolista_first: bool = False) -> list:
    if not capolista_first:
        return sorted(candidati_lista, key=_nome_key)
    cap = capolista_of(candidati_lista)
    cap_id = cap.get("id") if cap else None
    rest = sorted(
        (c for c in candidati_lista if c.get("id") != cap_id),
        key=_nome_key,
    )
    return ([cap] if cap else []) + rest


def group_by_lista(candidati: list, *, capolista_first: bool = False) -> list[dict]:
    order: list[str] = []
    buckets: dict[str, list] = {}
    for c in candidati:
        lista = (c.get("lista") or "").strip() or "Senza lista"
        if lista not in buckets:
            order.append(lista)
            buckets[lista] = []
        buckets[lista].append(c)
    return [
        {
            "nome": nome,
            "candidati": sort_candidati_in_lista(
                buckets[nome], capolista_first=capolista_first
            ),
        }
        for nome in order
    ]


def capolista_of(candidati_lista: list) -> dict | None:
    for c in candidati_lista:
        if c.get("capolista"):
            return c
    return candidati_lista[0] if candidati_lista else None


def somma_preferenze(voti: dict, candidati: list) -> int:
    return sum(int(voti.get(c["id"], 0) or 0) for c in candidati)


def somma_preferenze_lista(voti: dict, candidati_lista: list) -> int:
    return somma_preferenze(voti, candidati_lista)


def totale_lista(voti: dict, candidati_lista: list) -> int:
    """Voti di lista / sindaco = somma preferenze di tutta la lista (capolista incluso)."""
    return somma_preferenze_lista(voti, candidati_lista)


def somma_voti_sindaco(voti: dict, candidati: list) -> int:
    """Somma dei totali lista (un totale per lista)."""
    total = 0
    for g in group_by_lista(candidati):
        total += totale_lista(voti, g["candidati"])
    return total


def somma_preferenze_consiglieri(voti: dict, candidati_lista: list) -> int:
    cap = capolista_of(candidati_lista)
    cap_id = cap.get("id") if cap else None
    return sum(
        int(voti.get(c["id"], 0) or 0)
        for c in candidati_lista
        if c.get("id") != cap_id
    )


def voti_per_liste(voti: dict, candidati: list) -> dict[str, int]:
    out: dict[str, int] = {}
    for g in group_by_lista(candidati):
        out[g["nome"]] = somma_preferenze_lista(voti, g["candidati"])
    return out


def capolista_rows_for_esito(candidati: list, voti: dict) -> list[dict]:
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
                "lista": g["nome"],
                "voti_proiettati": tot,
            }
        )
    return rows


def normalize_candidati(candidati: list) -> list:
    out = []
    for i, c in enumerate(candidati):
        out.append(
            {
                "id": c.get("id") or str(i + 1),
                "nome": c["nome"].strip(),
                "lista": (c.get("lista") or "").strip(),
                "capolista": bool(c.get("capolista")),
            }
        )
    _ensure_capoliste(out)
    return sort_candidati_alphabetic(out)


def _ensure_capoliste(candidati: list) -> None:
    for g in group_by_lista(candidati):
        cands = g["candidati"]
        caps = [c for c in cands if c.get("capolista")]
        if len(caps) == 1:
            continue
        for c in cands:
            c["capolista"] = False
        if cands:
            cands[0]["capolista"] = True
