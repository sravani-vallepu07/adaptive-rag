from langchain_groq import ChatGroq
from src.config.settings import GROQ_API_KEY, GROQ_MODEL

llm = ChatGroq(
    model=GROQ_MODEL,
    temperature=0,
    api_key=GROQ_API_KEY
)