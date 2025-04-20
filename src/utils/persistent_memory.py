"""
Enhanced memory persistence implementation for the LangChain assistant with Windows compatibility.
"""
import platform
import os
import json
import time
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from pathlib import Path

from src.utils.path_utils import (
    get_platform_path, 
    ensure_dir_exists, 
    get_memory_path,
    is_file_locked
)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('persistent_memory')

class PersistentMemory:
    """
    A class to handle persistent conversation memory across sessions with Windows compatibility.
    """
    def __init__(self, storage_dir: str = "memory", session_id: str = "default", max_retries: int = 3):
        """
        Initialize the persistent memory.
        
        Args:
            storage_dir: Directory to store memory files
            session_id: Unique identifier for the conversation session
            max_retries: Maximum number of retries for file operations
        """
        self.storage_dir = storage_dir
        self.session_id = session_id
        self.max_retries = max_retries
        self.memory_file = get_memory_path(session_id, storage_dir)
        
        # Create storage directory if it doesn't exist
        if not ensure_dir_exists(storage_dir):
            fallback_dir = os.path.join(os.path.expanduser("~"), "langchain_memory")
            logger.warning(f"Failed to create directory {storage_dir}, using fallback: {fallback_dir}")
            ensure_dir_exists(fallback_dir)
            self.storage_dir = fallback_dir
            self.memory_file = get_memory_path(session_id, fallback_dir)
        
        # Initialize or load existing memory
        self.messages = self._load_memory()
    
    def _load_memory(self) -> List[Dict[str, Any]]:
        """
        Load memory from persistent storage with retry mechanism.
        
        Returns:
            List of message dictionaries
        """
        if not os.path.exists(self.memory_file):
            return []
            
        for attempt in range(self.max_retries):
            try:
                # Check if file is locked (Windows issue)
                if is_file_locked(self.memory_file):
                    logger.warning(f"Memory file {self.memory_file} is locked. Retry {attempt+1}/{self.max_retries}")
                    time.sleep(0.5)  # Wait before retrying
                    continue
                    
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f"Successfully loaded memory from {self.memory_file}")
                    return data
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error loading memory: {str(e)}")
                # If the file is empty or corrupted, create a backup and return empty list
                self._create_backup()
                return []
            except Exception as e:
                logger.error(f"Error loading memory (attempt {attempt+1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(0.5)  # Wait before retrying
                else:
                    # If all retries fail, create a backup of the potentially corrupted file
                    self._create_backup()
                    return []
        
        return []
    
    def _create_backup(self):
        """Create a backup of the memory file if it exists."""
        if os.path.exists(self.memory_file) and os.path.getsize(self.memory_file) > 0:
            try:
                backup_file = f"{self.memory_file}.bak.{int(time.time())}"
                with open(self.memory_file, 'rb') as src, open(backup_file, 'wb') as dst:
                    dst.write(src.read())
                logger.info(f"Created backup of memory file at {backup_file}")
            except Exception as e:
                logger.error(f"Failed to create backup of memory file: {str(e)}")
    
    def _save_memory(self) -> bool:
        """
        Save memory to persistent storage with retry mechanism.
        
        Returns:
            bool: True if successful, False otherwise
        """
        for attempt in range(self.max_retries):
            try:
                # Ensure directory exists before saving
                ensure_dir_exists(os.path.dirname(self.memory_file))
                
                # Check if file is locked (Windows issue)
                if os.path.exists(self.memory_file) and is_file_locked(self.memory_file):
                    logger.warning(f"Memory file {self.memory_file} is locked. Retry {attempt+1}/{self.max_retries}")
                    time.sleep(0.5)  # Wait before retrying
                    continue
                
                # Save to a temporary file first to prevent corruption
                temp_file = f"{self.memory_file}.tmp"
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(self.messages, f, indent=2, ensure_ascii=False)
                
                # On Windows, we need to remove the target file before renaming
                if platform.system() == "Windows" and os.path.exists(self.memory_file):
                    try:
                        os.remove(self.memory_file)
                    except Exception as e:
                        logger.warning(f"Could not remove existing file before rename: {str(e)}")
                
                # Rename temp file to actual file
                os.replace(temp_file, self.memory_file)
                logger.info(f"Successfully saved memory to {self.memory_file}")
                return True
                
            except Exception as e:
                logger.error(f"Error saving memory (attempt {attempt+1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(0.5)  # Wait before retrying
        
        logger.error(f"Failed to save memory after {self.max_retries} attempts")
        return False
    
    def add_message(self, role: str, content: str) -> bool:
        """
        Add a message to memory.
        
        Args:
            role: The role of the message sender ('user' or 'assistant')
            content: The message content
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Create message with timestamp
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add to memory
        self.messages.append(message)
        
        # Save to persistent storage
        return self._save_memory()
    
    def add_user_message(self, content: str) -> bool:
        """
        Add a user message to memory.
        
        Args:
            content: The user message content
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self.add_message("user", content)
    
    def add_assistant_message(self, content: str) -> bool:
        """
        Add an assistant message to memory.
        
        Args:
            content: The assistant message content
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self.add_message("assistant", content)
    
    def get_messages(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get messages from memory.
        
        Args:
            limit: Optional limit on number of most recent messages to return
            
        Returns:
            List of message dictionaries
        """
        if limit is not None:
            return self.messages[-limit:]
        return self.messages
    
    def get_langchain_messages(self, limit: Optional[int] = None) -> List[BaseMessage]:
        """
        Get messages in LangChain format.
        
        Args:
            limit: Optional limit on number of most recent messages to return
            
        Returns:
            List of LangChain message objects
        """
        messages = self.get_messages(limit)
        langchain_messages = []
        
        for msg in messages:
            if msg["role"] == "user":
                langchain_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                langchain_messages.append(AIMessage(content=msg["content"]))
        
        return langchain_messages
    
    def clear(self) -> bool:
        """
        Clear all messages from memory.
        
        Returns:
            bool: True if successful, False otherwise
        """
        self.messages = []
        return self._save_memory()
    
    def get_session_info(self) -> Dict[str, Any]:
        """
        Get information about the current session.
        
        Returns:
            Dictionary with session information
        """
        if not self.messages:
            return {
                "session_id": self.session_id,
                "memory_file": self.memory_file,
                "message_count": 0,
                "start_time": None,
                "last_update": None
            }
        
        return {
            "session_id": self.session_id,
            "memory_file": self.memory_file,
            "message_count": len(self.messages),
            "start_time": self.messages[0].get("timestamp"),
            "last_update": self.messages[-1].get("timestamp")
        }
    
    def list_available_sessions(self) -> List[str]:
        """
        List all available session IDs.
        
        Returns:
            List of session IDs
        """
        sessions = []
        try:
            if os.path.exists(self.storage_dir):
                for filename in os.listdir(self.storage_dir):
                    if filename.endswith(".json") and not filename.endswith(".tmp") and not filename.endswith(".bak"):
                        # Remove .json extension to get session ID
                        session_id = filename[:-5]
                        sessions.append(session_id)
        except Exception as e:
            logger.error(f"Error listing available sessions: {str(e)}")
        
        return sessions