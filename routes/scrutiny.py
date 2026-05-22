from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for

from services.projection import compute_projection
from services.session_store import append_storico, load, save
from services.validation import validate_session

scrutiny_bp = Blueprint("scrutiny", __name__)


def _get_session(session_id: str):
    return load(session_id)


@scrutiny_bp.route("/scrutinio/<session_id>")
def dashboard(session_id):
    scr = _get_session(session_id)
    if not scr:
        return redirect(url_for("home.index"))
    session["scrutiny_id"] = session_id
    proiezione = compute_projection(scr)
    validazione = validate_session(scr)
    return render_template(
        "dashboard.html",
        scr=scr,
        proiezione=proiezione,
        validazione=validazione,
    )


@scrutiny_bp.route("/scrutinio/<session_id>/inserimento")
def inserimento(session_id):
    scr = _get_session(session_id)
    if not scr:
        return redirect(url_for("home.index"))
    validazione = validate_session(scr)
    return render_template(
        "inserimento.html", scr=scr, validazione=validazione
    )


@scrutiny_bp.route("/scrutinio/<session_id>/inserimento/sezione", methods=["POST"])
def salva_sezione(session_id):
    scr = _get_session(session_id)
    if not scr:
        return redirect(url_for("home.index"))
    sec_id = request.form.get("sezione_id")
    for sec in scr["sezioni"]:
        if sec["id"] == sec_id:
            sec["schede_scrutinate"] = int(request.form.get("schede_scrutinate", 0))
            sec["voti_validi"] = int(request.form.get("voti_validi", 0))
            sec["nulli"] = int(request.form.get("nulli", 0))
            sec["contestati"] = int(request.form.get("contestati", 0))
            sec["bianche"] = int(request.form.get("bianche", 0))
            for c in scr["candidati"]:
                key = f"voto_{c['id']}"
                sec["voti"][c["id"]] = int(request.form.get(key, 0))
            break
    scr["modalita_inserimento"] = "sezione"
    save(scr)
    return redirect(url_for("scrutiny.inserimento", session_id=session_id))


@scrutiny_bp.route("/scrutinio/<session_id>/inserimento/cumulativo", methods=["POST"])
def salva_cumulativo(session_id):
    scr = _get_session(session_id)
    if not scr:
        return redirect(url_for("home.index"))
    cum = scr["cumulativo"]
    cum["schede_scrutinate"] = int(request.form.get("schede_scrutinate", 0))
    cum["voti_validi"] = int(request.form.get("voti_validi", 0))
    cum["nulli"] = int(request.form.get("nulli", 0))
    cum["contestati"] = int(request.form.get("contestati", 0))
    cum["bianche"] = int(request.form.get("bianche", 0))
    for c in scr["candidati"]:
        key = f"voto_{c['id']}"
        cum["voti"][c["id"]] = int(request.form.get(key, 0))
    scr["modalita_inserimento"] = "cumulativo"
    if request.form.get("salva_snapshot"):
        append_storico(scr, request.form.get("nota_snapshot", ""))
    save(scr)
    return redirect(url_for("scrutiny.inserimento", session_id=session_id))


@scrutiny_bp.route("/scrutinio/<session_id>/modalita", methods=["POST"])
def set_modalita(session_id):
    scr = _get_session(session_id)
    if not scr:
        return redirect(url_for("home.index"))
    scr["modalita_inserimento"] = request.form.get("modalita", "sezione")
    save(scr)
    return redirect(url_for("scrutiny.inserimento", session_id=session_id))


@scrutiny_bp.route("/api/scrutinio/<session_id>/proiezione")
def api_proiezione(session_id):
    scr = _get_session(session_id)
    if not scr:
        return jsonify({"error": "Sessione non trovata"}), 404
    metodo = request.args.get("metodo")
    return jsonify(compute_projection(scr, metodo))

