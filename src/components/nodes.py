"""
Node implementations for the LangGraph conversation flow.
"""
from typing import Tuple, Dict, Any, List
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

from src.components.state import ConversationState
from src.utils.config import DEFAULT_MODEL, SEARCH_MODEL

# Prompt templates
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

SEARCH_RESULTS_FORMATTER_TEMPLATE = """
You are an AI assistant that formats search results into a coherent and readable summary.
Your task is to take the raw search results and create a well-structured, informative summary that will be used to generate a response to the user's query.

User Query: {query}

Raw Search Results:
{search_results}

Format these results into a coherent, well-organized summary that:
1. Highlights the most relevant information related to the query
2. Organizes information logically with appropriate headings and structure
3. Removes duplicate information
4. Cites sources appropriately
5. Is comprehensive yet concise

Your formatted summary:
"""

RESPONSE_GENERATION_TEMPLATE = """
You are a helpful AI assistant engaged in a conversation with a user.
Your goal is to provide informative, relevant, and helpful responses based on the conversation history and any search results provided.

Conversation History:
{chat_history}

User Query: {query}

{search_info}

Based on the above information, provide a comprehensive, accurate, and helpful response to the user's query.
Make your response conversational and engaging while being informative.
If you used search results, incorporate that information naturally and cite sources where appropriate.
"""

def create_query_analyzer():
    """Create a function to analyze if a query requires web search."""
    prompt = ChatPromptTemplate.from_template(QUERY_ANALYSIS_TEMPLATE)
    model = ChatOpenAI(model=SEARCH_MODEL, temperature=0)
    chain = prompt | model | StrOutputParser()
    
    def query_analyzer(state: ConversationState) -> ConversationState:
        """Analyze if the query requires web search."""
        # Extract chat history and format it
        chat_history = ""
        for msg in state.messages:
            if isinstance(msg, HumanMessage):
                chat_history += f"User: {msg.content}\n"
            elif isinstance(msg, AIMessage):
                chat_history += f"Assistant: {msg.content}\n"
        
        # Run the chain
        result = chain.invoke({
            "chat_history": chat_history,
            "query": state.user_query
        })
        
        # Update state
        state.requires_search = result.strip().upper() == "YES"
        return state
    
    return query_analyzer

def create_search_results_formatter():
    """Create a function to format search results."""
    prompt = ChatPromptTemplate.from_template(SEARCH_RESULTS_FORMATTER_TEMPLATE)
    model = ChatOpenAI(model=DEFAULT_MODEL, temperature=0)
    chain = prompt | model | StrOutputParser()
    
    def format_search_results(state: ConversationState) -> ConversationState:
        """Format search results into a coherent summary."""
        if not state.search_results:
            state.formatted_search_results = "No search results available."
            return state
        
        # Format raw search results into a string
        search_results_str = ""
        for i, result in enumerate(state.search_results):
            search_results_str += f"Result {i+1}:\n"
            search_results_str += f"Title: {result.get('title', 'No title')}\n"
            search_results_str += f"Content: {result.get('content', 'No content')}\n"
            search_results_str += f"URL: {result.get('url', 'No URL')}\n\n"
        
        # Run the chain
        formatted_results = chain.invoke({
            "query": state.user_query,
            "search_results": search_results_str
        })
        
        # Update state
        state.formatted_search_results = formatted_results
        return state
    
    return format_search_results

def create_response_generator():
    """Create a function to generate the final response."""
    prompt = ChatPromptTemplate.from_template(RESPONSE_GENERATION_TEMPLATE)
    model = ChatOpenAI(model=DEFAULT_MODEL, temperature=0.7)
    chain = prompt | model | StrOutputParser()
    
    def generate_response(state: ConversationState) -> ConversationState:
        """Generate the final response to the user."""
        # Extract chat history and format it
        chat_history = ""
        for msg in state.messages:
            if isinstance(msg, HumanMessage):
                chat_history += f"User: {msg.content}\n"
            elif isinstance(msg, AIMessage):
                chat_history += f"Assistant: {msg.content}\n"
        
        # Prepare search info
        search_info = ""
        if state.requires_search and state.formatted_search_results:
            search_info = f"Search Results:\n{state.formatted_search_results}"
        else:
            search_info = "No search was performed as it wasn't necessary for this query."
        
        # Run the chain
        response = chain.invoke({
            "chat_history": chat_history,
            "query": state.user_query,
            "search_info": search_info
        })
        
        # Update state
        state.response = response
        return state
    
    return generate_response
