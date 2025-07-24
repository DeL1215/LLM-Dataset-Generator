# configuration.py

from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()


openai_api_key = os.getenv("OPENAI_API_KEY")
openai_model = os.getenv("OPENAI_MODEL")

LLM_OpenAI = ChatOpenAI(
    model=openai_model,
    temperature=0.7,
    openai_api_key=openai_api_key
)

openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
openrouter_model = os.getenv("OPENROUTER_MODEL")

LLM_OpenRouter =ChatOpenAI(
    model=openrouter_model,
    temperature=0.7,
    openai_api_key=openrouter_api_key,
    base_url="https://openrouter.ai/api/v1"
    
)


def get_llm(name: str):
    if name == openai_model:
        return LLM_OpenAI
    elif name == openrouter_model:
        return LLM_OpenRouter
    else:
        raise ValueError("未知的模型名稱")
