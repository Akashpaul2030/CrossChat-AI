"""
State definitions for the LangGraph conversation flow.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage

class ConversationState(BaseModel):
    """
    State model for the conversation flow.
    """
    # Messages in the current conversation
    messages: List[BaseMessage] = Field(default_factory=list)
    
    # Current user query
    user_query: str = ""
    
    # Whether the query requires web search
    requires_search: bool = False
    
    # Search results if any
    search_results: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Formatted search results for response generation
    formatted_search_results: Optional[str] = None
    
    # Final response to user
    response: Optional[str] = None
    
    # Error message if any
    error: Optional[str] = None
