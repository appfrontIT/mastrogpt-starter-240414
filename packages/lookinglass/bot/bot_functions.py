import config
import veichle
from openai.types.chat import ChatCompletion
import requests
from requests.auth import HTTPBasicAuth
import json
import os

def find_man_page(page: str):
    query = str(config.query[-1:])
    query = query.replace("[{'content': '", '')
    query = query.replace("', 'role': 'user'}]", '')
    resp = requests.post(f'https://walkiria.cloud/api/v1/web/mcipolla/embedding/retrieve', auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]), json={
        "collection": 'crawl_appfront_operations__gitbook__io',
        'query': query
    })
    config.frame = f"""https://appfront-operations.gitbook.io/lookinglass-manuale-utente/{page.lower()}"""
    return resp.text

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
    presigned = requests.get(f'https://walkiria.cloud/api/v1/web/mcipolla/db/minio/static/presignedUrl?name=' + f"quotations/{quot_obj['data']['id']}",
                            headers= {"Authorization": "Bearer " + config.session_user['JWT']})
    if presigned.status_code == 200:
        upload = requests.put(presigned.text, data=file.content)
        if upload.ok:
            config.frame = f"https://gporchia.nuvolaris.dev/" + f"quotations/{quot_obj['data']['id']}"
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

def extract_data_from_vehicle_reg(url = None, name = None):
    if not url and not name:
        return "both url and name missing"
    if url:
        response = config.AI.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": [
                {"type": "text", "text": "please extract the following informations from the img:\n" + config.carta_circolazione + "\nPlease, take your time to answer, it's very important that the informations are as much precise as possible"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": url,
                        "detail": "high"
                        },
                    }
                ]
            }
        ])
    return f"please use the full name of each category instead of the code:\n{response.choices[0].message.content}"

def tools_func(
        messages: list[dict[str, str]],
        response: ChatCompletion
        ):
    # requests.post("https://walkiria.cloud/api/v1/namespaces/mcipolla/actions/db/load_message", auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]), json={'id': config.session_user['_id'], "message": {"output": "Certo, procedo subito con la tua richiesta"}})
    while True:
        tool_calls = response.choices[0].message.tool_calls
        messages.append(response.choices[0].message)
        for tool_call in tool_calls:
            print(tool_call.function.name)
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(
                **function_args
                )
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": function_response
            })
        response = config.AI.chat.completions.create(model='gpt-4o', messages=messages, tools=tools, tool_choice="auto", temperature=0.1, top_p=0.1)
        if response.choices[0].finish_reason != "tool_calls":
            break
        # requests.post("https://walkiria.cloud/api/v1/namespaces/mcipolla/actions/db/load_message",
        #             auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]),
        #             json={'id': config.session_user['_id'], "message": {"output": "Sto elaborando la tua richiesta, per favore attendi"}}
        #             )
    return response.choices[0].message.content

available_functions = {
    "quotation_by_birth": quotation_by_birth,
    "quotation_by_cf": quotation_by_cf,
    "find_man_page": find_man_page,
    "extract_data_from_vehicle_reg": extract_data_from_vehicle_reg
}

tools = [
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
                    "page": {"type": "string", "description": f"one of the following manual page:\n{config.man}\n. Take your time to analyze the data, the page must be exact"},
                    },
                    "required": ["page"],
                },
            }
        },
        {
            "type": "function",
            "function": {
                "name": "extract_data_from_vehicle_reg",
                "description": "extract the vehicle registration document from a pdf, it can be url or name but not both",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "the pdf url"},
                        "name": {"type": "string", "description": "the pdf name stored in the database"},
                        "base64img": {"type": "string", "description": "base64 string representing an img"}
                    },
                },
            },
        }
    ]