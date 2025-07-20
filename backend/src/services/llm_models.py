
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

# Load environment variables securely
load_dotenv('.env.local')
load_dotenv()


def get_gemini_model(model_name: str):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables")
    
    gemini_flash_llm = ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=api_key,
        temperature=0.1
    )

    return gemini_flash_llm

def get_openrouter_model(model_name: str):
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not found in environment variables")
    
    openrouter_llm = ChatOpenAI(
        model=model_name,
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key
    )

    return openrouter_llm


openrouter_deepseek_model = get_openrouter_model("deepseek/deepseek-chat:free")