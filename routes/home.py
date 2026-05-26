from flask import Blueprint, redirect, render_template, request, session, url_for

from services.app_settings import elettori_sezione_default
from services.liste_candidati import normalize_candidati
from services.session_store import list_sessions, load, new_session, save

home_bp = Blueprint("home", __name__)


@home_bp.route("/")
def index():
    sessions = list_sessions()
    current = session.get("scrutiny_id")
    return render_template("index.html", sessions=sessions, current=current)


@home_bp.route("/setup", methods=["GET", "POST"])
def setup():
    if request.method == "POST":
        comune = request.form.get("comune", "").strip()
        tipo = request.form.get("tipo", "diretto")
        abitanti = request.form.get("abitanti", "").strip()
        elettori_default = elettori_sezione_default()
        nomi_sez = request.form.getlist("sezione_nome[]")
        zone_sez = request.form.getlist("sezione_zona[]")
        elettori_sez = request.form.getlist("sezione_elettori[]")
        nomi = request.form.getlist("candidato_nome[]")
        liste = request.form.getlist("candidato_lista[]")
        candidati = []
        for i, nome in enumerate(nomi):
            nome = nome.strip()
            if not nome:
                continue
            candidati.append(
                {
                    "id": str(len(candidati) + 1),
                    "nome": nome,
                    "lista": liste[i].strip() if i < len(liste) else "",
                }
            )
        if not comune or not candidati:
            return render_template(
                "setup.html", error="Comune e almeno un candidato sono obbligatori"
            )
        sezioni = []
        for i, nome in enumerate(nomi_sez):
            nome = nome.strip() or f"Sezione {i + 1}"
            raw_el = elettori_sez[i] if i < len(elettori_sez) else elettori_default
            elettori = int(raw_el) if str(raw_el).isdigit() else elettori_default
            zona = zone_sez[i].strip() if i < len(zone_sez) else ""
            sezioni.append(
                {
                    "id": str(i + 1),
                    "nome": nome,
                    "zona": zona,
                    "elettori": max(1, elettori),
                }
            )
        if not sezioni:
            return render_template(
                "setup.html",
                error="Inserisci almeno una sezione elettorale",
                elettori_default=elettori_sezione_default(),
            )
        ab = int(abitanti) if abitanti.isdigit() else None
        scr = new_session(comune, tipo, normalize_candidati(candidati), sezioni, ab)
        save(scr)
        session["scrutiny_id"] = scr["id"]
        return redirect(url_for("scrutiny.dashboard", session_id=scr["id"]))
    return render_template(
        "setup.html", elettori_default=elettori_sezione_default()
    )


@home_bp.route("/open/<session_id>")
def open_session(session_id):
    if load(session_id):
        session["scrutiny_id"] = session_id
        return redirect(url_for("scrutiny.dashboard", session_id=session_id))
    return redirect(url_for("home.index"))


@home_bp.route("/nuovo")
def nuovo():
    return redirect(url_for("home.setup"))
