"""
Test script for the LangChain assistant with Windows compatibility.
"""
import os
import sys
import unittest
import platform
from dotenv import load_dotenv

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.enhanced_assistant import EnhancedLangChainAssistant
from src.components.formatter import ResponseFormatter, HighlightedResponseFormatter
from src.utils.path_utils import get_platform_path, ensure_dir_exists

# Load environment variables
load_dotenv()

class TestLangChainAssistant(unittest.TestCase):
    """Test cases for the LangChain assistant with Windows compatibility."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_session_id = "test_session"
        self.assistant = EnhancedLangChainAssistant(session_id=self.test_session_id)
        self.formatter = ResponseFormatter()
        
        # Ensure memory directory exists
        ensure_dir_exists("memory")
    
    def test_session_creation(self):
        """Test session creation and management."""
        # Test current session
        self.assertEqual(self.assistant.session_id, self.test_session_id)
        
        # Test creating a new session
        new_session_id = self.assistant.create_new_session()
        self.assertNotEqual(new_session_id, self.test_session_id)
        self.assertEqual(self.assistant.session_id, new_session_id)
        
        # Test switching back to original session
        success = self.assistant.switch_session(self.test_session_id)
        self.assertTrue(success)
        self.assertEqual(self.assistant.session_id, self.test_session_id)
    
    def test_formatter(self):
        """Test response formatter."""
        # Test basic formatting
        query = "What is Python?"
        search_results = [
            {
                "title": "Python (programming language) - Wikipedia",
                "content": "Python is a high-level, general-purpose programming language.",
                "url": "https://en.wikipedia.org/wiki/Python_(programming_language)"
            }
        ]
        
        formatted = self.formatter.format_search_results(query, search_results)
        self.assertIsNotNone(formatted)
        self.assertIsInstance(formatted, str)
        self.assertGreater(len(formatted), 0)
    
    def test_path_utils(self):
        """Test path utilities for Windows compatibility."""
        # Test platform-specific path conversion
        unix_path = "/home/user/file.txt"
        windows_path = "C:\\Users\\user\\file.txt"
        
        if platform.system() == "Windows":
            self.assertEqual(get_platform_path("/test/path"), "\\test\\path")
        else:
            self.assertEqual(get_platform_path("\\test\\path"), "/test/path")
    
    def tearDown(self):
        """Clean up after tests."""
        # Clean up test session
        memory_file = os.path.join("memory", f"{self.test_session_id}.json")
        if os.path.exists(memory_file):
            os.remove(memory_file)
        
        # Clean up any other test sessions
        if os.path.exists("memory"):
            for filename in os.listdir("memory"):
                if filename.startswith("test_"):
                    os.remove(os.path.join("memory", filename))

if __name__ == "__main__":
    unittest.main()
