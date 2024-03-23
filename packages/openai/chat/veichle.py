from openai import AzureOpenAI
from openai.types.chat import ChatCompletion
import requests
import re
import os
import config
import json
import bot_func

VEICHLE_PREV_ROLE="""
Always answer in the user language.
Never suggest to call any company outside Lookinglass. Avoid suggesting an expert.
you're specialized into veichles ensurance quotations.
Ask for the plate and the one of date of birth or of the user.
"""
MODEL="gpt-35-turbo"
messages=[{"role": "system", "content": VEICHLE_PREV_ROLE}]

form_validation = False
AccessToken = None
quotation_doc = None

def make_quotation(plate, date_of_birth):
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
        json={
        "targhe": {
            "targa_polizza_numero": plate,
            "data_nascita": date_of_birth
        }
    })
    if resp.status_code != 200:
        print("Error getting veichle information")
        return False
    veichle_obj = json.loads(get_info.text)
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
    # quot_obj = json.loads(quot_req.text)
    # pdf = requests.get(f"https://api.appfront.cloud/lookinglass/dev/dllbg/mtr/external/api/v2/quotations/{quot_obj['data']['id']}/download-pdf", headers={
    #     "Accept": "application/json",
    #     'ExternalAuthorization': AccessToken,
    #     "Authorization": "Bearer kKYdPYn3AwEO3eYMvR1pzPjXWTw4QBafuzy23hy5H4tmgxz8x1mLDHQZpmcz",
    # })
    
    # f = open('temp.pdf', 'wb')
    # f.write(pdf.content)
    # path = os.getcwd()
    # print("path " + path)
    # print(os.listdir())
    # path = path + "/temp.pdf"
    # config.html =f"""
    # <iframe src="https://api.appfront.cloud/lookinglass/dev/dllbg/mtr/external/api/v2/quotations/{quot_obj['data']['id']}/download-pdf" width="100%" height="100%"></iframe>
    # """
    # print(config.html)
    global quotation_doc
    quotation_doc = quot_req.text
    # print(quot_req.text)
    return True


def extract_data_from_chat(plate, date_of_birth):
    global form_validation
    print("Data collected, retrieving informantions")
    if make_quotation(plate, date_of_birth):
        form_validation = True
        return "quotation obtained"
    return "couldn't get the quotation"

def is_veichle(AI = AzureOpenAI, input = dict[str, any]) -> ChatCompletion:
    global form_validation
    messages.append(input)
    if form_validation:
        response = AI.chat.completions.create(model=MODEL, messages=[
            {"role": "system", "content": "you answer 0 for negative and 1 for affirmative. You can't use any other character"},
            {"role": "user", "content": f"is the following text affirmative? {input['content']}"}])
        print(response.choices[0].message.content)
        form_validation = False
        if (response.choices[0].message.content == "1"):
            config.is_veichle_pr = False
            messages.append({"role": "assistant", "content": input['content']})
            comp = AI.chat.completions.create(model=MODEL, messages=messages)
            messages = [{"role": "system", "content": VEICHLE_PREV_ROLE}]
            return comp
    fun = bot_func.extract_data_from_chat
    comp = AI.chat.completions.create(model=MODEL, messages=messages, tools=fun, tool_choice="auto")

    if comp.choices[0].finish_reason == "function_call":
        tool_calls = comp.choices[0].message.tool_calls
        available_functions = {
            "extract_data_from_chat": extract_data_from_chat,
            }
        messages.append(comp.choices[0].message)
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(
                plate=function_args.get("plate"),
                date_of_birth=function_args.get("date of birth"),
                )
            messages.append({
                "tool_call_id":tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": function_response
            })
            if function_response == "quotation obtained":
                global quotation_doc
                response = AI.chat.completions.create(model=MODEL, messages=messages)
                messages.append({"role": "assistant", "content": response.choices[0].message.content})
                response = AI.chat.completions.create(model=MODEL, messages=[
                    {"role": "system", "content": "you syntetize the pass text into an insurance quotation and format it in html. Any link must be opened in a new tab. Answer in the user language"},
                    {"role": "user", "content": quotation_doc}
                ])
                config.html = response.choices[0].message.content
                response = AI.chat.completions.create(model=MODEL, messages=messages)
                return response
        response = AI.chat.completions.create(model=MODEL, messages=messages)
        messages.append({"role": "assistant", "content": response.choices[0].message.content})
        return response

    messages.append({"role": "assistant", "content": comp.choices[0].message.content})
    return comp

# ET233BW 04-07-1944