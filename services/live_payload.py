from config import DISPLAY_SEZIONI_PREVIEW
from services.logo_service import logo_urls
from services.projection import compute_projection
from services.sezioni_live import build_sezioni_live
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
    candidati = []
    for i, c in enumerate(proiezione.get("candidati", [])):
        candidati.append(
            {
                **c,
                "color": CANDIDATE_COLORS[i % len(CANDIDATE_COLORS)],
                "rank": i + 1,
            }
        )
    proiezione["candidati"] = candidati
    sezioni = build_sezioni_live(session)
    return {
        "revision": session["meta"].get("aggiornato", ""),
        "session_id": session["id"],
        "comune": session["meta"].get("comune", ""),
        "tipo": session["meta"].get("tipo", ""),
        "logo": logos,
        "proiezione": proiezione,
        "sezioni": sezioni,
        "sezioni_totali": len(sezioni),
        "sezioni_preview": DISPLAY_SEZIONI_PREVIEW,
        "validazione_ok": validazione["valid"],
        "warnings_count": len(validazione.get("warnings", [])),
    }
