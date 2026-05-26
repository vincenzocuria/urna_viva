from config import DISPLAY_SEZIONI_PREVIEW
from services.display_liste import preferenze_modal_payload, sindaco_display_rows
from services.logo_service import logo_urls
from services.projection import compute_projection
from services.sezioni_live import build_sezioni_live, stima_schede_votate_finale
from services.validation import validate_session


CANDIDATE_COLORS = [
    "#3b82f6",
    "#22c55e",
    "#f59e0b",
    "#ec4899",
    "#8b5cf6",
    "#06b6d4",
    "#ef4444",
    "#84cc16",
]


def build_live_payload(session: dict, metodo: str | None = None) -> dict:
    proiezione = compute_projection(session, metodo)
    validazione = validate_session(session)
    logos = logo_urls(session["id"], session.get("meta", {}).get("logo"))
    tipo = session.get("meta", {}).get("tipo", "")
    all_rows = proiezione.get("candidati", [])
    preferenze: list = []
    display_rows = all_rows
    if tipo == "liste":
        display_rows = sindaco_display_rows(
            session["candidati"], all_rows, proiezione
        )
        preferenze = preferenze_modal_payload(
            session["candidati"], all_rows, proiezione
        )
        for i, lista in enumerate(preferenze):
            lista["color"] = CANDIDATE_COLORS[i % len(CANDIDATE_COLORS)]
    candidati = []
    for i, c in enumerate(display_rows):
        candidati.append(
            {
                **c,
                "color": CANDIDATE_COLORS[i % len(CANDIDATE_COLORS)],
                "rank": i + 1,
            }
        )
    proiezione = {**proiezione, "candidati": candidati}
    sezioni = build_sezioni_live(session)
    schede = stima_schede_votate_finale(session)
    alert_sindaco = ""
    if tipo == "liste":
        vv = int(proiezione.get("voti_validi_reali", 0) or 0)
        sind = sum(int(r.get("voti_reali", 0) or 0) for r in display_rows)
        if vv > 0 and sind < vv * 0.85:
            alert_sindaco = (
                f"Preferenze incomplete: somma totali lista {sind} su {vv} "
                f"voti validi — completa tutte le liste in Inserimento e salva."
            )
    return {
        "revision": session["meta"].get("aggiornato", ""),
        "session_id": session["id"],
        "comune": session["meta"].get("comune", ""),
        "tipo": session["meta"].get("tipo", ""),
        "logo": logos,
        "proiezione": proiezione,
        "preferenze": preferenze,
        "sezioni": sezioni,
        "schede_votate": schede,
        "sezioni_totali": len(sezioni),
        "sezioni_preview": DISPLAY_SEZIONI_PREVIEW,
        "validazione_ok": validazione["valid"],
        "warnings_count": len(validazione.get("warnings", [])),
        "alert_sindaco": alert_sindaco,
    }
