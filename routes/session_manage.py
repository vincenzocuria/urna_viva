from flask import Blueprint, redirect, render_template, request, session, url_for

from services.app_settings import elettori_sezione_default
from services.session_manage import (
    clear_storico,
    delete_session,
    delete_storico_entry,
    update_meta,
    update_sezioni_config,
    update_storico_nota,
)
from services.session_store import load, save

manage_bp = Blueprint("manage", __name__)


@manage_bp.route("/scrutinio/<session_id>/elimina", methods=["POST"])
def elimina_scrutinio(session_id):
    if load(session_id):
        delete_session(session_id)
        if session.get("scrutiny_id") == session_id:
            session.pop("scrutiny_id", None)
    return redirect(url_for("home.index"))


@manage_bp.route("/scrutinio/<session_id>/modifica", methods=["GET", "POST"])
def modifica_scrutinio(session_id):
    scr = load(session_id)
    if not scr:
        return redirect(url_for("home.index"))
    if request.method == "POST":
        comune = request.form.get("comune", "").strip()
        if not comune:
            return render_template(
                "modifica_scrutinio.html",
                scr=scr,
                error="Il nome del comune è obbligatorio",
                elettori_default=elettori_sezione_default(),
            )
        update_meta(scr, comune, request.form.get("abitanti", ""))
        nomi_sez = request.form.getlist("sezione_nome[]")
        zone_sez = request.form.getlist("sezione_zona[]")
        elettori_sez = request.form.getlist("sezione_elettori[]")
        ids_sez = request.form.getlist("sezione_id[]")
        sezioni_in = []
        for i, nome in enumerate(nomi_sez):
            nome = nome.strip() or f"Sezione {i + 1}"
            raw_el = elettori_sez[i] if i < len(elettori_sez) else "100"
            sid = ids_sez[i] if i < len(ids_sez) else str(i + 1)
            elettori = int(raw_el) if str(raw_el).isdigit() else 100
            zona = zone_sez[i].strip() if i < len(zone_sez) else ""
            sezioni_in.append(
                {"id": sid, "nome": nome, "zona": zona, "elettori": elettori}
            )
        if sezioni_in:
            update_sezioni_config(scr, sezioni_in)
        save(scr)
        return redirect(url_for("scrutiny.dashboard", session_id=session_id))
    return render_template(
        "modifica_scrutinio.html",
        scr=scr,
        elettori_default=elettori_sezione_default(),
    )


@manage_bp.route("/scrutinio/<session_id>/storico", methods=["GET", "POST"])
def gestione_storico(session_id):
    scr = load(session_id)
    if not scr:
        return redirect(url_for("home.index"))
    if request.method == "POST":
        action = request.form.get("action")
        if action == "svuota":
            clear_storico(scr)
        elif action == "elimina":
            idx = int(request.form.get("index", -1))
            delete_storico_entry(scr, idx)
        elif action == "modifica_nota":
            idx = int(request.form.get("index", -1))
            update_storico_nota(scr, idx, request.form.get("nota", ""))
        save(scr)
        return redirect(url_for("manage.gestione_storico", session_id=session_id))
    return render_template("storico.html", scr=scr)
