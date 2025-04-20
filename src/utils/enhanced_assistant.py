"""
Simplified version of the LangChain assistant with web search capability.
"""
import os
import uuid
import logging
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tavily import TavilyClient
import wikipedia

from src.utils.persistent_memory import PersistentMemory
from src.utils.path_utils import ensure_dir_exists, get_platform_path
from src.utils.config import DEFAULT_MODEL, TAVILY_API_KEY, SEARCH_TOP_K

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('simple_assistant')

class SimpleTemplate:
    CHAT_TEMPLATE = """
    You are a helpful AI assistant engaged in a conversation with a user.
    Your goal is to provide informative, relevant, and helpful responses based on the conversation history.

    Conversation History:
    {chat_history}

    User Query: {query}

    {search_info}

    Based on the above information, provide a comprehensive, accurate, and helpful response to the user's query.
    Make your response conversational and engaging while being informative.
    If search results are provided, incorporate that information naturally and cite sources where appropriate.
    """

    QUERY_ANALYSIS_TEMPLATE = """
    You are an AI assistant analyzing user queries to determine if they require web search.
    Based on the conversation history and the current query, determine if you need to search the web for information.

    Conversation History:
    {chat_history}

    Current Query: {query}

    Do you need to search the web to properly answer this query? 
    Consider these factors:
    1. Is the query asking for recent information or events?
    2. Is the query about specific facts, statistics, or information you might not have?
    3. Is the query requesting information that might have changed since your training data?

    Respond with only "YES" if a web search is needed, or "NO" if you can answer without search.
    """

