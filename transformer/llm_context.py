import os
import json

from pathlib import Path

CONTEXT_PATH = "data/saved-context.json"
CONTEXT_SIZE = 20

def load_context():
    if Path(CONTEXT_PATH).is_file():
        with open(CONTEXT_PATH, "r") as f:
            messages = json.loads(f.read())

        return messages

    messages = []
    return messages

def save_context(messages: list):
    with open(CONTEXT_PATH, "w") as f:
        f.write(json.dumps(messages))
    return

def reset_context():
    try:
        os.remove(CONTEXT_PATH)
        return "Context reset"
    except FileNotFoundError:
        return "Context file does not exist"

