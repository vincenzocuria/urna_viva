from datetime import datetime

from flask import Blueprint, Response, abort

from exporters.excel_export import build_excel
from exporters.pdf_export import build_pdf
from services.projection import compute_projection
from services.session_store import load

export_bp = Blueprint("export", __name__)


@export_bp.route("/export/<session_id>.xlsx")
def export_xlsx(session_id):
    scr = load(session_id)
    if not scr:
        abort(404)
    proiezione = compute_projection(scr)
    data = build_excel(scr, proiezione)
    nome = scr["meta"]["comune"].replace(" ", "_")
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"parziali_{nome}_{ts}.xlsx"
    return Response(
        data,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@export_bp.route("/export/<session_id>.pdf")
def export_pdf(session_id):
    scr = load(session_id)
    if not scr:
        abort(404)
    proiezione = compute_projection(scr)
    data = build_pdf(scr, proiezione)
    nome = scr["meta"]["comune"].replace(" ", "_")
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"parziali_{nome}_{ts}.pdf"
    return Response(
        data,
        mimetype="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
