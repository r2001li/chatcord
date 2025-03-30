import requests
import json
import tomllib
from ollama import ChatResponse, Client
import os

import discord
from discord.ext import commands

from dotenv import load_dotenv
from asyncio import timeout

with open("config/config.toml", 'rb') as f:
    config_data = tomllib.load(f)

API_URL = config_data['ollama']['api_url']
HISTORY_PATH = config_data['history']['history_path']

def load_history():
    if os.path.exists(HISTORY_PATH):
        with open(HISTORY_PATH, 'r') as f:
            return json.load(f)

    return []

def save_history():
    with open(HISTORY_PATH, 'w') as f:
        json.dump(chat_history, f)

# Initialize chat history
chat_history = load_history()

# Initialize Discord client
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
client = discord.Client(intents=intents)

# Initialize Ollama client
ollama_client = Client(host='http://localhost:11434')

def generate_response(prompt):
    chat_history.append({
        "role": "user",
        "content": prompt
        })

    # save_history()

    system_prompt = [{
        "role": "system",
        "content": "You are aser on the Discord messaging platform, and your username is " + str(client.user.name)
        }]

    '''
    data = {
            "model": config_data['ollama']['model'],
            "messages": system_prompt + chat_history,
            "stream": False
            }

    response = requests.post(API_URL, json=data)
    '''
    
    response: ChatResponse = ollama_client.chat(
            model=config_data['ollama']['model'],
            messages=system_prompt + chat_history,
            stream=False
            )
    
    print("Raw Response Content: ", response)

    '''
    try:
        response_data = response.json()
        assistant_message = response_data['message']['content']
        chat_history.append({
            "role": "assistant",
            "content": assistant_message
            })

        save_history()

        return assistant_message
    except requests.exceptions.JSONDecodeError:
        return "Error: Invalid API response"
    '''

    assistant_message = response.message.content
    
    chat_history.append({
        "role": "assistant",
        "content": assistant_message
        })

    save_history()

    return assistant_message

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.author.bot == True:
        return

    if client.user.mentioned_in(message):
        prompt = message.clean_content
        prompt = f"{message.author.display_name} messages you: {prompt}"

        try:
            async with message.channel.typing():
                if prompt:
                    response = generate_response(prompt)
                    await message.channel.send(response)
        except discord.errors.Forbidden:
            print(f"Error: Bot does not have permission to type in {message.channel.name}")
            return

load_dotenv()
client.run(os.getenv("TOKEN"))
