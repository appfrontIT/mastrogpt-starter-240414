import config
from openai.types.chat import ChatCompletion

man_pages = ["accesso", "main", "articoli-wip", "dashboard", "intermediari", "utenti", "profili", "sconti-templates-wip", "preventivi", "blacklist-review", "contraenti-to-start", "dllbg-aagrafica-to-start", "polizze", "titoli", "post-vendita", "appendice-a-teoria-rca"]

quotation_functions = [
    {
        "type": "function",
        "function": {
            "name": "quotation_by_birth",
            "description": "Extract veichle plate and user date of birth. Store the data in DD-MM-YY",
            "parameters": {
                "type": "object",
                "properties": {
                    "plate" : {"type": "string", "description": "plate of veichle"},
                    "date_of_birth": { "type": "string", "description": "user date of birth"},
                    },
                    "required": ["plate", "date_of_birth"],
                },
            }
        },
        {
        "type": "function",
        "function": {
            "name": "quotation_by_cf",
            "description": "Extract veichle plate and user Tax ID code ",
            "parameters": {
                "type": "object",
                "properties": {
                    "plate" : {"type": "string", "description": "plate of veichle"},
                    "cf": { "type": "string", "description": "user Tax ID code"},
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
                    "page": {"type": "string", "description": f"one of the following manual page:{man_pages}"},
                    },
                    "required": ["page"],
                },
            }
        }
    ]