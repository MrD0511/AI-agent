
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI


gemini_flash_llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite-001",
    google_api_key="AIzaSyAB6po8ng-NXb651W0dkQx1tXOtf3KyN0o"
)

openrouter_llm = ChatOpenAI(
    model="mistralai/mistral-7b-instruct:free",
    base_url="https://openrouter.ai/api/v1",
    api_key="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"
)
