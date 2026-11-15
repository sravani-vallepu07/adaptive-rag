# 🧠 AdaptiveRag — LangGraph-Powered Agentic RAG Chatbot

An intelligent Retrieval-Augmented Generation (RAG) system that dynamically routes user queries to the most appropriate knowledge source using LangGraph-powered agentic workflows. Built with a FastAPI backend and a Streamlit frontend.

---

## ⚙️ How It Works

```
User Query → LangGraph Router
├── 📚 Index Route  → Searches uploaded documents (Qdrant Cloud)
├── 🧠 General Route → Answers using LLM knowledge (Groq: openai/gpt-oss-120b)
└── 🌐 Search Route  → Fetches real-time web results (Tavily Search API)
```

Each route includes:
- **Query Classification**: Decides whether the question needs documents, web search, or general knowledge.
- **Document Grading**: Evaluates whether retrieved documents are relevant before answering.
- **Query Rewriting**: Automatically rephrases queries if initial document retrieval fails.
- **Persistent Chat History**: Session-based memory stored in a local SQLite database (`chat_history.db`).

---

## 🛠️ Tech Stack

| Layer            | Technology                                |
|------------------|-------------------------------------------|
| Agentic Workflow | LangGraph                                 |
| LLM              | Groq (`openai/gpt-oss-120b` / configurable)|
| Vector Database  | Qdrant Cloud                              |
| Embeddings       | HuggingFace (`all-MiniLM-L6-v2`)          |
| Web Search       | Tavily Search API                         |
| Chat Memory      | SQLite (Local, Zero-Config)               |
| Backend API      | FastAPI & Uvicorn                         |
| Frontend UI      | Streamlit                                 |

---

## ✨ Features

- 🔀 **Adaptive Query Routing**: Routes questions across 3 intelligent paths.
- 📄 **PDF & TXT Document Indexing**: Upload documents via the UI and query them instantly.
- ✅ **Document Relevance Grading**: Verifies document context quality before generating answers.
- 🔁 **Automatic Query Rewriting**: Improves search queries dynamically when context is insufficient.
- 💬 **Persistent Chat Memory**: Stores conversation history per session locally in SQLite.
- 🌐 **Real-Time Web Search**: Integrates live Tavily web search for up-to-date queries.

---

## 📁 Project Structure

```
AdaptiveRag/
├── src/
│   ├── api/              # FastAPI routes (/rag/query, /rag/documents/upload, /rag/history)
│   ├── config/           # Settings, env loaders, and prompts.yaml
│   ├── core/             # Application logger
│   ├── db/               # SQLite database client & initialization
│   ├── llms/             # Groq LLM setup
│   ├── memory/           # Chat history manager (SQLite)
│   ├── models/           # Pydantic schemas (QueryRequest, GraphState)
│   └── rag/              # Core RAG pipeline
│       ├── graph_builder.py   # LangGraph workflow definition
│       ├── nodes.py           # Agent workflow nodes
│       ├── retriever_setup.py # Qdrant vector store & HuggingFace embeddings
│       └── document_upload.py # Document parsing & chunk indexing
├── streamlit_app/        # Streamlit frontend
│   ├── home.py           # Landing page & user session entry
│   └── pages/
│       └── chat.py       # Chat interface & document upload sidebar
├── .env.example          # Environment variable template
├── requirements.txt      # Python dependencies
└── README.md
```

---

## 🔧 Local Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/sravani-vallepu07/adaptive-rag.git
cd adaptive-rag
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
# Windows
copy .env.example .env

# Linux / macOS
cp .env.example .env
```

Open `.env` and fill in your API credentials:
```env
# LLM Provider (Free key from https://console.groq.com)
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b

# Web Search (Free key from https://app.tavily.com)
TAVILY_API_KEY=your_tavily_api_key

# Vector Database (Free cluster from https://cloud.qdrant.io)
QDRANT_URL=https://your-cluster-id.us-east-4-0.aws.cloud.qdrant.io:6333
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_DOCS_COLLECTION=documents

# Chat Memory Database (Local SQLite - no setup required)
SQLITE_DB_PATH=chat_history.db
```

### 5. Run the Backend (FastAPI)
```bash
python -m uvicorn src.main:app --reload --port 8000
```
- API Docs: `http://localhost:8000/docs`

### 6. Run the Frontend (Streamlit)
In a second terminal window (with `venv` activated):
```bash
python -m streamlit run streamlit_app/home.py
```
- Web UI: `http://localhost:8501`

---

## ☁️ Deployment

### Backend on Render (Free)
1. Push your repository to GitHub.
2. Go to [Render Dashboard](https://dashboard.render.com/) $\rightarrow$ **New Web Service** $\rightarrow$ Connect your repository.
3. Configure settings:
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
4. Add your `.env` variables under the **Environment Variables** tab.
5. Deploy to obtain your public backend URL (e.g. `https://your-backend.onrender.com`).

### Frontend on Streamlit Community Cloud (Free)
1. Go to [Streamlit Community Cloud](https://share.streamlit.io/) $\rightarrow$ **Create app**.
2. Connect your repository: `sravani-vallepu07/adaptive-rag`.
3. Set **Main file path** to `streamlit_app/home.py`.
4. In **Advanced Settings $\rightarrow$ Secrets**, provide your backend endpoint:
   ```toml
   API_BASE = "https://your-backend.onrender.com/rag"
   ```
5. Click **Deploy**!

---

## 👤 Author

**Sravani Vallepu**

- GitHub: [@sravani-vallepu07](https://github.com/sravani-vallepu07)
- Repository: [adaptive-rag](https://github.com/sravani-vallepu07/adaptive-rag)
