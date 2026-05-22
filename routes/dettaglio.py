from flask import Blueprint, render_template, request

from services.dettaglio_sezioni import build_dettaglio
from services.session_store import load
from services.validation import validate_session

dettaglio_bp = Blueprint("dettaglio", __name__)


@dettaglio_bp.route("/scrutinio/<session_id>/dettaglio")
def pagina_dettaglio(session_id):
    scr = load(session_id)
    if not scr:
        return "Scrutinio non trovato", 404
    metodo = request.args.get("metodo")
    dettaglio = build_dettaglio(scr, metodo)
    validazione = validate_session(scr)
    return render_template(
        "dettaglio.html",
        scr=scr,
        dettaglio=dettaglio,
        proiezione=dettaglio["proiezione"],
        validazione=validazione,
    )
