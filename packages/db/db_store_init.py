#--web false
#--kind python:default
#--annotation provide-api-key true
#--param OPENAI_API_KEY $OPENAI_API_KEY
#--annotation description "store a collection of data inside the database following a specific format"
#--timeout 600000
#--annotation url https://walkiria.cloud/api/v1/namespaces/mcipolla/actions/db/db_store_init

import requests
from requests.auth import HTTPBasicAuth
import os
import json
from itertools import islice
from bs4 import BeautifulSoup
import time

OW_KEY = os.getenv('__OW_API_KEY')
OW_API_SPLIT = OW_KEY.split(':')

def crawl(url):
    response = requests.get(url)
    if response.status_code != 200:
        print("Error fetching page")
        return ""
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup.get_text()

def main(args):
    url = args.get('url', False)
    format = args.get('format', False)
    collection = args.get('collection', False)
    user = args.get('user', False)
    if not url or not format or not collection or not user:
        return {"statusCode": 400, "body": "data incomplete"}
    token = args.get('token', False)
    if not token:
        return {'statusCode': 401}
    
    text = crawl(url)
    format_obj = requests.post('https://walkiria.cloud/api/v1/namespaces/mcipolla/actions/utility/md_to_json?blocking=true', auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]), json={
        "md": format
    })
    obj = format_obj.json()
    md = obj['response']['result']['body']
    split = text.splitlines()
    request = f"""
    create an action that will take a 'line' as parameter and store it inside a json.
    The line will be like: {split[0]}, and the json must follow this guidelines: {format}.
    You will find the start and the length of each element inside the guideline.
    The action must return the filled json.
    Use the following name for the action: {collection}_store
    remember to import the necessary libraries.
    Don't put authorization inside the action.
    Example:
    {{
        "guidelines": {{
            "testata" {{
                "cod_impresa_mittente": {{ "offset": 1, "lungh": 8 }},
                "data_inizio_elaborazione": {{ "offset": 9, "lungh": 8 }},
                "ora_inizio_elaborazione": {{ "offset": 17, "lungh": 6 }},
                "progressivo_record": {{ "offset": 23, "lungh": 9 }},
                "tipo_record": {{ "offset": 32, "lungh": 4 }},
                "codice_flusso": {{ "offset": 36, "lungh": 8 }},
                "codice_impresa_destinataria": {{ "offset": 44, "lungh": 4 }},
                "non_utilizzato": {{ "offset": 48, "lungh": 3 }},
                }},
            "tipo_record": {{ "offset": 51, "lungh": 6 }},
            "data_di_elaborazione_ania": {{ "offset": 57, "lungh": 8 }},
            "edizione_tracciato": {{ "offset": 65, "lungh": 5 }},
            "cod_impresa_gestionaria_assegnata": {{ "offset": 70, "lungh": 10 }},
            "cod_impresa_debitrice_assegnata": {{ "offset": 80, "lungh": 10 }},
            "cod_impresa_gestionaria": {{ "offset": 90, "lungh": 10 }},
            "formato_identificativo_veicolo_gestionaria": {{ "offset": 100, "lungh": 1 }},
            "identificativo_veicolo_gestionaria": {{ "offset": 101, "lungh": 25 }},
            "cod_impresa_debitrice": {{ "offset": 126, "lungh": 10 }},
            "formato_identificativo_veicolo_debitrice": {{ "offset": 136, "lungh": 1 }},
            "identificativo_veicolo_debitrice": {{ "offset": 137, "lungh": 25 }},
            "data_sinistro": {{ "offset": 162, "lungh": 8 }},
            "identificativo_partita_di_danno_danneggiato-gestionaria": {{ "offset": 170, "lungh": 20 }},
            "identificativo_danno_danneggiato-gestionaria": {{ "offset": 190, "lungh": 1 }},
            "identificativo_sinistro_gestionaria": {{ "offset": 191, "lungh": 25 }},
            "data_ultimo_aggiornamento_tipo_danno_comunicato_elaborato_da_ania": {{ "offset": 216, "lungh": 8 }},
            "tipo_flusso_ultimo_aggiornamento_tipo_danno": {{ "offset": 224, "lungh": 1 }},
            "ruolo_impresa": {{ "offset": 225, "lungh": 1 }},
            "non_utilizzato": {{ "offset": 226, "lungh": 75 }},
            }}

        "ouput": {{
            def main(args):
                import re
                line = args.get('line', False)
                if not line:
                    return {{"statusCode": 400}}
                data = {{
                    'Testata': {{
                        'cod_impresa_mittente': line[0:7].strip(),
                        'data_inizio_elaborazione': line[8:16].strip(),
                        'ora_inizio_elaborazione': line[16:22].strip(),
                        'progressivo_record': line[22:31].strip(),
                        'tipo_record': line[31:35].strip(),
                        'codice_flusso': line[35:43].strip(),
                        'codice_impresa_destinataria': line[43:47].strip(),
                        'non_utilizzato': line[47:50].strip(),
                        }}
                    'tipo_record': line[50:56].strip(),
                    'data_di_elaborazione_ania': line[56:64].strip(),
                    'edizione_tracciato': line[64:69].strip(),
                    'cod_impresa_gestionaria_assegnata': line[69:79].strip(),
                    'cod_impresa_debitrice_assegnata': line[79:89].strip(),
                    'cod_impresa_gestionaria': line[89:99].strip(),
                    'formato_identificativo_veicolo_gestionaria': line[99:100].strip(),
                    'identificativo_veicolo_gestionaria': line[100:125].strip(),
                    'cod_impresa_debitrice': line[125:135].strip(),
                    'formato_identificativo_veicolo_debitrice': line[135:136].strip(),
                    'identificativo_veicolo_debitrice': line[136:161].strip(),
                    'data_sinistro': line[161:169].strip(),
                    'identificativo_partita_di_danno_danneggiato-gestionaria': line[169:189].strip(),
                    'identificativo_danno_danneggiato-gestionaria': line[189:190].strip(),
                    'identificativo_sinistro_gestionaria': line[190:215].strip(),
                    'data_ultimo_aggiornamento_tipo_danno_comunicato_elaborato_da_ania': line[215:223].strip(),
                    'tipo_flusso_ultimo_aggiornamento_tipo_danno': line[223:224].strip(),
                    'ruolo_impresa': line[224:225].strip(),
                    'non_utilizzato': line[225:300].strip()
                }}
                return {{'body': data}}
        }}
    }}

    Remember to keep the same keys as the guidelines, all lowercase and snake_case
    """
    action = requests.post('https://walkiria.cloud/api/v1/namespaces/mcipolla/actions/walkiria/generate?blocking=true',
                        auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]),
                        json={"request": request, "token": token}
                        )
    action_obj = action.json()
    body = action_obj['response']['result']['body']
    url = body.split("'")[1]
    while True:
        lines = list(islice(split, 500))
        if not lines:
            break
        requests.post('https://walkiria.cloud/api/v1/namespaces/mcipolla/actions/db/db_store_exec',
                    auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]),
                    json={"format": md, "collection": collection, "text": lines, "url": url}
                    )
        split = split[500:]
        time.sleep(1)
    return {"statusCode": 204}
