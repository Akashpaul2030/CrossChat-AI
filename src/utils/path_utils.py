"""
Path utilities for Windows compatibility with enhanced error handling and logging.
"""
import os
import platform
import logging
import tempfile
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('path_utils')

def get_platform_path(path):
    """
    Convert path to the appropriate format for the current platform.
    
    Args:
        path: The path to convert
        
    Returns:
        Platform-appropriate path
    """
    try:
        if platform.system() == "Windows":
            # Convert forward slashes to backslashes for Windows
            return path.replace("/", "\\")
        else:
            # Use forward slashes for Unix-like systems
            return path.replace("\\", "/")
    except Exception as e:
        logger.error(f"Error converting path {path}: {str(e)}")
        return path  # Return original path if conversion fails

def ensure_dir_exists(directory):
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory: The directory path to check/create
        
    Returns:
        bool: True if directory exists or was created, False on failure
    """
    try:
        # Use pathlib for better cross-platform compatibility
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error creating directory {directory}: {str(e)}")
        return False

def get_memory_path(session_id, base_dir="memory"):
    """
    Get the platform-appropriate path for a memory file.
    
    Args:
        session_id: The session ID
        base_dir: The base directory for memory files
        
    Returns:
        Full path to the memory file
    """
    # Sanitize session_id to remove characters that might be invalid in filenames
    clean_session_id = "".join(c for c in session_id if c.isalnum() or c in "-_")
    
    try:
        # Ensure directory exists
        success = ensure_dir_exists(base_dir)
        if not success:
            # Fall back to temp directory if we can't create the specified directory
            base_dir = tempfile.gettempdir()
            logger.warning(f"Using temporary directory for memory files: {base_dir}")
            
        # Use pathlib for better path handling
        memory_file = Path(base_dir) / f"{clean_session_id}.json"
        return str(memory_file)
    except Exception as e:
        logger.error(f"Error getting memory path: {str(e)}")
        # Fallback to a simple path join
        return os.path.join(base_dir, f"{clean_session_id}.json")

def is_file_locked(filepath):
    """
    Check if a file is locked (Windows-specific issue).
    
    Args:
        filepath: Path to the file to check
        
    Returns:
        bool: True if file is locked, False otherwise
    """
    if not os.path.exists(filepath):
        return False
        
    try:
        # Try to open the file in append mode
        with open(filepath, 'a') as f:
            pass
        return False
    except PermissionError:
        return True
    except Exception as e:
        logger.error(f"Error checking if file {filepath} is locked: {str(e)}")
        return True  # Assume locked to be safe

def get_absolute_path(relative_path):
    """
    Convert a relative path to an absolute path based on the project root.
    
    Args:
        relative_path: The relative path from project root
        
    Returns:
        str: The absolute path
    """
    # Determine the project root (assuming this file is in src/utils)
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up two levels to get to the project root
        project_root = os.path.dirname(os.path.dirname(current_dir))
        # Join with the relative path
        abs_path = os.path.normpath(os.path.join(project_root, relative_path))
        return abs_path
    except Exception as e:
        logger.error(f"Error getting absolute path for {relative_path}: {str(e)}")
        return relative_path