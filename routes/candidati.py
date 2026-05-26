from flask import Blueprint, redirect, render_template, request, session, url_for

from services.liste_candidati import group_by_lista, normalize_candidati
from services.session_liste import sync_voti_candidati
from services.session_store import load, save

candidati_bp = Blueprint("candidati", __name__)


def _parse_candidati_form(scr) -> list | str:
    nomi = request.form.getlist("candidato_nome[]")
    liste = request.form.getlist("candidato_lista[]")
    ids = request.form.getlist("candidato_id[]")
    capolisti = {
        v.strip()
        for k, v in request.form.items()
        if k.startswith("capolista_lista__") and v.strip()
    }
    nuovi = []
    used_ids: set[str] = set()
    for i, nome in enumerate(nomi):
        nome = nome.strip()
        if not nome:
            continue
        cid = ids[i].strip() if i < len(ids) and ids[i].strip() else ""
        if not cid or cid in used_ids:
            n = 1
            while str(n) in used_ids:
                n += 1
            cid = str(n)
        used_ids.add(cid)
        lista = liste[i].strip() if i < len(liste) else ""
        nuovi.append(
            {
                "id": cid,
                "nome": nome,
                "lista": lista,
                "capolista": cid in capolisti,
            }
        )
    if len(nuovi) < 1:
        return "Serve almeno un candidato"
    if scr["meta"].get("tipo") == "liste":
        liste_ok = {c["lista"] for c in nuovi if c["lista"]}
        if not liste_ok:
            return "Inserisci almeno una lista con candidati"
    return normalize_candidati(nuovi)


def _sync_voti(scr, candidati: list) -> None:
    for sec in scr["sezioni"]:
        sync_voti_candidati(sec, candidati)
    sync_voti_candidati(scr["cumulativo"], candidati)


@candidati_bp.route("/scrutinio/<session_id>/candidati", methods=["GET", "POST"])
def modifica_candidati(session_id):
    scr = load(session_id)
    if not scr:
        return redirect(url_for("home.index"))
    session["scrutiny_id"] = session_id
    if request.method == "POST":
        parsed = _parse_candidati_form(scr)
        if isinstance(parsed, str):
            return render_template(
                "candidati.html",
                scr=scr,
                liste_gruppi=group_by_lista(scr["candidati"]),
                error=parsed,
            )
        _sync_voti(scr, parsed)
        scr["candidati"] = parsed
        save(scr)
        return redirect(url_for("scrutiny.inserimento", session_id=session_id))
    for c in scr.get("candidati", []):
        c.setdefault("capolista", False)
    return render_template(
        "candidati.html",
        scr=scr,
        liste_gruppi=group_by_lista(scr["candidati"]),
    )
