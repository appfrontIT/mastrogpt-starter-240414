import config
from openai.types.chat import ChatCompletion

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
        }
    ]

find_man_page = [
    {
        "type": "function",
        "function": {
            "name": "find_man_page",
            "description": "Find the right manual page",
            "parameters": {
                "type": "object",
                "properties": {
                    "page": {"type": "string", "description": "manual page section"},
                },
            },
            "required": ["page"],
        }
    }
]