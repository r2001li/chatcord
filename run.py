import datetime
import json
import tomllib
from ollama import ChatResponse, Client
import os

import discord
from discord.ext import commands

from dotenv import load_dotenv

with open("config/config.toml", 'rb') as f:
    config_data = tomllib.load(f)

HOST_URL = config_data['ollama']['host_url']
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
ollama_client = Client(host=HOST_URL)

# Initialize listeners
listening_channels = {}

def generate_response(prompt):
    chat_history.append({
        "role": "user",
        "content": prompt
        })

    system_prompt = [{
        "role": "system",
        "content": "You are a user on the Discord messaging platform, and your username is " + str(client.user.name)
        }]

    response: ChatResponse = ollama_client.chat(
            model=config_data['ollama']['model'],
            messages=system_prompt + chat_history,
            stream=False
            )
    
    print("Raw Response Content: ", response)

    assistant_message = response.message.content
    
    chat_history.append({
        "role": "assistant",
        "content": assistant_message
        })

    save_history()

    return assistant_message

async def process_message(message: discord.Message):
    # Format prompt
    prompt = message.clean_content
    prompt = f"{message.author.display_name} messages you: {prompt}"

    # Send generated response
    try:
        async with message.channel.typing():
            response = generate_response(prompt)
            await message.channel.send(response)
    except discord.errors.Forbidden:
        print(f"Error: Bot does not have permission to type in {message.channel.name}")
    
    return


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@client.event
async def on_message(message: discord.Message):
    # Ignore messages from self or bots
    if message.author == client.user:
        return

    if message.author.bot:
        return

    # Clean up any expired session
    now = datetime.datetime.utcnow()
    channel_id = message.channel.id

    if channel_id in listening_channels:
        if now > listening_channels[channel_id]:
            del listening_channels[channel_id]
            print("Session expired for channel: ", channel_id)

    # When mentioned, answer prompt and start listening
    if client.user in message.mentions:
        listening_channels[channel_id] = now + datetime.timedelta(minutes=2)
        print("Starting session for channel: ", channel_id)
        return await process_message(message)

    # If not mentioned, answer prompt only if channel is active
    if channel_id in listening_channels:
        listening_channels[channel_id] = now + datetime.timedelta(minutes=2)
        print("Extending session for channel: ", channel_id)
        return await process_message(message)

load_dotenv()
client.run(os.getenv("TOKEN"))
