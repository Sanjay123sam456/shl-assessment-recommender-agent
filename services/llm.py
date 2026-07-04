from langchain_openai import ChatOpenAI

from config import BASE_URL, MODEL_NAME, OPENROUTER_API_KEY


llm = ChatOpenAI(
    model=MODEL_NAME,
    api_key=OPENROUTER_API_KEY,
    base_url=BASE_URL,
    temperature=0,
)