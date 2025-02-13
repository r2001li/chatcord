import os
import re

import discord
from discord.ext import commands

from dotenv import load_dotenv

from transformer import llm_engine

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

print("Loading model...")
model = llm_engine.get_model()
print(f"Loaded model: {llm_engine.LLM_MODEL_PATH}")

is_chatting = False

@bot.event
async def on_ready():
    print("Login successful")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    '''
    if bot.user not in message.mentions:
        return
    '''

    message_clean = message.clean_content
    print("Generating answer for prompt: ", message_clean)
    async with message.channel.typing():
        answer = llm_engine.answer_prompt(prompt=message_clean, model=model)
    return await message.channel.send(answer)

load_dotenv()
bot.run(os.getenv("TOKEN"))
