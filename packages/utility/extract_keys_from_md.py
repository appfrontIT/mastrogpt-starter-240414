#--web false
#--kind python:default
#--param GPORCHIA_API_KEY $GPORCHIA_API_KEY
#--annotation description "This action take a markdown document in input and extract each key from a tab. It returns a json. Parameter: {"md": 'md file'}"
#--timeout 300000

from openai import OpenAI
    
ROLE = """Your job is to read a markdown file and extract all the fields inside 'DESCRIZIONE CAMPO', using snake_case. 
Return a json object that works as a guideline to parse a text file.
Example:
{
    "input":
    Row total lenght 300
    DESCRIZIONE CAMPO | TIPO | OFFSET | LUNGH. | NOTE
    -- | -- | -- | -- | --
    Testata | AN | 1 | 50 | Testata standard ANIA. (Vedi Allegato Z)
    Tipo record | AN | 51 | 6 | CIDVLE per Avviso tipologie NON pagate CIDCLE per Chiusura d'ufficio   tipologie NON pagate CIDVPT per Avviso tipologie pagate Parzialmente CIDCPT per Chiusura d'ufficio   tipologie pagate Parzialmente
    Data di elaborazione   ANIA | N | 57 | 8 | Data di elaborazione ANIA Formato AAAAMMGG.
    Edizione tracciato | AN | 65 | 5 | 07.01 (fisso)
    Cod. Impresa Gestionaria   Assegnata | N | 70 | 10 | In caso di assorbimento dell'impresa Gestionaria comunicata,   contiene il codice dell'impresa che l'ha assorbita
    Cod. Impresa Debitrice   Assegnata | N | 80 | 10 | In caso di assorbimento dell'impresa Debitrice comunicata,   contiene il codice dell'impresa che l'ha assorbita
    Cod. Impresa Gestionaria | N | 90 | 10 | Impresa Gestionaria secondo codifica ANIA
    Formato Identificativo Veicolo   Gestionaria | AN | 100 | 1 | Vedi Allegato P
    Identificativo Veicolo   Gestionaria | AN | 101 | 25 | Vedi Allegato A
    Cod. Impresa Debitrice | N | 126 | 10 | Impresa Debitrice secondo codifica ANIA
    Formato Identificativo Veicolo   Debitrice | AN | 136 | 1 | Vedi Allegato P
    Identificativo Veicolo   Debitrice | AN | 137 | 25 | Vedi Allegato A
    Data sinistro | N | 162 | 8 | In formato AAAAMMGG; Esempio: 20020225
    Identificativo partita di   danno danneggiato - Gestionaria | AN | 170 | 20 | Identifica univocamente il danneggiato nell'ambito del   sinistro.
    Tipo danno danneggiato -   Gestionaria | AN | 190 | 1 | V = veicolo P = persona (comprensivo della rivalsa di enti   mutualistici) C = cose
    Identificativo Sinistro   Gestionaria | AN | 191 | 25 | Identifica in modo univoco la posizione del sinistro presso   l'impresa Gestionaria.
    Data ultimo aggiornamento Tipo   Danno comunicato elaborato da ANIA | N | 216 | 8 | AAAAMMGG - data in cui l'ultimo aggiornamento andato a buon   fine è stata elaborata dalla procedura di controllo ANIA.
    Tipo flusso dell'ultimo   aggiornamento Tipo Danno | AN | 224 | 1 | Tipo dell'ultimo flusso che ha aggiornato la tipologia di   danno: D = flusso Denunce R = flusso Riserve P = flusso Pagamenti U = flusso   chiusure d'Ufficio
    Ruolo Impresa | AN | 225 | 1 | G = Gestionaria D = Debitrice
    Non utilizzato |   | 226 | 75 |  

    Where the first 50 bytes are called "testata" first row above. Here the specs.

    Row total lenght 50
    Descrizione   campo | Tipo | Offset | Lungh. | Obblig. | Note
    -- | -- | -- | -- | -- | --
    Cod. impresa mittente | N | 1 | 8 | Si | Codice impresa che trasmette il flusso. Esempio impresa 91:   00000091
    Data inizio elaborazione | N | 9 | 8 | Si | In formato AAAAMMGG Uguale per tutti i record di una stessa   elaborazione
    Ora inizio elaborazione | N | 17 | 6 | Si | In formato HHMMSS Uguale per tutti i record di una stessa   elaborazione
    Progressivo record | N | 23 | 9 | Si |  
    Tipo record | AN | 32 | 4 | Si | Vuoto per tutti i record tranne l'ultimo (valorizzato con   “FINE”)
    Codice flusso | AN | 36 | 8 | Si | Nome flusso
    Codice impresa   destinataria | AN | 44 | 4 | Si | Esempio impresa 91: 0091 - Impostato da ANIA nei flussi per le   imprese. La valorizzazione del campo permette di facilitare la gestione in un   unico file dei dati relativi ad imprese diverse dello stesso gruppo.
    Non utilizzato | AN | 48 | 3 | Inizializzare a spaces |  

    "output":
    {
        "testata" {
            "cod_impresa_mittente": { "offset": 1, "lungh": 8 },
            "data_inizio_elaborazione": { "offset": 9, "lungh": 8 },
            "ora_inizio_elaborazione": { "offset": 17, "lungh": 6 },
            "progressivo_record": { "offset": 23, "lungh": 9 },
            "tipo_record": { "offset": 32, "lungh": 4 },
            "codice_flusso": { "offset": 36, "lungh": 8 },
            "codice_impresa_destinataria": { "offset": 44, "lungh": 4 },
            "non_utilizzato": { "offset": 48, "lungh": 3 },
            },
        "tipo_record": { "offset": 51, "lungh": 6 },
        "data_di_elaborazione_ania": { "offset": 57, "lungh": 8 },
        "edizione_tracciato": { "offset": 65, "lungh": 5 },
        "cod_impresa_gestionaria_assegnata": { "offset": 70, "lungh": 10 },
        "cod_impresa_debitrice_assegnata": { "offset": 80, "lungh": 10 },
        "cod_impresa_gestionaria": { "offset": 90, "lungh": 10 },
        "formato_identificativo_veicolo_gestionaria": { "offset": 100, "lungh": 1 },
        "identificativo_veicolo_gestionaria": { "offset": 101, "lungh": 25 },
        "cod_impresa_debitrice": { "offset": 126, "lungh": 10 },
        "formato_identificativo_veicolo_debitrice": { "offset": 136, "lungh": 1 },
        "identificativo_veicolo_debitrice": { "offset": 137, "lungh": 25 },
        "data_sinistro": { "offset": 162, "lungh": 8 },
        "identificativo_partita_di_danno_danneggiato-gestionaria": { "offset": 170, "lungh": 20 },
        "identificativo_danno_danneggiato-gestionaria": { "offset": 190, "lungh": 1 },
        "identificativo_sinistro_gestionaria": { "offset": 191, "lungh": 25 },
        "data_ultimo_aggiornamento_tipo_danno_comunicato_elaborato_da_ania": { "offset": 216, "lungh": 8 },
        "tipo_flusso_ultimo_aggiornamento_tipo_danno": { "offset": 224, "lungh": 1 },
        "ruolo_impresa": { "offset": 225, "lungh": 1 },
        "non_utilizzato": { "offset": 226, "lungh": 75 },
    }
}

Obviously, the correctness of data is fundamental. Take your time to fulfill the task, think backward and check your answer before sending it.
"""

def main(args):
    md = args.get('md', False)
    if not md:
        return {"statusCode": 400,}
    AI = OpenAI(api_key=args['GPORCHIA_API_KEY'])

    messages = [
            {"role": "system", "content": ROLE},
            {"role": "user", "content": md}
            ]
    response = AI.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        response_format={"type": "json_object"},
    )
    print(response.choices[0].message.content)
    return {"statusCode": 200, "body": response.choices[0].message.content}