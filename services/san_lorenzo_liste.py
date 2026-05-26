"""Costruisce l'elenco candidati liste per San Lorenzo del Vallo."""

LISTA_AZIA = "Lista 1"
LISTA_RIMOLI = "Lista 2"

CONSIGLIERI_AZIA = [
    "GRAZIA",
    "BOSCO ANTONIO",
    "BIANCO ANASTASIA",
    "BELLUSCI FRANCESCO",
    "BOSCO GIUSEPPE",
    "CORRADO EMILIO",
    "CURTI GIACOMO",
    "FAILLACE ALESSANDRO",
    "IANTORNO SERGIO",
    "MAGNAVITA ELENA",
    "MAURO SARA",
    "MOSCA ANTONIO",
    "SANNUTI IOLANDA",
]

CONSIGLIERI_LISTA_2 = [
    "CIPOLLA CINZIA",
    "CIPOLLA FRANCESCO",
    "DE MARCO DOMENICO",
    "FILICE ANGELO",
    "FUSARO CLAUDIA",
    "MOSCA MARTINA",
    "MOTTA PASQUALE",
    "PIRAGINE NICOLA",
    "VERTA SIMONA",
    "VICECONTE AGOSTINO",
    "VICECONTE BIAGIO",
]


def build_san_lorenzo_candidati(
    capolista_azia: str = "Marranghello",
    capolista_lista2: str = "Rimoli",
) -> list[dict]:
    out: list[dict] = [
        {
            "id": "1",
            "nome": capolista_azia,
            "lista": LISTA_AZIA,
            "capolista": True,
        }
    ]
    next_id = 3
    for nome in CONSIGLIERI_AZIA:
        out.append(
            {
                "id": str(next_id),
                "nome": nome,
                "lista": LISTA_AZIA,
                "capolista": False,
            }
        )
        next_id += 1
    out.append(
        {
            "id": "2",
            "nome": capolista_lista2,
            "lista": LISTA_RIMOLI,
            "capolista": True,
        }
    )
    for nome in CONSIGLIERI_LISTA_2:
        out.append(
            {
                "id": str(next_id),
                "nome": nome,
                "lista": LISTA_RIMOLI,
                "capolista": False,
            }
        )
        next_id += 1
    return out
