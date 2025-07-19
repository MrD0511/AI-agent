
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI


def get_gemini_model(model_name: str):
    gemini_flash_llm = ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key="AIzaSyAB6po8ng-NXb651W0dkQx1tXOtf3KyN0o",
        temperature=0.1
    )

    return gemini_flash_llm

def get_openrouter_model(model_name: str):
    openrouter_llm = ChatOpenAI(
        model=model_name,
        base_url="https://openrouter.ai/api/v1",
        api_key="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"
    )

    return openrouter_llm


openrouter_deepseek_model = get_openrouter_model("deepseek/deepseek-chat:free")