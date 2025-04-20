# CrossChat-AI: Cross-Platform LangChain Assistant

A powerful AI chat assistant that works seamlessly on both Windows and Linux

This project implements a comprehensive AI assistant using LangChain with the following features:

- Contextual understanding of user queries
- Real-time information retrieval via web search (Tavily API)
- Memory persistence across sessions
- Beautifully formatted responses
- React-based user interface
- **Cross-platform compatibility** (Windows and Linux)

## About CrossChat-AI

CrossChat-AI is designed to provide a seamless AI assistant experience regardless of your operating system. Built on LangChain and integrated with web search capabilities, it delivers intelligent responses while maintaining conversation context across multiple sessions.

Key aspects that set CrossChat-AI apart:

1. **True Cross-Platform Design**: Built from the ground up with compatibility in mind
2. **Intelligent Web Search**: Automatically determines when to search the web for current information
3. **Persistent Memory**: Maintains conversation history across sessions and system restarts
4. **Modern React UI**: Clean, responsive interface that works well on all devices
5. **Easy Installation**: Platform-specific scripts make setup simple on any system

## Project Structure

```
CrossChat-AI/
├── src/
│   ├── components/         # Core components
│   │   ├── formatter.py    # Response formatting
│   │   ├── graph.py        # LangGraph implementation
│   │   ├── integrated_graph.py # Graph with search
│   │   ├── nodes.py        # Node implementations
│   │   ├── search.py       # Web search functionality
│   │   └── state.py        # State definitions
│   ├── utils/              # Utility modules
│   │   ├── config.py       # Configuration
│   │   ├── enhanced_assistant.py # Main assistant class
│   │   ├── memory.py       # Memory utilities
│   │   ├── path_utils.py   # Cross-platform path utilities
│   │   └── persistent_memory.py # Persistent memory
│   ├── frontend/           # React frontend
│   │   ├── public/         # Static assets
│   │   └── src/            # React components
│   │       ├── components/ # UI components
│   │       ├── App.js      # Main application
│   │       └── index.js    # Entry point
│   ├── api.py              # FastAPI backend
│   └── main.py             # Entry point for the application
├── tests/                  # Test cases
│   └── test_assistant.py   # Unit tests
├── memory/                 # Conversation storage
├── requirements.txt        # Python dependencies
├── run.bat                 # Windows run script
├── install.bat             # Windows installation script
└── test.bat                # Windows test script
```

## Setup Instructions

### Prerequisites

- Python 3.10+
- Node.js 14+
- OpenAI API key
- Tavily API key

### Windows Installation

1. Clone the repository:
```
git clone <repository-url>
cd CrossChat-AI
```

2. Create a virtual environment (recommended):
```
python -m venv venv
venv\Scripts\activate
```

3. Run the installation batch file:
```
install.bat
```

4. Create a `.env` file in the project root with your API keys:
```
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

### Linux Installation

1. Clone the repository:
```
git clone <repository-url>
cd CrossChat-AI
```

2. Create a virtual environment (recommended):
```
python -m venv venv
source venv/bin/activate
```

3. Make the installation and run scripts executable:
```
chmod +x run.sh
chmod +x install.sh
```

4. Run the installation script:
```
./install.sh
```

5. Create a `.env` file in the project root with your API keys:
```
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

### Running the Application on Windows

Run the application using the provided batch file:
```
run.bat
```

This will start both the backend API server and the frontend development server.

### Running the Application on Linux

Run the application using the provided shell script:
```
./run.sh
```

For both platforms:
- Backend API: http://localhost:8001
- Frontend: http://localhost:3000

If you encounter port conflicts, you can manually start the servers:

```
# Start backend
python -m src.api

# Start frontend (in another terminal)
cd src/frontend    # Linux
cd src\frontend    # Windows
npm start
```

### Testing

Run the unit tests using the provided batch file:
```
test.bat
```

## API Endpoints

- `POST /api/message`: Process a user message
- `POST /api/session/new`: Create a new conversation session
- `GET /api/session/list`: List all available sessions
- `GET /api/session/{session_id}`: Get session information
- `GET /api/conversation/{session_id}`: Get conversation history
- `DELETE /api/conversation/{session_id}`: Clear conversation history

## Cross-Platform Compatibility

This project includes several enhancements for cross-platform compatibility:

### Windows-Specific Features
1. **Path Utilities**: Proper handling of backslashes in file paths
2. **Batch Files**: Windows-specific batch files for installation, running, and testing
3. **File Locking**: Special handling for Windows file locking during read/write operations
4. **Process Management**: Windows-specific process handling in batch scripts

### Linux-Specific Features
1. **Path Utilities**: Proper handling of forward slashes in file paths
2. **Shell Scripts**: Linux-compatible shell scripts for installation, running, and testing
3. **Process Management**: Proper handling of background processes and cleanup on exit
4. **File Permissions**: Appropriate file permission handling

