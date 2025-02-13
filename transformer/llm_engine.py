
from llama_cpp import Llama
from transformer import llm_context

LLM_MODEL_PATH = "models/Qwen2.5-7B-Instruct-IQ4_XS.gguf"
N_GPU_LAYERS = 32
N_CTX = 2048

MAX_TOKENS = 256

def get_model():
    model = Llama(model_path=LLM_MODEL_PATH, n_ctx=N_CTX, n_gpu_layers=N_GPU_LAYERS)
    return model

def answer_prompt(prompt: str, model: Llama):
    system = [{"role": "system", "content": "You are Promya, a helpful assistant."}]
    messages = llm_context.load_context()

    messages.append({"role": "user", "content": prompt})
    completion = model.create_chat_completion(messages=system + messages, max_tokens=MAX_TOKENS)
    answer = completion["choices"][0]["message"]["content"]
    messages.append({"role": "assistant", "content": answer})
    
    llm_context.save_context(messages)

    return answer

