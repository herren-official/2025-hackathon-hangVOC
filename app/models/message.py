from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class SlackMessage(BaseModel):
    user: Optional[str] = None
    text: str
    ts: str
    channel: Optional[str] = None
    thread_ts: Optional[str] = None
    
class SearchQuery(BaseModel):
    question: str
    top_k: Optional[int] = 10
    
class SearchResult(BaseModel):
    answer: str
    sources: List[dict]
    query: str