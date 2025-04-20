"""
FastAPI backend for the LangChain assistant.
"""
import os
import uuid
import logging
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import the enhanced assistant
from src.utils.enhanced_assistant import EnhancedLangChainAssistant

# Set up logging
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="LangChain Assistant API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active assistants for each session
active_assistants = {}

# Pydantic models for request/response
class MessageRequest(BaseModel):
    message: str
    session_id: str

class MessageResponse(BaseModel):
    response: str

class SessionResponse(BaseModel):
    session_id: str

class SessionListResponse(BaseModel):
    sessions: List[str]

class ConversationResponse(BaseModel):
    messages: List[Dict[str, Any]]

# Get or create assistant for a session
def get_assistant(session_id: str) -> EnhancedLangChainAssistant:
    if session_id not in active_assistants:
        assistant = EnhancedLangChainAssistant(session_id=session_id)
        active_assistants[session_id] = assistant
    return active_assistants[session_id]

# API routes
@app.post("/api/message", response_model=MessageResponse)
async def process_message(request: MessageRequest):
    try:
        assistant = get_assistant(request.session_id)
        response = assistant.process_message(request.message)
        
        # Check if this is the first message in the conversation
        conversation = assistant.get_conversation_history()
        if len(conversation) <= 2:  # Just the current exchange (user + assistant)
            # Generate a conversation name
            conversation_name = assistant.generate_conversation_name(request.message, response)
            assistant.set_conversation_name(conversation_name)
            
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@app.post("/api/session/new", response_model=SessionResponse)
async def create_session():
    try:
        session_id = str(uuid.uuid4())
        assistant = EnhancedLangChainAssistant(session_id=session_id)
        active_assistants[session_id] = assistant
        return {"session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating session: {str(e)}")

@app.get("/api/session/list", response_model=SessionListResponse)
async def list_sessions():
    try:
        # Create a temporary assistant to list available sessions
        temp_assistant = EnhancedLangChainAssistant()
        sessions = temp_assistant.list_available_sessions()
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing sessions: {str(e)}")

@app.get("/api/session/{session_id}", response_model=Dict[str, Any])
async def get_session_info(session_id: str):
    try:
        assistant = get_assistant(session_id)
        info = assistant.get_session_info()
        
        # Add conversation name if available
        if hasattr(assistant, 'memory') and assistant.memory is not None:
            name = assistant.memory.get_session_metadata("conversation_name")
            if name:
                info["conversation_name"] = name
                
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting session info: {str(e)}")

@app.get("/api/conversation/{session_id}", response_model=ConversationResponse)
async def get_conversation(session_id: str, limit: Optional[int] = None):
    try:
        assistant = get_assistant(session_id)
        messages = assistant.get_conversation_history(limit)
        return {"messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting conversation: {str(e)}")

@app.delete("/api/conversation/{session_id}", response_model=Dict[str, bool])
async def clear_conversation(session_id: str):
    """
    Clear a conversation's history.
    
    Args:
        session_id: The session ID of the conversation to clear
        
    Returns:
        Dictionary with success status
    """
    try:
        # Make sure we have an assistant for this session
        assistant = get_assistant(session_id)
        
        # Clear the conversation
        success = assistant.clear_conversation()
        
        # Remove from active assistants to ensure a fresh start next time
        if session_id in active_assistants:
            del active_assistants[session_id]
            
        return {"success": success}
    except Exception as e:
        logger.error(f"Error clearing conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error clearing conversation: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)  # Changed to port 8001