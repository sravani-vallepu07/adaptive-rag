from typing import List, Optional, Dict, Any
from typing_extensions import TypedDict


class GraphState(TypedDict):
    query: str
    session_id: str
    route: Optional[str]                  # index / general / search
    documents: Optional[List[str]]
    answer: Optional[str]
    rewrite_count: int                    # stops infinite rewrite loops
    chat_history: Optional[List[Dict[str, Any]]] # recent conversation messages