from fpdf import FPDF


def _ascii_safe(text: str) -> str:
    return text.replace("\u2014", "-").replace("\u2013", "-").encode("ascii", "replace").decode("ascii")


def build_pdf(session: dict, proiezione: dict) -> bytes:
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    meta = session["meta"]
    pdf.cell(0, 10, f"Parziali elezioni comunali - {meta.get('comune', '')}", ln=True)
    pdf.set_font("Helvetica", "", 10)
    esito = proiezione.get("esito", {})
    info = [
        f"Tipo: {proiezione.get('tipo_label', meta.get('tipo'))}",
        f"Metodo: {proiezione.get('metodo_label', '')}",
        f"Avanzamento: {proiezione.get('avanzamento_pct', 0)}% "
        f"({proiezione.get('schede_scrutinate', 0)} / {proiezione.get('schede_totali', 0)} schede)",
        f"Esito: {esito.get('messaggio', '')}",
    ]
    for line in info:
        pdf.cell(0, 7, _ascii_safe(line), ln=True)
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 9)
    cols = ["Candidato", "Voti", "%", "Proiett.", "% proj.", "Delta"]
    widths = [70, 25, 20, 30, 25, 25]
    for w, c in zip(widths, cols):
        pdf.cell(w, 8, c, border=1)
    pdf.ln()
    pdf.set_font("Helvetica", "", 9)
    for cand in proiezione.get("candidati", []):
        nome = cand.get("nome_display", cand["nome"])
        if cand.get("lista"):
            nome = f"{cand['lista']} - {cand['nome']}"
        row = [
            _ascii_safe(nome[:40]),
            str(cand["voti_reali"]),
            f"{cand['pct_reali']}%",
            str(cand["voti_proiettati"]),
            f"{cand['pct_proiettate']}%",
            f"{cand['delta_soglia']}%",
        ]
        for w, val in zip(widths, row):
            pdf.cell(w, 7, val, border=1)
        pdf.ln()
    pdf.ln(6)
    pdf.set_font("Helvetica", "I", 8)
    pdf.multi_cell(
        0,
        5,
        "Proiezione indicativa, non ufficiale. Non sostituisce il verbale di seggio.",
    )
    out = pdf.output()
    return bytes(out) if not isinstance(out, bytes) else out
