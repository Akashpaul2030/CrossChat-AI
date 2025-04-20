"""
Main graph implementation for the LangChain assistant using LangGraph.
"""
from typing import Dict, Any, List, Tuple, Annotated, TypedDict
from langchain_core.messages import HumanMessage, AIMessage

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from src.components.state import ConversationState
from src.components.nodes import (
    create_query_analyzer,
    create_search_results_formatter,
    create_response_generator
)

def create_conversation_graph():
    """
    Create the main conversation graph using LangGraph.
    
    Returns:
        A compiled LangGraph StateGraph
    """
    # Create the graph with the conversation state
    graph = StateGraph(ConversationState)
    
    # Create node functions
    query_analyzer = create_query_analyzer()
    search_results_formatter = create_search_results_formatter()
    response_generator = create_response_generator()
    
    # Add nodes to the graph
    graph.add_node("query_analyzer", query_analyzer)
    graph.add_node("search_results_formatter", search_results_formatter)
    graph.add_node("response_generator", response_generator)
    
    # Add a placeholder for the search_tool that will be added later
    # This prevents the "unknown node" error
    def placeholder_search(state):
        """Placeholder for search tool"""
        state.error = "Search tool not properly initialized"
        return state
    
    graph.add_node("search_tool", placeholder_search)
    
    # Define conditional edges
    def should_search(state: ConversationState) -> str:
        """Determine if search is required based on state."""
        if state.requires_search:
            return "search_tool"
        else:
            return "response_generator"
    
    # Add edges to the graph
    graph.add_edge("query_analyzer", should_search)
    graph.add_edge("search_tool", "search_results_formatter")
    graph.add_edge("search_results_formatter", "response_generator")
    graph.add_edge("response_generator", END)
    
    # Set the entry point
    graph.set_entry_point("query_analyzer")
    
    return graph

def process_user_input(
    graph,
    user_input: str,
    messages: List[Dict[str, Any]]
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Process user input through the conversation graph.
    
    Args:
        graph: The compiled conversation graph
        user_input: The user's input text
        messages: The current conversation messages
    
    Returns:
        Tuple of (assistant_response, updated_messages)
    """
    try:
        # Convert dict messages to LangChain message objects
        langchain_messages = []
        for msg in messages:
            if msg["role"] == "user":
                langchain_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                langchain_messages.append(AIMessage(content=msg["content"]))
        
        # Create initial state
        state = ConversationState(
            messages=langchain_messages,
            user_query=user_input
        )
        
        # Run the graph
        result = graph.invoke(state)
        
        # Extract the response
        assistant_response = result.response if hasattr(result, 'response') else "I couldn't process that request."
        
        # Update messages
        updated_messages = messages.copy()
        updated_messages.append({"role": "user", "content": user_input})
        updated_messages.append({"role": "assistant", "content": assistant_response})
        
        return assistant_response, updated_messages
        
    except Exception as e:
        # Handle errors and provide a fallback response
        import logging
        logging.error(f"Error in process_user_input: {str(e)}")
        
        # Create a fallback response
        fallback_response = "I apologize, but I encountered an error processing your request. The team has been notified."
        
        # Update messages with the fallback response
        updated_messages = messages.copy()
        updated_messages.append({"role": "user", "content": user_input})
        updated_messages.append({"role": "assistant", "content": fallback_response})
        
        return fallback_response, updated_messages