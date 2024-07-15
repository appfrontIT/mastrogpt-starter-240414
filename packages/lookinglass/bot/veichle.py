from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageToolCall
import requests
from typing import List
import config
import json
import base64
import os

MODEL="gpt-4o"

form_validation = False
AccessToken = None

def make_quotation_birth(data):
    global AccessToken
    resp = requests.post("https://cognito-idp.eu-west-1.amazonaws.com/", headers={
        'X-Amz-Target': 'AWSCognitoIdentityProviderService.InitiateAuth',
        'Content-Type': 'application/x-amz-json-1.1',
        'ExternalAuthorization': '',
    },
    json={
        "AuthParameters": {
            "USERNAME": "mastrogpt01@appfront.cloud",
            "PASSWORD": "mastroGPT_2024"
            },
        "AuthFlow": "USER_PASSWORD_AUTH",
        "ClientId": "7a2nff1m1ms4m0g438udgdbaka"
    })
    if resp.status_code != 200:
        print("Error authenticating")
        return False
    obj = json.loads(resp.text)
    AccessToken = obj["AuthenticationResult"]["AccessToken"]
    get_info = requests.post('https://api.appfront.cloud/lookinglass/dev/dllbg/mtr/external/api/v2/quotations/skeleton', headers={
        "Accept": "applicatoin/json",
        'ExternalAuthorization': AccessToken,
        "Authorization": "Bearer kKYdPYn3AwEO3eYMvR1pzPjXWTw4QBafuzy23hy5H4tmgxz8x1mLDHQZpmcz",
        },
        json=data
    )
    if resp.status_code != 200:
        print("Error getting veichle information")
        return False
    print(get_info.text)
    veichle_obj = get_info.json()
    extract_obj = veichle_obj['data']
    extract_obj['targa_attestato_rca_numero'] = ""
    extract_obj['opzione_proprieta'] = '00'
    extract_obj['opzione_atr'] = '00'
    extract_obj['frazionamento'] = 'A'
    extract_obj['rivalsa'] = False
    extract_obj['guida'] = 'Libera'
    extract_obj['massimale'] = "6.450.000/1.300.000€"
    extract_obj['dati_contratto']['infortuni'] = []
    extract_obj['dati_contratto']['assistenza'] = []
    extract_obj['customer_is_owner'] = True
    extract_obj["customer"] = None
    extract_obj['contract_id'] = "123213"
    extract_obj['id_request'] = "213123123123123123"
    extract_obj['owner']['dati_personali']['cap'] = '5#f574f19'
    extract_obj['owner']['dati_personali']['indirizzo'] = 'via del bosco 3'
    extract_obj['owner']['lookinglass']['contact']['email'] = ['matcip@hotmail.com']

    quot_req = requests.post("https://api.appfront.cloud/lookinglass/dev/dllbg/mtr/external/api/v2/quotations", headers={
        "Accept": "application/json",
        'ExternalAuthorization': AccessToken,
        "Authorization": "Bearer kKYdPYn3AwEO3eYMvR1pzPjXWTw4QBafuzy23hy5H4tmgxz8x1mLDHQZpmcz",
    }, json=extract_obj)
    if quot_req.status_code != 200:
        print("Error getting quotation")
        return False
    quot_obj = quot_req.json()
    file = requests.get(f"https://api.appfront.cloud/lookinglass/dev/dllbg/mtr/external/api/v2/quotations/{quot_obj['data']['id']}/download-pdf", headers={
        "Accept": "application/json",
        'ExternalAuthorization': AccessToken,
        "Authorization": "Bearer kKYdPYn3AwEO3eYMvR1pzPjXWTw4QBafuzy23hy5H4tmgxz8x1mLDHQZpmcz",
    })
    presigned = requests.get(f'https://walkiria.cloud/api/v1/web/{os.environ['__OW_NAMESPACE']}/db/minio/static/presignedUrl?name=' + f"quotations/{quot_obj['data']['id']}",
                            headers= {"Authorization": "Bearer " + config.session_user['JWT']})
    if presigned.status_code == 200:
        upload = requests.put(presigned.text, data=file.content)
        if upload.ok:
            config.frame = f"https://walkiria.cloud/" + f"quotations/{quot_obj['data']['id']}"
    return True

def quotation_by_cf(plate, cf):
    global form_validation
    if make_quotation_birth({"targhe": {"targa_polizza_numero": plate, "codice_fiscale_atr": cf}}):
        form_validation = True
        return "quotation obtained"
    return "couldn't get the quotation"

def quotation_by_birth(plate, date_of_birth):
    global form_validation
    if make_quotation_birth({"targhe": {"targa_polizza_numero": plate, "data_nascita": date_of_birth}}):
        form_validation = True
        return "quotation obtained"
    return "couldn't get the quotation"
