"""
Web search integration for the LangChain assistant.
"""
from typing import List, Dict, Any, Optional
from tavily import TavilyClient
import wikipedia
from langchain_core.tools import Tool

from src.components.state import ConversationState
from src.utils.config import TAVILY_API_KEY, SEARCH_TOP_K

class WebSearchTool:
    """
    A class to handle web search functionality using Tavily and Wikipedia.
    """
    def __init__(self, tavily_api_key: str = TAVILY_API_KEY):
        """
        Initialize the web search tool.
        
        Args:
            tavily_api_key: API key for Tavily search
        """
        self.tavily_client = TavilyClient(api_key=tavily_api_key)
        
    def tavily_search(self, query: str, max_results: int = SEARCH_TOP_K) -> List[Dict[str, Any]]:
        """
        Perform a web search using Tavily API.
        
        Args:
            query: The search query
            max_results: Maximum number of results to return
            
        Returns:
            List of search results
        """
        try:
            search_result = self.tavily_client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results
            )
            return search_result.get("results", [])
        except Exception as e:
            print(f"Tavily search error: {str(e)}")
            return []
    
    def wikipedia_search(self, query: str, max_results: int = 1) -> List[Dict[str, Any]]:
        """
        Perform a search using Wikipedia API.
        
        Args:
            query: The search query
            max_results: Maximum number of results to return
            
        Returns:
            List of search results
        """
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
            print(f"Wikipedia search error: {str(e)}")
            return []
    
    def combined_search(self, query: str) -> List[Dict[str, Any]]:
        """
        Perform a combined search using both Tavily and Wikipedia.
        
        Args:
            query: The search query
            
        Returns:
            Combined list of search results
        """
        # Get results from both sources
        tavily_results = self.tavily_search(query)
        wiki_results = self.wikipedia_search(query)
        
        # Combine results, prioritizing Tavily
        combined_results = tavily_results
        
        # Add Wikipedia results if they're not duplicates
        wiki_urls = [result.get("url") for result in wiki_results]
        tavily_urls = [result.get("url") for result in tavily_results]
        
        for wiki_result in wiki_results:
            if wiki_result.get("url") not in tavily_urls:
                combined_results.append(wiki_result)
        
        return combined_results

def create_search_tool():
    """
    Create a search tool node for the LangGraph.
    
    Returns:
        A function that can be used as a node in the graph
    """
    search_tool = WebSearchTool()
    
    def search_web(state: ConversationState) -> ConversationState:
        """
        Perform a web search based on the user query.
        
        Args:
            state: The current conversation state
            
        Returns:
            Updated conversation state with search results
        """
        try:
            # Perform the search
            search_results = search_tool.combined_search(state.user_query)
            
            # Update state with search results
            state.search_results = search_results
            
            # Handle case where no results were found
            if not search_results:
                state.error = "No search results found for the query."
                
            return state
        except Exception as e:
            state.error = f"Error during web search: {str(e)}"
            state.search_results = []
            return state
    
    return search_web
