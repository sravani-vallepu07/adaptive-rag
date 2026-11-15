import os
from dotenv import load_dotenv
# import API from .env


load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
QDRANT_DOCS_COLLECTION = os.getenv("QDRANT_DOCS_COLLECTION", "documents")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "chat_history.db")


