from pydantic import BaseModel
from typing import List, Dict, Any


class QueryRequest(BaseModel):
    query: str
    session_id: str


class AgentResponse(BaseModel):
    answer: str
    tool_calls: List[str]
    data_quality_notes: List[str]
