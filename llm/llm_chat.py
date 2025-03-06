import os
import json

from pathlib import Path
from config import config

def load_chat():
    if Path(config.CHAT_PATH).is_file():
        with open(config.CHAT_PATH, "r") as f:
            chat = json.loads(f.read())

        return chat

    return []

def save_chat(chat: list):
    with open(config.CHAT_PATH, "w") as f:
        f.write(json.dumps(chat))
    return

def reset_chat():
    try:
        os.remove(config.CHAT_PATH)
        return "Chat history reset"
    except FileNotFoundError:
        return "Chat history does not exist"