### Common Improvements
1. **Memory Persistence**: Cross-platform compatible file operations
2. **Error Handling**: Robust error handling that works across operating systems
3. **Fallback Mechanisms**: Graceful degradation when features aren't available
4. **Platform Detection**: Automatic detection of operating system for appropriate behavior

## Troubleshooting

### Common Issues and Solutions (Windows)

1. **Port Already In Use**:
   ```
   ERROR: [Errno 10048] error while attempting to bind on address ('0.0.0.0', 8000): only one usage of each socket address (protocol/network address/port) is normally permitted
   ```
   
   **Solution**: 
   - Check for processes using the port: `netstat -ano | findstr :8000`
   - Kill the process: `taskkill /F /PID <PID>`
   - Or change the port number in `src/api.py` and `src/main.py`

2. **Memory File Access Issues**:
   
   **Solution**:
   - Run Command Prompt as Administrator
   - Ensure your antivirus isn't blocking access to the memory directory

3. **Windows Path Issues**:
   
   **Solution**:
   - Make sure `path_utils.py` is properly handling Windows backslashes
   - Use the provided path utility functions for all file operations

### Common Issues and Solutions (Linux)

1. **Port Already In Use**:
   ```
   ERROR: [Errno 98] Address already in use
   ```
   
   **Solution**: 
   - Check for processes using the port: `sudo lsof -i :8000`
   - Kill the process: `kill -9 <PID>`
   - Or change the port number in `src/api.py` and `src/main.py`

2. **Permission Issues**:
   
   **Solution**:
   - Ensure scripts have proper execute permissions: `chmod +x *.sh`
   - Check file permissions on the memory directory: `chmod -R 755 memory/`

3. **Background Process Management**:
   
   **Solution**:
   - If background processes remain after stopping the app, find and kill them:
     ```
     ps aux | grep python
     kill -9 <PID>
     ```

### Common Issues for Both Platforms

1. **Frontend/Backend Connection Issues**:
   
   **Solution**:
   - Ensure backend is running and accessible at http://localhost:8001
   - Check that all API URLs in the frontend code use the correct port
   - Verify CORS settings in `src/api.py` match your frontend URL

2. **Creating New Conversation Not Working**:
   
   **Solution**:
   - Check browser console for errors
   - Ensure API endpoints for session creation are correctly implemented
   - Verify that frontend is properly updating state with new session ID

3. **API Key Issues**:
   
   **Solution**:
   - Make sure your `.env` file exists and contains valid API keys
   - Check that API keys don't have extra spaces or quotes
   - Verify your API keys haven't expired or reached usage limits

## Implementation Details

### Cross-Platform File Handling

The application uses a dedicated `path_utils.py` module to handle platform-specific path issues:

```python
def get_platform_path(path):
    if platform.system() == "Windows":
        # Convert forward slashes to backslashes for Windows
        return path.replace("/", "\\")
    else:
        # Use forward slashes for Unix-like systems
        return path.replace("\\", "/")
```

This ensures consistent file operations regardless of operating system.

### Memory Persistence

Conversations are persisted to disk using a file-based storage system with robust error handling and retry mechanisms:

- Each conversation is stored as a JSON file with a unique session ID
- The system implements retry logic to handle file locking issues on Windows
- Temporary files are used to prevent corruption during writes
- The system creates automatic backups if file corruption is detected
- Fallback directories are used if the primary memory directory is inaccessible

### Web Search

The application uses both Tavily API and Wikipedia to search for information:

1. Query analysis determines if search is needed
2. Tavily is used for primary search (requires API key)
3. Wikipedia serves as a fallback search option
4. Search results are formatted and incorporated into responses

### React Frontend

The frontend provides a clean, intuitive interface for interacting with the assistant, featuring:
- Real-time chat interface
- Session management for multiple conversations
- Markdown rendering for formatted responses
- Responsive design for all device sizes

### Error Handling and Fallbacks

The system implements robust error handling at multiple levels:

- Path-related errors are handled with fallback paths
- Memory persistence errors fall back to in-memory operation
- Web search errors fall back to local information retrieval
- Frontend connectivity issues provide clear error messages
- All operations include proper logging for debugging

## Future Improvements

CrossChat-AI is constantly evolving. Planned improvements include:

- Advanced LangGraph implementation for more complex reasoning chains
- Additional search sources beyond Tavily and Wikipedia
- Caching mechanisms for improved performance
- Enhanced conversation analysis for better search decisions
- Document upload and analysis capabilities
- Docker containerization for even better cross-platform support
- WebSocket implementation for real-time updates
- Authentication and multi-user support

## Contributing

Contributions to CrossChat-AI are welcome! Please feel free to submit a Pull Request.



## Acknowledgments

- Thanks to the LangChain team for the excellent framework
- Tavily for providing the search API
- All contributors who have helped make CrossChat-AI better