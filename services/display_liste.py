from calculators.common import pct
from services.liste_candidati import capolista_of, group_by_lista, totale_lista


def _totali_lista_da_rows(
    candidati_lista: list, by_id: dict, key_reali: str, key_proj: str
) -> tuple[int, int]:
    tot_r = sum(int(by_id.get(c["id"], {}).get(key_reali, 0) or 0) for c in candidati_lista)
    tot_p = sum(
        round(float(by_id.get(c["id"], {}).get(key_proj, 0) or 0))
        for c in candidati_lista
    )
    return tot_r, tot_p


def sindaco_display_rows(
    candidati: list, candidati_rows: list, proiezione: dict
) -> list:
    by_id = {r["id"]: r for r in candidati_rows}
    vv_r = proiezione.get("voti_validi_reali", 0)
    vv_p = proiezione.get("voti_validi_proiettati", 0)
    out = []
    for g in group_by_lista(candidati):
        cap = capolista_of(g["candidati"])
        if not cap:
            continue
        tot_r, tot_p = _totali_lista_da_rows(
            g["candidati"], by_id, "voti_reali", "voti_proiettati"
        )
        out.append(
            {
                "id": cap["id"],
                "nome": cap["nome"],
                "lista": g["nome"],
                "nome_display": cap["nome"],
                "voti_reali": tot_r,
                "voti_proiettati": tot_p,
                "tot_r": tot_r,
                "tot_p": tot_p,
            }
        )
    denom_r = sum(r["tot_r"] for r in out) or vv_r
    denom_p = sum(r["tot_p"] for r in out) or vv_p
    for r in out:
        r["pct_reali"] = pct(r["tot_r"], denom_r)
        r["pct_proiettate"] = pct(r["tot_p"], denom_p)
        r["pct_su_validi_reali"] = pct(r["tot_r"], vv_r)
        r["pct_su_validi_proiettati"] = pct(r["tot_p"], vv_p)
        r["delta_soglia"] = round(r["pct_su_validi_proiettati"] - 50.0, 2)
        del r["tot_r"]
        del r["tot_p"]
    out.sort(key=lambda r: r["pct_proiettate"], reverse=True)
    return out


def preferenze_modal_payload(
    candidati: list, candidati_rows: list, proiezione: dict | None = None
) -> list:
    by_id = {r["id"]: r for r in candidati_rows}
    vv_r = int((proiezione or {}).get("voti_validi_reali", 0) or 0)
    vv_p = float((proiezione or {}).get("voti_validi_proiettati", 0) or 0)
    liste = []
    for g in group_by_lista(candidati, capolista_first=True):
        cap = capolista_of(g["candidati"])
        cap_id = cap["id"] if cap else None
        tot_r, tot_p = _totali_lista_da_rows(
            g["candidati"], by_id, "voti_reali", "voti_proiettati"
        )
        membri = []
        for c in g["candidati"]:
            is_cap = c["id"] == cap_id
            row = by_id.get(c["id"], {})
            vr = int(row.get("voti_reali", 0) or 0)
            vp = round(float(row.get("voti_proiettati", 0) or 0))
            membri.append(
                {
                    "id": c["id"],
                    "nome": c["nome"],
                    "capolista": is_cap,
                    "voti_reali": vr,
                    "pct_reali": pct(vr, vv_r),
                    "voti_proiettati": vp,
                    "pct_proiettate": pct(vp, vv_p),
                }
            )
        membri.sort(key=lambda m: (0 if m["capolista"] else 1, -m["voti_proiettati"]))
        liste.append(
            {
                "nome": g["nome"],
                "capolista_nome": cap["nome"] if cap else "",
                "totale_proiettato": tot_p,
                "totale_reale": tot_r,
                "candidati": membri,
            }
        )
    return liste
