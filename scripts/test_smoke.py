"""Test manuale end-to-end della logica di proiezione."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from exporters.excel_export import build_excel
from exporters.pdf_export import build_pdf
from services.projection import compute_projection
from services.session_store import new_session, save, load
from services.validation import validate_session


def main():
    candidati = [
        {"id": "1", "nome": "Rossi", "lista": ""},
        {"id": "2", "nome": "Bianchi", "lista": ""},
        {"id": "3", "nome": "Verdi", "lista": ""},
    ]
    sezioni = [{"id": str(i), "nome": f"Sezione {i}", "elettori": 500} for i in range(1, 11)]
    session = new_session("Comune Test", "diretto", candidati, sezioni, 12000)
    for i, sec in enumerate(session["sezioni"][:4]):
        sec["schede_scrutinate"] = 400
        sec["voti_validi"] = 380
        sec["nulli"] = 5
        sec["contestati"] = 0
        sec["bianche"] = 15
        sec["voti"] = {"1": 200 - i * 10, "2": 120 + i * 5, "3": 60 + i * 5}
    save(session)
    loaded = load(session["id"])
    assert loaded is not None
    val = validate_session(loaded)
    assert val["valid"], val["errors"]
    proj = compute_projection(loaded)
    assert proj["schede_scrutinate"] == 1600
    assert proj["schede_totali"] == 5000
    assert len(proj["candidati"]) == 3
    assert proj["esito"]["stato"] in ("incerto", "ballottaggio", "vittoria_primo_turno")
    xlsx = build_excel(loaded, proj)
    pdf = build_pdf(loaded, proj)
    assert len(xlsx) > 1000
    assert len(pdf) > 500
    print("OK smoke test", session["id"], proj["esito"]["messaggio"])
    print("  avanzamento:", proj["avanzamento_pct"], "%")
    for c in proj["candidati"]:
        print(f"  {c['nome']}: {c['voti_reali']} -> proj {c['voti_proiettati']} ({c['pct_proiettate']}%)")


if __name__ == "__main__":
    main()
