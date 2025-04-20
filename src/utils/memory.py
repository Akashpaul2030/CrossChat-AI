"""
Memory utilities for the LangChain assistant.
"""
from typing import List, Dict, Any
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

class MemorySaver:
    """
    A class to handle conversation memory persistence.
    """
    def __init__(self, memory_key: str = "chat_history", return_messages: int = 10):
        """
        Initialize the memory saver.
        
        Args:
            memory_key: The key to use for storing chat history
            return_messages: Number of most recent messages to return
        """
        self.memory = ConversationBufferMemory(
            memory_key=memory_key,
            return_messages=return_messages
        )
        
    def add_user_message(self, message: str) -> None:
        """
        Add a user message to memory.
        
        Args:
            message: The user message to add
        """
        self.memory.chat_memory.add_user_message(message)
        
    def add_ai_message(self, message: str) -> None:
        """
        Add an AI message to memory.
        
        Args:
            message: The AI message to add
        """
        self.memory.chat_memory.add_ai_message(message)
        
    def get_messages(self) -> List[BaseMessage]:
        """
        Get all messages from memory.
        
        Returns:
            List of messages
        """
        return self.memory.chat_memory.messages
    
    def get_memory_variables(self) -> Dict[str, Any]:
        """
        Get memory variables for LLM context.
        
        Returns:
            Dictionary of memory variables
        """
        return self.memory.load_memory_variables({})
    
    def clear(self) -> None:
        """
        Clear all messages from memory.
        """
        self.memory.chat_memory.clear()
