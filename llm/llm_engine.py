from llama_cpp import Llama
from llm import llm_chat
import json

from config import config

def get_model():
    model = Llama(model_path=config.MODEL_PATH, n_ctx=config.CONTEXT_LEN, n_gpu_layers=config.GPU_LAYERS)
    return model

def answer_prompt(prompt: str, uname: str, model: Llama):
    uinfo = f" You are addressing the user through the Discord messaging platform. Your display name is {uname}."
    system = [{"role": "system", "content": config.SYSTEM_PROMPT + uinfo}]
    chat = llm_chat.load_chat()

    chat.append({"role": "user", "content": prompt})
    completion = model.create_chat_completion(messages=system + chat, max_tokens=config.MAX_TOKENS)
    answer = completion["choices"][0]["message"]["content"]
    chat.append({"role": "assistant", "content": answer})
    
    llm_chat.save_chat(chat)

    return answer

