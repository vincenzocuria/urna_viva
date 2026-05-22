from flask import Blueprint, jsonify, render_template, request

from config import DISPLAY_POLL_MS, DISPLAY_SEZIONI_PREVIEW
from services.live_payload import build_live_payload
from services.session_store import load

display_bp = Blueprint("display", __name__)


@display_bp.route("/proiezione/<session_id>")
def proiezione_tv(session_id):
    scr = load(session_id)
    if not scr:
        return "Scrutinio non trovato", 404
    return render_template(
        "display.html",
        session_id=session_id,
        comune=scr["meta"].get("comune", ""),
        poll_ms=DISPLAY_POLL_MS,
        sezioni_preview=DISPLAY_SEZIONI_PREVIEW,
    )


@display_bp.route("/api/scrutinio/<session_id>/live")
def api_live(session_id):
    scr = load(session_id)
    if not scr:
        return jsonify({"error": "Sessione non trovata"}), 404
    metodo = request.args.get("metodo")
    return jsonify(build_live_payload(scr, metodo))
