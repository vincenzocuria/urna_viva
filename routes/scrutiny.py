from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for

from services.inserimento_fase import (
    applica_spoglio,
    elettori_totali,
    registra_arrivo,
)
from services.inserimento_liste import liste_verbale_da_form
from services.liste_candidati import group_by_lista
from services.projection import compute_projection
from services.session_store import append_storico, load, save
from services.spoglio_progress import compute_spoglio_progress
from services.validation import validate_session

scrutiny_bp = Blueprint("scrutiny", __name__)


def _get_session(session_id: str):
    return load(session_id)


def _redirect_inserimento(session_id: str, errore: str | None = None):
    if errore:
        return redirect(
            url_for("scrutiny.inserimento", session_id=session_id, errore=errore)
        )
    return redirect(url_for("scrutiny.inserimento", session_id=session_id))


def _voti_da_form(scr) -> dict[str, int]:
    voti = {}
    for c in scr["candidati"]:
        voti[c["id"]] = int(request.form.get(f"voto_{c['id']}", 0))
    return voti


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
    spoglio_prog = compute_spoglio_progress(scr)
    return render_template(
        "inserimento.html",
        scr=scr,
        validazione=validazione,
        spoglio_prog=spoglio_prog,
        errore=request.args.get("errore", ""),
        liste_gruppi=group_by_lista(scr["candidati"], capolista_first=True),
    )


@scrutiny_bp.route("/scrutinio/<session_id>/inserimento/sezione", methods=["POST"])
def salva_sezione(session_id):
    scr = _get_session(session_id)
    if not scr:
        return redirect(url_for("home.index"))
    sec_id = request.form.get("sezione_id")
    fase = request.form.get("fase", "spoglio")
    conferma = request.form.get("conferma_modifica") == "1"
    target = next((s for s in scr["sezioni"] if s["id"] == sec_id), None)
    if not target:
        return _redirect_inserimento(session_id, "Sezione non trovata.")

    if fase == "arrivo":
        err = registra_arrivo(
            target,
            int(request.form.get("schede_scrutinate", 0)),
            int(target.get("elettori", 0)),
            conferma,
        )
        if err:
            return _redirect_inserimento(session_id, err)
    else:
        is_liste = scr.get("meta", {}).get("tipo") == "liste"
        err = applica_spoglio(
            target,
            int(request.form.get("nulli", 0)),
            int(request.form.get("contestati", 0)),
            int(request.form.get("bianche", 0)),
            _voti_da_form(scr),
            liste=is_liste,
        )
        if err:
            return _redirect_inserimento(session_id, err)
        if is_liste:
            target["liste_verbale"] = liste_verbale_da_form(request.form)

    scr["modalita_inserimento"] = "sezione"
    save(scr)
    return _redirect_inserimento(session_id)


@scrutiny_bp.route("/scrutinio/<session_id>/inserimento/cumulativo", methods=["POST"])
def salva_cumulativo(session_id):
    scr = _get_session(session_id)
    if not scr:
        return redirect(url_for("home.index"))
    cum = scr["cumulativo"]
    fase = request.form.get("fase", "spoglio")
    conferma = request.form.get("conferma_modifica") == "1"

    if fase == "arrivo":
        err = registra_arrivo(
            cum,
            int(request.form.get("schede_scrutinate", 0)),
            elettori_totali(scr),
            conferma,
        )
        if err:
            return _redirect_inserimento(session_id, err)
    else:
        is_liste = scr.get("meta", {}).get("tipo") == "liste"
        err = applica_spoglio(
            cum,
            int(request.form.get("nulli", 0)),
            int(request.form.get("contestati", 0)),
            int(request.form.get("bianche", 0)),
            _voti_da_form(scr),
            liste=is_liste,
        )
        if err:
            return _redirect_inserimento(session_id, err)
        if is_liste:
            cum["liste_verbale"] = liste_verbale_da_form(request.form)
        if request.form.get("salva_snapshot"):
            append_storico(scr, request.form.get("nota_snapshot", ""))

    scr["modalita_inserimento"] = "cumulativo"
    save(scr)
    return _redirect_inserimento(session_id)


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
