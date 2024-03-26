import utils
html = ""

nuvolaris = []

nuvolaris.append(utils.crawl("https://nuvolaris.github.io/nuvolaris/3.1.0/development/actions.html"))
nuvolaris.append(utils.crawl("https://nuvolaris.github.io/nuvolaris/3.1.0/development/webactions.html"))
nuvolaris.append(utils.crawl("https://nuvolaris.github.io/nuvolaris/3.1.0/development/parameters.html"))
nuvolaris.append(utils.crawl("https://nuvolaris.github.io/nuvolaris/3.1.0/development/annotations.html"))

EMB = f"""
From now on you are a programming language. If you show some code, do only in Python. Answer based on this informations:
{nuvolaris}
"""

func_finder = [
    {
        "type": "function",
        "function": {
            "name": "find_func",
            "description": "find the function inside the text, a",
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
]