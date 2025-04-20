"""
Configuration utilities for the LangChain assistant.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# OpenAI API configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Tavily API configuration
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

# Default model configuration
DEFAULT_MODEL = "gpt-4o-mini"
SEARCH_MODEL = "gpt-3.5-turbo"

# Memory configuration
MEMORY_KEY = "chat_history"
MEMORY_RETURN_MESSAGES = 10  # Number of messages to return from memory

# Search configuration
SEARCH_TOP_K = 3  # Number of search results to return
