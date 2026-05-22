import os

from flask import (
    Blueprint,
    abort,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)

from config import LOGO_DIR
from services.logo_service import (
    allowed_file,
    apply_crop,
    has_pending_original,
    logo_urls,
    remove_logo,
    save_upload,
    update_session_logo,
)
from services.session_store import load, save

logo_bp = Blueprint("logo", __name__)


@logo_bp.route("/loghi/<session_id>/<filename>")
def serve_logo(session_id, filename):
    safe = os.path.basename(filename)
    directory = os.path.join(LOGO_DIR, session_id)
    if not os.path.isfile(os.path.join(directory, safe)):
        abort(404)
    return send_from_directory(directory, safe)


@logo_bp.route("/scrutinio/<session_id>/logo", methods=["GET"])
def logo_settings(session_id):
    scr = load(session_id)
    if not scr:
        return redirect(url_for("home.index"))
    session["scrutiny_id"] = session_id
    logos = logo_urls(session_id, scr.get("meta", {}).get("logo"))
    pending = has_pending_original(session_id)
    original_url = None
    is_svg = False
    if pending:
        dest_dir = os.path.join(LOGO_DIR, session_id)
        for name in os.listdir(dest_dir):
            if name.startswith("original."):
                original_url = url_for(
                    "logo.serve_logo", session_id=session_id, filename=name
                )
                is_svg = name.lower().endswith(".svg")
                break
    return render_template(
        "logo.html",
        scr=scr,
        logos=logos,
        pending=pending,
        original_url=original_url,
        is_svg=is_svg,
    )


@logo_bp.route("/scrutinio/<session_id>/logo/upload", methods=["POST"])
def upload_logo(session_id):
    scr = load(session_id)
    if not scr:
        return redirect(url_for("home.index"))
    f = request.files.get("logo")
    if not f or not f.filename or not allowed_file(f.filename):
        return redirect(
            url_for("logo.logo_settings", session_id=session_id) + "?err=formato"
        )
    save_upload(session_id, f)
    return redirect(url_for("logo.logo_settings", session_id=session_id))


@logo_bp.route("/scrutinio/<session_id>/logo/applica", methods=["POST"])
def apply_logo(session_id):
    scr = load(session_id)
    if not scr:
        return redirect(url_for("home.index"))
    crop = None
    if request.form.get("crop_x"):
        crop = {
            "x": request.form.get("crop_x"),
            "y": request.form.get("crop_y"),
            "width": request.form.get("crop_w"),
            "height": request.form.get("crop_h"),
        }
    fit = request.form.get("fit", "cover")
    try:
        info = apply_crop(session_id, crop, fit)
        update_session_logo(scr, info)
        save(scr)
    except FileNotFoundError:
        return redirect(
            url_for("logo.logo_settings", session_id=session_id) + "?err=missing"
        )
    return redirect(url_for("logo.logo_settings", session_id=session_id))


@logo_bp.route("/scrutinio/<session_id>/logo/elimina", methods=["POST"])
def delete_logo(session_id):
    scr = load(session_id)
    if not scr:
        return redirect(url_for("home.index"))
    remove_logo(session_id)
    scr.setdefault("meta", {})["logo"] = None
    save(scr)
    return redirect(url_for("logo.logo_settings", session_id=session_id))
