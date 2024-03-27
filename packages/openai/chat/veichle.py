from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageToolCall
import requests
from typing import List
import config
import json

VEICHLE_PREV_ROLE="""
Always answer in the user language.
you're specialized into veichles ensurance quotations.
If the message has a plate and a date, call function
"""
MODEL="gpt-3.5-turbo"
messages=[{"role": "system", "content": VEICHLE_PREV_ROLE}]

form_validation = False
AccessToken = None
quotation_doc = None

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
    extract_obj['owner']['dati_personali']['cap'] = '55049'
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
    quot_obj = json.loads(quot_req.text)
    file = requests.get(f"https://api.appfront.cloud/lookinglass/dev/dllbg/mtr/external/api/v2/quotations/{quot_obj['data']['id']}/download-pdf", headers={
        "Accept": "application/json",
        'ExternalAuthorization': AccessToken,
        "Authorization": "Bearer kKYdPYn3AwEO3eYMvR1pzPjXWTw4QBafuzy23hy5H4tmgxz8x1mLDHQZpmcz",
    })
    pdf_api_key = "matcip@hotmail.com_TPQ0f19qKjQD5K03k7K9v7RR64JVlWkcjhmeCP72x1M68B06WZCFO3wnI1D7Ni0L"
    get_upload_link = requests.get("https://api.pdf.co/v1/file/upload/get-presigned-url", headers={"x-api-key": pdf_api_key}).json()
    # print(get_upload_link.text)
    upload_file = requests.put(get_upload_link['presignedUrl'], headers={"x-api-key": pdf_api_key}, data=file.content)
    print(upload_file.status_code)
    get_html = requests.post("https://api.pdf.co/v1/pdf/convert/to/html", headers={"x-api-key": pdf_api_key}, json={"url": get_upload_link['url']})
    print(get_html.text)
    html_obj = json.loads(get_html.text)
    config.html = f"""<iframe src="{html_obj['url']}" width='100%' height='800'></iframe>"""
    global quotation_doc
    quotation_doc = quot_req.text
    return True

def quotation_by_cf(plate, cf):
    global form_validation
    print("Data collected, retrieving informantions")
    if make_quotation_birth({"targhe": {"targa_polizza_numero": plate, "codice_fiscale_atr": cf}}):
        form_validation = True
        return "quotation obtained"
    return "couldn't get the quotation"

def quotation_by_birth(plate, date_of_birth):
    global form_validation
    print("Data collected, retrieving informantions")
    if make_quotation_birth({"targhe": {"targa_polizza_numero": plate, "data_nascita": date_of_birth}}):
        form_validation = True
        return "quotation obtained"
    return "couldn't get the quotation"

def quotation_func(
        AI: OpenAI,
        tool_calls: List[ChatCompletionMessageToolCall],
        messages: list[dict[str, str]],
        response: ChatCompletion
):
    available_functions = {
        "quotation_by_birth": quotation_by_birth,
        "quotation_by_cf": quotation_by_cf
        }
    messages.append(response.choices[0].message)
    for tool_call in tool_calls:
        function_name = tool_call.function.name
        function_to_call = available_functions[function_name]
        function_args = json.loads(tool_call.function.arguments)
        function_response = function_to_call(
            **function_args
            )
        messages.append({
            "tool_call_id":tool_call.id,
            "role": "tool",
            "name": function_name,
            "content": function_response
        })
    response = AI.chat.completions.create(model=MODEL, messages=messages)
    return response.choices[0].message.content