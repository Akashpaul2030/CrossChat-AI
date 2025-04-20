"""
Response formatting module for enhancing presentation of search results.
"""
from typing import List, Dict, Any, Optional
import re
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

from src.utils.config import DEFAULT_MODEL

# Enhanced formatting prompt with more detailed instructions
ENHANCED_FORMATTER_TEMPLATE = """
You are an expert at formatting search results into beautiful, well-structured, and informative responses.
Your task is to transform raw search results into a coherent, engaging, and visually appealing summary.

User Query: {query}

Raw Search Results:
{search_results}

Format these results into a comprehensive response that:

1. STRUCTURE:
   - Start with a clear, direct answer to the query when possible
   - Use appropriate headings and subheadings to organize information
   - Group related information together logically
   - Use bullet points or numbered lists for series of related items
   - Include a brief summary at the beginning for complex topics

2. CONTENT QUALITY:
   - Prioritize the most relevant and accurate information
   - Remove duplicate information
   - Reconcile any contradictory information from different sources
   - Fill in logical connections between facts when needed
   - Ensure comprehensive coverage of the topic

3. VISUAL FORMATTING:
   - Use **bold** for important terms or key concepts
   - Use *italics* for emphasis or to highlight secondary points
   - Use horizontal dividers (---) to separate major sections when appropriate
   - Use indentation for quotes or to highlight specific information
   - Maintain consistent formatting throughout

4. CITATIONS:
   - Cite sources inline using [Source: title] format
   - Include a "Sources" section at the end with numbered references
   - Link to original sources when URLs are available

5. LANGUAGE:
   - Use clear, concise, and engaging language
   - Maintain a helpful, informative tone
   - Adjust complexity based on the nature of the query
   - Ensure the response flows naturally and reads cohesively

Your formatted response:
"""

class ResponseFormatter:
    """
    A class to handle formatting of search results into well-structured responses.
    """
    def __init__(self, model: str = DEFAULT_MODEL, temperature: float = 0.2):
        """
        Initialize the response formatter.
        
        Args:
            model: The language model to use
            temperature: Temperature setting for response generation
        """
        self.prompt = ChatPromptTemplate.from_template(ENHANCED_FORMATTER_TEMPLATE)
        self.model = ChatOpenAI(model=model, temperature=temperature)
        self.chain = self.prompt | self.model | StrOutputParser()
    
    def format_search_results(self, query: str, search_results: List[Dict[str, Any]]) -> str:
        """
        Format search results into a well-structured response.
        
        Args:
            query: The user's query
            search_results: List of search result dictionaries
            
        Returns:
            Formatted response
        """
        if not search_results:
            return "I couldn't find any relevant information for your query."
        
        # Format raw search results into a string
        search_results_str = self._prepare_search_results_text(search_results)
        
        # Generate formatted response
        formatted_response = self.chain.invoke({
            "query": query,
            "search_results": search_results_str
        })
        
        # Post-process the response
        formatted_response = self._post_process_response(formatted_response)
        
        return formatted_response
    
    def _prepare_search_results_text(self, search_results: List[Dict[str, Any]]) -> str:
        """
        Prepare search results as text for the formatter.
        
        Args:
            search_results: List of search result dictionaries
            
        Returns:
            Formatted search results text
        """
        results_text = ""
        
        for i, result in enumerate(search_results):
            results_text += f"RESULT {i+1}:\n"
            results_text += f"Title: {result.get('title', 'No title')}\n"
            
            # Format content with proper spacing
            content = result.get('content', 'No content')
            # Clean up content by removing excessive whitespace
            content = re.sub(r'\s+', ' ', content).strip()
            results_text += f"Content: {content}\n"
            
            # Add URL if available
            url = result.get('url', '')
            if url:
                results_text += f"URL: {url}\n"
            
            # Add separator between results
            results_text += "\n" + "-" * 40 + "\n\n"
        
        return results_text
    
    def _post_process_response(self, response: str) -> str:
        """
        Post-process the formatted response for consistency and readability.
        
        Args:
            response: The raw formatted response
            
        Returns:
            Post-processed response
        """
        # Ensure consistent formatting for citations
        response = re.sub(r'\[Source: ([^\]]+)\]', r'[Source: \1]', response)
        
        # Ensure proper spacing around horizontal dividers
        response = re.sub(r'([^\n])---', r'\1\n\n---', response)
        response = re.sub(r'---([^\n])', r'---\n\n\1', response)
        
        # Ensure proper spacing around headings
        response = re.sub(r'([^\n])#{1,3} ', r'\1\n\n# ', response)
        response = re.sub(r'#{1,3} ([^\n]+)([^\n])', r'# \1\2\n', response)
        
        return response

class HighlightedResponseFormatter(ResponseFormatter):
    """
    Extended response formatter with additional highlighting capabilities.
    """
    def __init__(self, model: str = DEFAULT_MODEL, temperature: float = 0.2):
        """Initialize the highlighted response formatter."""
        super().__init__(model, temperature)
    
    def format_with_highlights(self, query: str, search_results: List[Dict[str, Any]], 
                              highlight_terms: Optional[List[str]] = None) -> str:
        """
        Format search results with highlighted key terms.
        
        Args:
            query: The user's query
            search_results: List of search result dictionaries
            highlight_terms: Optional list of terms to highlight
            
        Returns:
            Formatted response with highlights
        """
        # Get base formatted response
        formatted_response = self.format_search_results(query, search_results)
        
        # If no highlight terms provided, extract them from the query
        if not highlight_terms:
            highlight_terms = self._extract_key_terms(query)
        
        # Apply highlighting
        highlighted_response = self._apply_highlighting(formatted_response, highlight_terms)
        
        return highlighted_response
    
    def _extract_key_terms(self, query: str) -> List[str]:
        """
        Extract key terms from the query for highlighting.
        
        Args:
            query: The user's query
            
        Returns:
            List of key terms
        """
        # Remove common stop words
        stop_words = ['a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'with', 'about', 'is', 'are']
        
        # Split query into words and filter out stop words
        words = query.lower().split()
        key_terms = [word for word in words if word not in stop_words and len(word) > 2]
        
        return key_terms
    
    def _apply_highlighting(self, text: str, terms: List[str]) -> str:
        """
        Apply highlighting to key terms in the text.
        
        Args:
            text: The text to highlight
            terms: List of terms to highlight
            
        Returns:
            Text with highlights applied
        """
        # Skip terms that are already part of markdown formatting
        highlighted_text = text
        
        for term in terms:
            # Avoid highlighting terms that are already part of markdown formatting
            pattern = r'(?<!\*\*)(?<!\*)\b(' + re.escape(term) + r')\b(?!\*\*)(?!\*)'
            replacement = r'**\1**'
            highlighted_text = re.sub(pattern, replacement, highlighted_text, flags=re.IGNORECASE)
        
        return highlighted_text
