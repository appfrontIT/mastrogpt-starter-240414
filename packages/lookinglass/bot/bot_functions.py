import config
from openai.types.chat import ChatCompletion

man_pages = ["accesso", "main", "articoli-wip", "dashboard", "intermediari", "utenti", "profili", "sconti-templates-wip", "preventivi", "blacklist-review", "contraenti-to-start", "dllbg-aagrafica-to-start", "polizze", "titoli", "post-vendita", "appendice-a-teoria-rca"]

man = """
    |- lookinglass-manuale-utente
        |- lookinglass-manuale-utente#id-1-portale
        |- lookinglass-manuale-utente#id-2-login
        |- lookinglass-manuale-utente#id-3-problematiche-di-login
    |- main
        | main#id-1-struttura
        | main#id-1.1-logo-ipa
        | main#id-1.2-tasto-assistenza
        | main#id-1.3-menu
        | main#id-1.4-barra-di-scorrimento
        | main#id-1.5-filtro
        | main#id-1.6-indice
        | main#id-1.7-overview-comunicazioni-ufficiali
    |- articoli-wip
        |- articoli-wip#id-2.-come-creare-un-articolo
    |- dashboard
        | dashboard#id-1-struttura
        | dashboard#id-1.1-menu
        | dashboard#id-1.2-info-utente
        | dashboard#id-1.3-percorso
        | dashboard#id-1.4-panoramica
    |- intermediari
        |- intermediari#id-1.-definizione
        |- intermediari#id-2.-view
        |- intermediari#id-3.-come-creare-un-intermediario
        |- intermediari#id-4.-modifica-un-intermediario
    |- utenti
        |- utenti#introduzione
        |- utenti#id-1.-creazione-utenza
        |- utenti#id-2.-aggiornare-lutenza
    |- profili
    |- sconti-templates-wip
        |- sconti-templates-wip#introduzione
        |- sconti-templates-wip#id-1.-come-creare-un-sconto-template
        |- sconti-templates-wip#id-2-come-modificare
    |- ruoli-review
        |- ruoli-review#id-1-definizione
        |- ruoli-review#id-2-come-creare-un-ruolo
        |- ruoli-review#id-3-modifica-e-duplica
    |- ruoli-analisi-wip
    |- preventivi
        |- preventivi#id-1.-definizione
        |- preventivi#id-2.-come-creare-un-preventivo
        |- preventivi#id-3.-stesura-preventivo
        |- preventivi#id-4.-come-modificare-un-preventivo
    |- blacklist-review
        |- blacklist-review#id-1-definizione-e-introduzione
        |- blacklist-review#id-2-come-inserire-un-codice-fiscale-allinterno-della-blacklist
        |- blacklist-review#id-3-modifica-e-attivazione
    |- contraenti-to-start
    |- dllbg-aagrafica-to-start
    |- polizze
        |- polizze#id-1.definizione
        |- polizze#id-2.come-cercare-una-polizza
        |- polizze#id-3.come-visualizzare-una-polizza
    |- titoli
        |- titoli#id-1.definizione
        |- titoli#id-2.-come-cercare-un-titolo
        |- titoli#id-3-utilita-del-titolo
    |- post-vendita
        |- post-vendita#id-1.sostituire-una-polizza
        |- post-vendita#id-2.annullare-polizze
        |- post-vendita#id-3.sospendere-polizze
        |- post-vendita#id-4.riattivare-polizza
    |- appendice-a-teoria-rca
        |- appendice-a-teoria-rca#preventivi
        |- appendice-a-teoria-rca#le-targhe
        |- appendice-a-teoria-rca#gli-attestati-di-rischio
        |- appendice-a-teoria-rca#le-operazioni-recupero-atr-e-bersani
        |- appendice-a-teoria-rca#emissione
        |- appendice-a-teoria-rca#anatomia-della-polizza
        |- appendice-a-teoria-rca#i-dati-piu-importanti
        |- appendice-a-teoria-rca#titoli
        |- appendice-a-teoria-rca#quietanze
        |- appendice-a-teoria-rca#rinnovi
        |- appendice-a-teoria-rca#sostituzioni
        |- appendice-a-teoria-rca#annullamenti
        |- appendice-a-teoria-rca#sospensioni-e-riattivazioni
    |- appendice-a-teoria"""

quotation_functions = [
    {
        "type": "function",
        "function": {
            "name": "quotation_by_birth",
            "description": "The user wants to make a quotation using veichle plate and date of birth",
            "parameters": {
                "type": "object",
                "properties": {
                    "plate" : {"type": "string", "description": "plate of veichle"},
                    "date_of_birth": { "type": "string", "description": "date of birth of the veichle owner"},
                    },
                    "required": ["plate", "date_of_birth"],
                },
            }
        },
        {
        "type": "function",
        "function": {
            "name": "quotation_by_cf",
            "description": "The user wants to make a quotation using veichle plate and Tax ID code ",
            "parameters": {
                "type": "object",
                "properties": {
                    "plate" : {"type": "string", "description": "plate of veichle"},
                    "cf": { "type": "string", "description": "tax ID of the veichle owner"},
                    },
                    "required": ["plate", "cf"],
                },
            }
        },
        {
        "type": "function",
        "function": {
            "name": "find_man_page",
            "description": "the user wants information about the manual",
            "parameters": {
                "type": "object",
                "properties": {
                    "page": {"type": "string", "description": f"one of the following manual page:\n{man}\n. Take your time to analyze the data, the page must be exact"},
                    },
                    "required": ["page"],
                },
            }
        }
    ]