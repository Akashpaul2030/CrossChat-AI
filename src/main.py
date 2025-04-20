"""
Main entry point for the LangChain Assistant API.
"""
import os
import sys
import uvicorn
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('langchain_assistant.log')
    ]
)
logger = logging.getLogger('main')

# Add the project root directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the FastAPI app (we import here to ensure paths are set up correctly)
try:
    from src.api import app
except ImportError as e:
    logger.error(f"Error importing API: {str(e)}")
    print(f"Error importing API: {str(e)}")
    sys.exit(1)

def check_environment():
    """Check if required environment variables are set."""
    load_dotenv()
    
    openai_key = os.getenv("OPENAI_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")
    
    missing_keys = []
    if not openai_key or openai_key == "your_openai_api_key_here":
        missing_keys.append("OPENAI_API_KEY")
    
    if not tavily_key or tavily_key == "your_tavily_api_key_here":
        missing_keys.append("TAVILY_API_KEY")
    
    if missing_keys:
        logger.error(f"Missing or invalid environment variables: {', '.join(missing_keys)}")
        print(f"Error: Missing or invalid environment variables: {', '.join(missing_keys)}")
        print("Please set these variables in your .env file or environment.")
        return False
    
    return True

def main():
    """Main entry point for the application."""
    try:
        logger.info("Starting LangChain Assistant API")
        
        # Check environment variables
        if not check_environment():
            sys.exit(1)
        
        # Run the API server
        uvicorn.run(
            app, 
            host="127.0.0.1", 
            port=8000,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Error starting application: {str(e)}")
        print(f"Error starting application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()