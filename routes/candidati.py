from flask import Blueprint, redirect, render_template, request, session, url_for

from services.session_store import load, save

candidati_bp = Blueprint("candidati", __name__)


@candidati_bp.route("/scrutinio/<session_id>/candidati", methods=["GET", "POST"])
def modifica_candidati(session_id):
    scr = load(session_id)
    if not scr:
        return redirect(url_for("home.index"))
    session["scrutiny_id"] = session_id
    if request.method == "POST":
        nomi = request.form.getlist("candidato_nome[]")
        liste = request.form.getlist("candidato_lista[]")
        ids = request.form.getlist("candidato_id[]")
        nuovi = []
        used_ids = set()
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
            nuovi.append(
                {
                    "id": cid,
                    "nome": nome,
                    "lista": liste[i].strip() if i < len(liste) else "",
                }
            )
        if len(nuovi) < 1:
            return render_template(
                "candidati.html",
                scr=scr,
                error="Serve almeno un candidato",
            )
        for sec in scr["sezioni"]:
            old_voti = sec.get("voti", {})
            sec["voti"] = {c["id"]: old_voti.get(c["id"], 0) for c in nuovi}
        cum = scr["cumulativo"]
        old_cum = cum.get("voti", {})
        cum["voti"] = {c["id"]: old_cum.get(c["id"], 0) for c in nuovi}
        scr["candidati"] = nuovi
        save(scr)
        return redirect(url_for("scrutiny.inserimento", session_id=session_id))
    return render_template("candidati.html", scr=scr)
