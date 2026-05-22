from flask import Blueprint, redirect, render_template, request, url_for

from services.app_settings import load_settings, save_settings

settings_bp = Blueprint("settings", __name__)


@settings_bp.route("/impostazioni", methods=["GET", "POST"])
def impostazioni():
    if request.method == "POST":
        raw = request.form.get("elettori_sezione_default", "500")
        try:
            val = max(1, int(raw))
        except ValueError:
            val = 500
        save_settings({"elettori_sezione_default": val})
        return redirect(url_for("settings.impostazioni") + "?ok=1")
    cfg = load_settings()
    return render_template(
        "impostazioni.html",
        cfg=cfg,
        saved=request.args.get("ok") == "1",
    )
