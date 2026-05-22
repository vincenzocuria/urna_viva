# Urna Viva

Proiezione indicativa delle elezioni comunali italiane: parziali per sezione, dashboard live, schermata TV e export Excel/PDF.

Stack: **Python 3.11+**, **Flask**, senza login né database (dati in JSON locali).

## Funzioni

- Setup scrutinio (sindaco diretto o liste / capolista)
- Inserimento parziali per sezione o cumulativo, con sincronizzazione automatica dei conteggi
- Proiezione pesata per **zona** elettorale
- Stima di nulli, bianche e contestati
- Schermata **Proiezione TV** a tutto schermo con aggiornamento live
- Pagina **Dettaglio sezioni** con tabella completa
- Logo comune con ritaglio
- Export Excel e PDF
- Gestione scrutinii salvati e snapshot storico

## Avvio rapido

```bash
pip install -r requirements.txt
python app.py
```

Apri nel browser: **http://127.0.0.1:5050**

## Struttura

```
app.py              # Avvio Flask
config.py           # Configurazione (nome app, soglie, percorsi)
routes/             # Endpoint HTTP
services/           # Logica scrutinio, proiezione, logo
calculators/        # Regole elettorali (50%+1, ballottaggio)
exporters/          # Excel e PDF
templates/          # Interfaccia web
static/             # CSS e JavaScript
data/sessions/      # Scrutini salvati (gitignored)
```

## Note legali

La proiezione è **indicativa e statistica**. Non sostituisce il verbale di seggio né ha valore ufficiale. Il ballottaggio mostrato è una simulazione sul trend attuale, non modella il secondo turno.

## Licenza

MIT — vedi file [LICENSE](LICENSE).
