import yaml
import os
from langchain_community.tools.tavily_search import TavilySearchResults
from src.models.state import GraphState
from src.llms.groq import llm
from src.rag.retriever_setup import retriever
from src.config.settings import TAVILY_API_KEY
from src.core.logger import get_logger

logger = get_logger(__name__)

# Load prompts
with open("src/config/prompts.yaml", "r") as f:
    prompts = yaml.safe_load(f)

# Tavily web search
os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY or ""
web_search_tool = TavilySearchResults(max_results=3)


def classify_query(state: GraphState) -> GraphState:
    query = state["query"]
    history = state.get("chat_history") or []
    history_context = ""
    if history:
        history_snippet = "\n".join([f"{m.get('role', 'user')}: {m.get('content', '')}" for m in history[-4:]])
        history_context = f"\nRecent conversation:\n{history_snippet}\n"

    prompt = prompts["classify_prompt"] + f"{history_context}\nQuestion: {query}"
    try:
        response = llm.invoke(prompt)
        route_raw = response.content.strip().lower()
    except Exception as e:
        logger.warning(f"Classify error: {e}, defaulting route.")
        route_raw = "index" if history else "general"

    if "index" in route_raw:
        route = "index"
    elif "search" in route_raw:
        route = "search"
    elif "general" in route_raw:
        route = "general"
    else:
        route = "index" if history else "general"

    logger.info(f"Classified as: {route}")
    return {**state, "route": route}


def retrieve(state: GraphState) -> GraphState:
    query = state["query"]
    history = state.get("chat_history") or []
    
    search_query = query
    # Contextualize short follow-ups using prior user messages
    if history and len(query.split()) < 8:
        prior_user_msgs = [m.get("content", "") for m in history if m.get("role") == "user"]
        if prior_user_msgs:
            search_query = f"{prior_user_msgs[-1]} {query}"

    docs = retriever.invoke(search_query)
    doc_texts = [doc.page_content for doc in docs]
    logger.info(f"Retrieved {len(doc_texts)} documents for query: '{search_query}'.")
    return {**state, "documents": doc_texts}


def grade_documents(state: GraphState) -> GraphState:
    query = state["query"]
    documents = state.get("documents", [])
    if not documents:
        return {**state, "documents": []}

    # If the user is asking an analytical/instructional question about the uploaded document,
    # keep all retrieved document chunks without discarding
    doc_keywords = ["resume", "cv", "document", "pdf", "file", "upload", "question", "questions", "answer", "answers", "summary", "summarize", "project", "experience", "skill", "from this", "about this"]
    query_lower = query.lower()
    if any(kw in query_lower for kw in doc_keywords):
        logger.info(f"Document instruction detected. Retaining all {len(documents)} retrieved documents.")
        return {**state, "documents": documents}

    # Otherwise do a single batch relevance check to prevent multiple rapid API calls & rate limits
    docs_summary = "\n---\n".join([f"Excerpt {i+1}: {d[:250]}" for i, d in enumerate(documents)])
    check_prompt = f"Question: {query}\n\nDocument Excerpts:\n{docs_summary}\n\nAre these document excerpts helpful to answer the question? Reply YES or NO."
    try:
        response = llm.invoke(check_prompt)
        if "yes" in response.content.strip().lower():
            return {**state, "documents": documents}
    except Exception as e:
        logger.warning(f"Grading check failed ({e}); defaulting to keeping documents.")
        return {**state, "documents": documents}

    logger.info("Documents graded as not relevant.")
    return {**state, "documents": []}


def rewrite_query(state: GraphState) -> GraphState:
    query = state["query"]
    prompt = prompts["rewrite_prompt"] + f"\n\nOriginal question: {query}"
    response = llm.invoke(prompt)
    new_query = response.content.strip()
    count = state.get("rewrite_count", 0) + 1
    logger.info(f"Rewritten query (attempt {count}): {new_query}")
    return {**state, "query": new_query, "rewrite_count": count}


def generate(state: GraphState) -> GraphState:
    query = state["query"]
    documents = state.get("documents", [])
    history = state.get("chat_history") or []
    context = "\n\n".join(documents) if documents else "No context available."
    if history:
        history_text = "\n".join([f"{m.get('role', 'user')}: {m.get('content', '')}" for m in history[-3:]])
        context = f"Recent conversation:\n{history_text}\n\nRelevant Documents:\n{context}"
    prompt = prompts["generate_prompt"].format(
        context=context,
        question=query
    )
    response = llm.invoke(prompt)
    return {**state, "answer": response.content.strip()}


def web_search(state: GraphState) -> GraphState:
    query = state["query"]
    results = web_search_tool.invoke(query)
    doc_texts = [r["content"] for r in results if "content" in r]
    logger.info(f"Web search returned {len(doc_texts)} results.")
    return {**state, "documents": doc_texts}


def general_llm(state: GraphState) -> GraphState:
    query = state["query"]
    history = state.get("chat_history") or []
    if history:
        history_text = "\n".join([f"{m.get('role', 'user')}: {m.get('content', '')}" for m in history[-3:]])
        prompt = f"Recent conversation:\n{history_text}\n\nUser request: {query}\n\nAnswer:"
        response = llm.invoke(prompt)
    else:
        response = llm.invoke(query)
    return {**state, "answer": response.content.strip()}


def route_query(state: GraphState) -> str:
    return state.get("route", "general")


def decide_to_rewrite(state: GraphState) -> str:
    documents = state.get("documents", [])
    rewrite_count = state.get("rewrite_count", 0)
    if not documents and rewrite_count < 2:
        return "rewrite"
    return "generate"