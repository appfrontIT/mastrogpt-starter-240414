import config
from openai.types.chat import ChatCompletion

extract_data_from_chat = [
    {
        "type": "function",
        "function": {
            "name": "extract_data_from_chat",
            "description": "Extract veichle plate and user date of birth. Store the data in DD-MM-YY",
            "parameters": {
                "type": "object",
                "properties": {
                    "plate" : {"type": "string", "description": "plate of veichle"},
                    "ssc" : {"type": "string", "description": "social security certificate of user"},
                    "date of birth": { "type": "string", "description": "user date of birth"},
                    },
                    "required": ["plate", "date_of_birth"],
                    "required": ["ssc", "date_of_birth"]
                },
            }
        }
    ]


def find_link(link):
    print("find link")
    if link.find("appfront-operations.gitbook.io/lookinglass-manuale-utente") != -1:
        config.html = "<iframe src='https://appfront-operations.gitbook.io/lookinglass-manuale-utente' width='100%' height='800'></iframe>"
    return "ok"

find_link_tool = [
    {
        "type": "function",
        "function": {
            "name": "find_link",
            "description": "extract links",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "url in text"},
                },
            },
            "required": ["url"],
        }
    }
]

def find_man(
        data: str,
        AI: ChatCompletion
        ):
    if data.find("appfront-operations.gitbook.io/lookinglass-manuale-utente") != -1:
        # response = AI.chat.completions.create(
        #     model="gpt-3.5-turbo",
        #     messages= [
        #         {"role": "system", "content": "Return the number associated with the topic:"}
        #     ],
        # )
        config.html = "<iframe src='https://appfront-operations.gitbook.io/lookinglass-manuale-utente' width='100%' height='800'></iframe>"