class WebSearch:
    def __init__(self, tavily_api_key: str = TAVILY_API_KEY):
        """Initialize the web search tool."""
        self.tavily_client = None
        if tavily_api_key:
            try:
                self.tavily_client = TavilyClient(api_key=tavily_api_key)
            except Exception as e:
                logger.error(f"Error initializing Tavily client: {str(e)}")
    
    def tavily_search(self, query: str, max_results: int = SEARCH_TOP_K) -> List[Dict[str, Any]]:
        """Perform a web search using Tavily API."""
        if not self.tavily_client:
            logger.warning("Tavily client not initialized")
            return []
            
        try:
            search_result = self.tavily_client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results
            )
            return search_result.get("results", [])
        except Exception as e:
            logger.error(f"Tavily search error: {str(e)}")
            return []
    
    def wikipedia_search(self, query: str, max_results: int = 1) -> List[Dict[str, Any]]:
        """Perform a search using Wikipedia API."""
        try:
            # Search for Wikipedia pages
            search_results = wikipedia.search(query, results=max_results)
            
            results = []
            for title in search_results:
                try:
                    # Get page content
                    page = wikipedia.page(title)
                    summary = wikipedia.summary(title, sentences=5)
                    
                    results.append({
                        "title": page.title,
                        "content": summary,
                        "url": page.url
                    })
                except (wikipedia.exceptions.DisambiguationError, 
                        wikipedia.exceptions.PageError) as e:
                    continue
                    
            return results
        except Exception as e:
            logger.error(f"Wikipedia search error: {str(e)}")
            return []
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Perform a combined search using available sources."""
        results = []
        
        # Try Tavily search first
        tavily_results = self.tavily_search(query)
        if tavily_results:
            results.extend(tavily_results)
        
        # If no Tavily results or Tavily is not available, try Wikipedia
        if not results:
            wiki_results = self.wikipedia_search(query)
            results.extend(wiki_results)
        
        return results

class EnhancedLangChainAssistant:
    """
    Simplified LangChain assistant with persistent memory and web search capability.
    """
    def __init__(self, session_id: Optional[str] = None, memory_dir: str = "memory"):
        """
        Initialize the assistant with persistent memory.
        
        Args:
            session_id: Optional session ID, generates a new one if not provided
            memory_dir: Directory to store memory files
        """
        try:
            # Set up session ID
            self.session_id = session_id or str(uuid.uuid4())
            
            # Convert memory_dir to platform-appropriate format
            self.memory_dir = get_platform_path(memory_dir)
            
            # Ensure memory directory exists
            if not ensure_dir_exists(self.memory_dir):
                fallback_dir = os.path.join(os.path.expanduser("~"), "langchain_memory")
                logger.warning(f"Failed to create directory {self.memory_dir}, using fallback: {fallback_dir}")
                ensure_dir_exists(fallback_dir)
                self.memory_dir = fallback_dir
            
            # Initialize persistent memory
            self.memory = PersistentMemory(
                storage_dir=self.memory_dir,
                session_id=self.session_id
            )
            
            # Load conversation history from persistent memory
            self.messages = self._convert_to_dict_format(self.memory.get_messages())
            
            # Set up language models
            self.chat_model = ChatOpenAI(model=DEFAULT_MODEL, temperature=0.7)
            self.analysis_model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
            
            # Create prompt templates
            self.chat_prompt = ChatPromptTemplate.from_template(SimpleTemplate.CHAT_TEMPLATE)
            self.analysis_prompt = ChatPromptTemplate.from_template(SimpleTemplate.QUERY_ANALYSIS_TEMPLATE)
            
            # Create chains
            self.chat_chain = self.chat_prompt | self.chat_model | StrOutputParser()
            self.analysis_chain = self.analysis_prompt | self.analysis_model | StrOutputParser()
            
            # Initialize web search
            self.web_search = WebSearch(tavily_api_key=TAVILY_API_KEY)
            
            logger.info(f"Assistant initialized with session ID: {self.session_id}")
            logger.info(f"Memory directory: {self.memory_dir}")
            
        except Exception as e:
            logger.error(f"Error initializing assistant: {str(e)}")
            # Minimal fallback initialization
            self.session_id = session_id or str(uuid.uuid4())
            self.memory_dir = memory_dir
            self.messages = []
            
            # Minimal model setup
            self.chat_model = ChatOpenAI(model=DEFAULT_MODEL, temperature=0.7)
            self.chat_prompt = ChatPromptTemplate.from_template(SimpleTemplate.CHAT_TEMPLATE)
            self.chat_chain = self.chat_prompt | self.chat_model | StrOutputParser()
            
            # Try to initialize memory
            try:
                self.memory = PersistentMemory(
                    storage_dir=self.memory_dir,
                    session_id=self.session_id
                )
            except Exception as mem_error:
                logger.error(f"Cannot initialize memory: {str(mem_error)}")
                self.memory = None
            
            # Try to initialize web search
            try:
                self.web_search = WebSearch(tavily_api_key=TAVILY_API_KEY)
            except Exception as search_error:
                logger.error(f"Cannot initialize web search: {str(search_error)}")
                self.web_search = None
                
            logger.warning("Initialized with minimal functionality due to errors")
    
    def _convert_to_dict_format(self, memory_messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert memory messages to the format expected by the processor.
        
        Args:
            memory_messages: Messages from persistent memory
            
        Returns:
            Messages in the format expected by the processor
        """
        try:
            return [
                {"role": msg["role"], "content": msg["content"]}
                for msg in memory_messages
            ]
        except Exception as e:
            logger.error(f"Error converting messages: {str(e)}")
            return []
    
    def _needs_web_search(self, query: str, chat_history: str) -> bool:
        """
        Determine if a query requires web search.
        
        Args:
            query: The user's query
            chat_history: Formatted chat history
            
        Returns:
            True if web search is needed, False otherwise
        """
        try:
            if not hasattr(self, 'analysis_chain'):
                # Default to searching for most queries if analysis chain isn't available
                return True
                
            result = self.analysis_chain.invoke({
                "chat_history": chat_history,
                "query": query
            })
            
            return result.strip().upper() == "YES"
        except Exception as e:
            logger.error(f"Error determining if search is needed: {str(e)}")
            # Default to not searching if there's an error
            return False
    
    def _format_search_results(self, results: List[Dict[str, Any]]) -> str:
        """
        Format search results into a readable string.
        
        Args:
            results: List of search result dictionaries
            
        Returns:
            Formatted search results string
        """
        if not results:
            return "No search results available."
            
        formatted = "Search Results:\n\n"
        
        for i, result in enumerate(results):
            formatted += f"Source {i+1}: {result.get('title', 'No title')}\n"
            formatted += f"Content: {result.get('content', 'No content')}\n"
            if 'url' in result:
                formatted += f"URL: {result.get('url')}\n"
            formatted += "\n"
            
        return formatted
    
    def process_message(self, user_input: str) -> str:
        """
        Process a user message and generate a response.
        
        Args:
            user_input: The user's input text
            
        Returns:
            The assistant's response
        """
        try:
            # Format chat history for prompt
            chat_history = ""
            for msg in self.messages:
                role = "User" if msg["role"] == "user" else "Assistant"
                chat_history += f"{role}: {msg['content']}\n\n"
            
            # Determine if web search is needed
            needs_search = self._needs_web_search(user_input, chat_history)
            
            # Perform web search if needed
            search_info = ""
            if needs_search and hasattr(self, 'web_search') and self.web_search is not None:
                logger.info(f"Performing web search for query: {user_input}")
                search_results = self.web_search.search(user_input)
                search_info = self._format_search_results(search_results)
            else:
                search_info = "No web search was performed as it wasn't necessary for this query."
            
            # Generate response
            response = self.chat_chain.invoke({
                "chat_history": chat_history,
                "query": user_input,
                "search_info": search_info
            })
            
            # Update conversation history
            self.messages.append({"role": "user", "content": user_input})
            self.messages.append({"role": "assistant", "content": response})
            
            # Update persistent memory if available
            if hasattr(self, 'memory') and self.memory is not None:
                try:
                    self.memory.add_user_message(user_input)
                    self.memory.add_assistant_message(response)
                except Exception as mem_error:
                    logger.error(f"Error saving to memory: {str(mem_error)}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            # Return a graceful error message to the user
            error_response = "I'm sorry, I encountered an issue processing your message. Please try again."
            
            # Try to save the error interaction to memory
            if hasattr(self, 'memory') and self.memory is not None:
                try:
                    self.memory.add_user_message(user_input)
                    self.memory.add_assistant_message(error_response)
                except Exception as mem_error:
                    logger.error(f"Could not save error message to memory: {str(mem_error)}")
                    
            return error_response
    
    def get_conversation_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get the current conversation history.
        
        Args:
            limit: Optional limit on number of most recent messages to return
            
        Returns:
            List of message dictionaries
        """
        try:
            if limit is not None:
                return self.messages[-limit:]
            return self.messages
        except Exception as e:
            logger.error(f"Error retrieving conversation history: {str(e)}")
            return []
    
    def clear_conversation(self) -> bool:
        """
        Clear the conversation history and memory.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Clear in-memory messages
            self.messages = []
            
            # Clear persistent memory if available
            if hasattr(self, 'memory') and self.memory is not None:
                try:
                    # Try to use clear method first
                    if hasattr(self.memory, 'clear'):
                        success = self.memory.clear()
                        if success:
                            logger.info(f"Successfully cleared conversation memory for session {self.session_id}")
                            return True
                    
                    # If that fails, try to delete the file directly
                    memory_file = getattr(self.memory, 'memory_file', None)
                    if memory_file and os.path.exists(memory_file):
                        try:
                            os.remove(memory_file)
                            logger.info(f"Deleted memory file {memory_file}")
                            return True
                        except Exception as e:
                            logger.error(f"Error deleting memory file: {str(e)}")
                    
                    # If we don't know the file path, try to reinitialize memory
                    self.memory = PersistentMemory(
                        storage_dir=self.memory_dir,
                        session_id=self.session_id
                    )
                    
                    logger.info("Reinitialized memory object")
                    return True
                    
                except Exception as mem_error:
                    logger.error(f"Error clearing memory: {str(mem_error)}")
                    # Continue even if memory clearing fails
            
            return True
        except Exception as e:
            logger.error(f"Error clearing conversation: {str(e)}")
            return False
    
    def get_session_info(self) -> Dict[str, Any]:
        """
        Get information about the current session.
        
        Returns:
            Dictionary with session information
        """
        try:
            if hasattr(self, 'memory') and self.memory is not None:
                return self.memory.get_session_info()
            return {
                "session_id": self.session_id,
                "message_count": len(self.messages),
                "in_memory_only": True
            }
        except Exception as e:
            logger.error(f"Error getting session info: {str(e)}")
            return {
                "session_id": self.session_id,
                "error": str(e)
            }
    
    def list_available_sessions(self) -> List[str]:
        """
        List all available session IDs.
        
        Returns:
            List of session IDs
        """
        try:
            if hasattr(self, 'memory') and self.memory is not None:
                return self.memory.list_available_sessions()
            return [self.session_id]
        except Exception as e:
            logger.error(f"Error listing available sessions: {str(e)}")
            return []
    
    def switch_session(self, session_id: str) -> bool:
        """
        Switch to a different conversation session.
        
        Args:
            session_id: The session ID to switch to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if session exists
            available_sessions = self.list_available_sessions()
            if session_id not in available_sessions:
                logger.warning(f"Session {session_id} not found in available sessions")
                return False
            
            # Update session ID
            self.session_id = session_id
            
            # Reinitialize memory with new session
            if hasattr(self, 'memory') and self.memory is not None:
                self.memory = PersistentMemory(
                    storage_dir=self.memory_dir,
                    session_id=self.session_id
                )
                
                # Load conversation history from persistent memory
                self.messages = self._convert_to_dict_format(self.memory.get_messages())
            
            logger.info(f"Successfully switched to session: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error switching session: {str(e)}")
            return False
    
    def create_new_session(self) -> str:
        """
        Create a new conversation session.
        
        Returns:
            The new session ID
        """
        try:
            # Generate new session ID
            new_session_id = str(uuid.uuid4())
            
            # Switch to new session
            self.session_id = new_session_id
            
            if hasattr(self, 'memory') and self.memory is not None:
                self.memory = PersistentMemory(
                    storage_dir=self.memory_dir,
                    session_id=self.session_id
                )
                
            self.messages = []
            
            logger.info(f"Created new session with ID: {new_session_id}")
            return new_session_id
            
        except Exception as e:
            logger.error(f"Error creating new session: {str(e)}")
            # Fall back to a simple UUID as the session ID
            fallback_id = str(uuid.uuid4())
            self.session_id = fallback_id
            self.messages = []
            return fallback_id