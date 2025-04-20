"""
Integration of the search tool with the LangGraph conversation flow.
"""
from langgraph.graph import StateGraph, END

from src.components.state import ConversationState
from src.components.graph import create_conversation_graph
from src.components.search import create_search_tool
import logging

logger = logging.getLogger('integrated_graph')

def create_integrated_graph():
    """
    Create the conversation graph with integrated search functionality.
    
    Returns:
        A compiled LangGraph StateGraph with search capability
    """
    try:
        # Get the base conversation graph
        graph = create_conversation_graph()
        
        # Create the search tool
        search_tool_fn = create_search_tool()
        
        # Try to replace the search tool node
        try:
            # For newer versions of LangGraph
            graph.update_node("search_tool", search_tool_fn)
        except AttributeError:
            # For older versions of LangGraph
            # We need to recreate the node
            graph.add_node("search_tool", search_tool_fn)
        
        # Compile the graph
        compiled_graph = graph.compile()
        
        return compiled_graph
    except Exception as e:
        logger.error(f"Error creating integrated graph: {str(e)}")
        # Create a simple fallback graph
        fallback_graph = create_fallback_graph()
        return fallback_graph.compile()